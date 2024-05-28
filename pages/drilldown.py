# Imports
import dash
from collections import namedtuple
import pandss as pdss
import pandas as pd
import numpy as np
import yaml
from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page, State
import plotly.express as px
from utils.query_data import df, scen_aliases


#import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from utils.tools import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums,
                   wyt_list, convert_wyt_nums, cfs_taf,list_files)



register_page(
    __name__,
    name='Drilldown',
    top_nav=True,
    path='/drilldown'
)

cs3_icon_path = 'assets/cs3_icon_draft.png'
date_map = pd.read_csv('constants/date_map.csv', index_col=0, parse_dates=True)
with open('constants/vars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)

bparts = []
aliases = []


for var in var_dict:
    bparts.append(var)
    aliases.append(var_dict[var]['alias'])


# DataFrames for the summary tables
df_tbl = make_summary_df(scen_aliases,df,var_dict)
df_tbl_res = make_ressum_df(scen_aliases,df,var_dict)


# Layout Starts Here
def layout():
    layout = dbc.Container([
    dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Results Dashboard"),
    dcc.Markdown("### A General dashboard for reviewing CalSim 3 Results"),

    dbc.Row([
        dbc.Col(
            [
                "Select B-Part: ",
                dcc.Dropdown(bparts, id='b-part',value="C_CAA003",
                            style={'width': '100%'}
                            ),
                "Or search by alias: ",
                dcc.Dropdown(options=aliases, id='alias', value="Total Banks Exports",
                            style={'width': '100%'}
                            )
            ],
            width=6
        ),
    ]),

        html.Br(),
        html.Div(id='my-output'),
        dcc.Markdown("**Timeseries**"),
        dcc.Graph(id='timeseries-plot'),
                
        dbc.Row([
            dbc.Col([dcc.Markdown("**Monthly Exceedance**"),
                    dcc.Checklist(options = month_list,
                        value = month_list,
                        inline=True,
                        id = 'monthchecklist-exc',
                        inputStyle={"margin-right": "5px","margin-left": "5px"}),
                    
                    dcc.Graph(id='exceedance-plot')
                    ],
                    align="center"
                    ),
            
            dbc.Col([dcc.Markdown("**Monthly Average**"),
                    dcc.Checklist(options = wyt_list,
                        value = wyt_list,
                        inline=True,
                        id = 'wytchecklist-bar',
                        inputStyle={"margin-right": "5px","margin-left": "30px"},
                        ),
                        dcc.Graph(id='bar-plot'),                 
                    ]),
        ]),

        dbc.Row([
            dbc.Col([dcc.Markdown("**Annual Exceedance**"),
                    dcc.Dropdown(
                            options=['Calendar Year','Water Year'], 
                            id='yearwindow',
                            style={'width': '50%'},
                            value = "Water Year"
                            ),
                    dcc.Graph(id='exceedance-plot-annual')
                    ]),

            dbc.Col([dcc.Markdown("**Annual Average**"),
                    dcc.Dropdown(
                            options=['Calendar Year','Water Year'], 
                            id='yearwindow-repeater',
                            style={'width': '50%'},
                            value = "Water Year",
                            disabled=True
                            ),
                    dcc.Graph(id='bar-plot-annual'),
                    ]),


        ]),

        dcc.Markdown("#### Table Controls"),
        dcc.Markdown("End-of-Month (for Reservoirs)"),

        dcc.RadioItems(
        options = month_list,
        value = 'Sep',
        inline=True, id = 'monthradio'
        ),

        dcc.Markdown("Flow Average Period"),
        dcc.Checklist(
            options = month_list, value = month_list, inline=True,
            id = 'monthchecklist'
        ),
        html.Div(id='output-container-month-checklist'),

        dcc.RangeSlider(1922, 2021, 1, value=[1922, 2021],
                        marks={i: '{}'.format(i) for i in range(1922,2021,5)},
                        pushable=False,
                        id='slider-yr-range'),
        html.Div(id='output-container-range-slider'),

        #html.Button('Load', id='btn-refresh-tbl', n_clicks=0),
        dcc.Markdown("**Reservoir Summary Tables (Single Month)**"),
        dash_table.DataTable(
            id='sum_tbl_res',
            columns=[{"name": i, "id": i} 
                    for i in df_tbl.columns],
            data=df_tbl_res.to_dict(orient='records'),
            style_header={
                    'backgroundColor': 'rgb(200, 200, 200)',
                    'fontWeight': 'bold'
            },
            style_cell={
            'width': '{}%'.format(len(df_tbl.columns)),
            'textOverflow': 'ellipsis',
            'overflow': 'hidden'
            },
        ),
        dcc.Markdown("**Flow Summary Tables (Average Annual)**"),
        dash_table.DataTable(
            id='sum_tbl',
            columns=[{"name": i, "id": i} 
                    for i in df_tbl.columns],
            data=df_tbl.to_dict(orient='records'),
            style_header={
                    'backgroundColor': 'rgb(200, 200, 200)',
                    'fontWeight': 'bold'
            },
            style_cell={
            'width': '{}%'.format(len(df_tbl.columns)),
            'textOverflow': 'ellipsis',
            'overflow': 'hidden'
            },
        )
    ],
    fluid=False
    )
    return layout


# CALLBACKS Start Here

# Return B Part based on alias search
@callback(
    Output(component_id='b-part', component_property='value'),
    Input(component_id='alias', component_property='value')        
)
def update_b_part(alias):
    i=aliases.index(str(alias))
    b = bparts[i]
    return b

# Timeseries Plot
@callback(
    Output(component_id='timeseries-plot', component_property='figure'),
    Input(component_id='b-part', component_property='value')
)
def update_timeseries(b_part):
    fig = px.line(df, x=df.index, y=b_part, color='Scenario')
    #print(df)
    return fig

# Exceedance Plot
@callback(
    Output(component_id='exceedance-plot', component_property='figure'),
    Input(component_id='b-part', component_property='value'),
    Input(component_id='monthchecklist-exc', component_property='value')
)
def update_exceedance(b_part,monthchecklist):
    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    for scenario in scen_aliases:
        df1 = df0.loc[df0['Scenario']==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1
    fig = px.line(df2)
    return fig

# Annual Exceedance Plot
@callback(
    Output(component_id='exceedance-plot-annual', component_property='figure'),
    Input(component_id='b-part', component_property='value'),
    Input(component_id='monthchecklist-exc', component_property='value'),
    Input(component_id='yearwindow', component_property='value')
)
def update_exceedance(b_part,monthchecklist,yearwindow):
    if yearwindow=="Calendar Year":
        yw='icy'
    else:
        yw='iwy'

    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    cfs_taf(df0,var_dict)
    df0 = df0.groupby(['Scenario',yw]).sum()
    for scenario in scen_aliases:
        df1 = df0.loc[df0.index.get_level_values(0)==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1
    fig = px.line(df2)
    return fig

# Monthly Bar Plot
@callback(
    Output(component_id='bar-plot', component_property='figure'),
    Input(component_id='b-part', component_property='value'),
    Input(component_id='wytchecklist-bar', component_property='value')
)
def update_bar(b_part,wytchecklist):
    df0=df.loc[df['WYT_SAC_'].isin(convert_wyt_nums(wytchecklist))]
    df1 = round(df0.groupby(['Scenario','iwm']).mean())
    df1 = df1.reindex(scen_aliases, level='Scenario')
    fig = px.bar(df1, x = df1.index.get_level_values(1), y = b_part, 
                 color=df1.index.get_level_values(0), barmode='group')
    return fig


# Annual Bar Plot
@callback(
    Output(component_id='bar-plot-annual', component_property='figure'),
    Input(component_id='b-part', component_property='value'),
    Input(component_id='wytchecklist-bar', component_property='value'),
    Input(component_id='slider-yr-range', component_property='value')
)
def update_bar_annual(b_part,wytchecklist,slider_yr_range):
    startyr=slider_yr_range[0]
    endyr=slider_yr_range[1]
    df0=df.loc[df['WYT_SAC_'].isin(convert_wyt_nums(wytchecklist))]
    
    cfs_taf(df0,var_dict)
    
    df1 = round(df0.groupby(['Scenario']).sum()/(endyr-startyr+1))
    df1 = df1.reindex(scen_aliases, level='Scenario')
    fig = px.bar(df1, x = df1.index.get_level_values(0), y = b_part, 
                 color=df1.index.get_level_values(0),text_auto=True)
    fig.update_layout(barmode='relative')
    return fig

# Flow Summary tables
@callback(
    Output(component_id='sum_tbl', component_property='data'),
    Input(component_id='slider-yr-range', component_property='value'),
    Input(component_id='monthchecklist', component_property='value')
)
def update_table(slider_yr_range,monthchecklist):
    monthfilter = []
    for v in monthchecklist:
        monthfilter.append(month_map[v])

    df_tbl = make_summary_df(scen_aliases,df,var_dict,
                             start_yr=slider_yr_range[0],end_yr=slider_yr_range[1],
                             monthfilter=monthfilter)
    data=df_tbl.to_dict(orient='records')
    return data

# Reservoir Summary tables
@callback(
    Output(component_id='sum_tbl_res', component_property='data'),
    Input(component_id='slider-yr-range', component_property='value'),
    Input(component_id='monthradio', component_property='value')
)
def update_table2(slider_yr_range,monthradio):
    monthradio=[month_map[monthradio]]

    df_tbl = make_ressum_df(scen_aliases,df,var_dict,
                             start_yr=slider_yr_range[0],end_yr=slider_yr_range[1],
                             monthfilter=monthradio)
    data=df_tbl.to_dict(orient='records')
    return data

@callback(
    Output(component_id='output-container-range-slider', component_property='children'),
    Input(component_id='slider-yr-range', component_property='value')
)
def update_table(value):
    return value[0],str('-'),value[1]


#@callback(
#    Output('container-button-basic', 'children'),
#    Input('submit-val', 'n_clicks'),
#    prevent_initial_call=True
#)
#def load(n_clicks):
#    load_data_mult(scen_dict,var_dict,date_map)
#    return


@callback(
    Output('dummy-div1', 'children'),
    Input('load-studies', 'n_clicks'),
    State('file-table','data'),
    prevent_initial_call=True
)
def load(n_clicks,full_scen_table):
    scen_dict={}
    for s in full_scen_table:
        if (s['alias'].strip()!=''):
            scen_dict[s['alias']]=s['pathname']
    load_data_mult(scen_dict,var_dict,date_map)
    print(scen_dict)
    return "Loading"

# Callback to populate the ledger
@callback(
    Output('file-table', 'data'),
    Input('populate-table','n_clicks')
)
def populate_table(n_clicks):
    scenarios = list_files('uploads')
    for s in scenarios:
        new_entries = [{'pathname':scenarios[s],'filename': s, 'alias': ''} for s in scenarios]
    
    return new_entries

# Return a scenario dictionary with the aliases that user entered
@callback(
    Output('table-update-output','children'),
    Input('file-table','data')
)
def display_updated_data(full_scen_table):
    if full_scen_table is None:
        return "No data in the table."
    else:
        pass
        
    scen_dict={}
    for s in full_scen_table:
        if (s['alias'].strip()!=''):
            scen_dict[s['alias']]=s['pathname']
    #print(scen_dict)
    return #str(full_scen_table)


#@callback(
#    Output('file-table', 'data'),
#    [Input('upload-data', 'filename'),
#     Input('clear-button', 'n_clicks')],
#    [State('file-table', 'data')]
#)
#def update_or_clear_table(filenames, n_clicks_clear, existing_data):
#    ctx = dash.callback_context
#
#    if not ctx.triggered:
#        # No input has been triggered, do nothing
#        return existing_data
#
#    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
#
#    if triggered_id == 'upload-data':
#        # Handling file uploads
#        if filenames:
#            if not isinstance(filenames, list):
#                filenames = [filenames]  # Ensure filenames are in list form
#            new_entries = [{'filename': filename, 'alias': ''} for filename in filenames if filename not in {row['filename'] for row in existing_data}]
#            file_data.extend(new_entries)  # Add new entries to the global file_data
#            return file_data
#
#    elif triggered_id == 'clear-button':
#        # Handling clear button click
#        file_data.clear()  # Clear the global file_data
#        return []
#
#    return existing_data

#@callback(
#    Output('table-update-output','children'),
#    Input('file-table','data')
#)
#def display_updated_data(updated_rows):
#    if updated_rows is None:
#        return "No data in the table."
#    else:
#        # You can process the data as needed, here we just print it
#        return str(updated_rows)



#def parse_contents(contents, filename, date):
#    content_type, content_string = contents.split(',')
#    decoded = base64.b64decode(content_string)
#    try:
#        if 'text' in content_type:
#            # Assume that the user uploaded a text file
#            return html.Div([
#                html.H5(filename),
#                html.P(f"Last modified: {str(date)}"),
#                html.Pre(decoded.decode('utf-8'))
#            ])
#        elif 'image' in content_type:
#            # Assume that the user uploaded an image
#            return html.Div([
#                html.H5(filename),
#                html.P(f"Last modified: {str(date)}"),
#                html.Img(src=contents)
#            ])
#        else:
#            return html.Div([
#                'Unsupported file type: {}'.format(content_type)
#            ])
#    except Exception as e:
#        return html.Div([
#            'There was an error processing this file.'
#        ])



#@callback(
#    Output('output-data-upload', 'children'),
#    Input('upload-data', 'contents'),
#    State('upload-data', 'filename'),
#    State('upload-data', 'last_modified')
#)
#def update_output(list_of_contents, list_of_names, list_of_dates):
#    print(list_of_contents,list_of_names)
#    #if list_of_contents is not None:
#    #    children = [
#    #        parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
#    #    ]
#    return #children
