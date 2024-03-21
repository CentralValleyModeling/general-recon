# Imports
from collections import namedtuple
import pandss as pdss
import pandas as pd
import numpy as np
import yaml

from dash import Dash, html, dcc, Input, Output, callback, dash_table
import plotly.express as px
#import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from utils import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums,
                   wyt_list, convert_wyt_nums, cfs_taf)

Scenario = namedtuple('Scenario',['pathname','alias','active'])
with open('dictionary.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)

s1 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1.dss', 'Baseline',1)
s2 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_1.dss', 'OA_1',1)
s3 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_2.dss', 'OA_2',1)
s4 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_3.dss', 'OA_3',1)
s5 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_4.dss', 'OA_4',1)

# Generator object for Scenarios
scenarios = (scenario for scenario in [s1,s2,s3,s4,s5] if scenario.active==1)

#load_data_mult(scenarios,var_dict)
bparts = []
aliases = []

for var in var_dict:
    bparts.append(var)
    aliases.append(var_dict[var]['alias'])

df = pd.read_csv('temp_mult.csv', index_col=0, parse_dates=True)

df_tbl = make_summary_df(df,var_dict)
df_tbl_res = make_ressum_df(df,var_dict)



app = Dash(__name__,external_stylesheets=[dbc.themes.YETI])

app.layout = dbc.Container([
    dcc.Markdown("# CalSim 3 Results Dashboard"),
    dcc.Markdown("### A General dashboard for reviewing CalSim 3 Results"),

dbc.Row([
    dbc.Col(
        [
            dcc.Upload(id='upload-data',
                children=html.Div([
                    'Connect to SQL Database ',
                    html.A('or Select DSS Files')
                ]),
                style={
                    'width': '100%',
                    'height': '120px',
                    'lineHeight': '120px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                }
            ),
            html.Button('Load', id='btn-load-study-1', n_clicks=0),
            html.Div(id='dummy-div',children=[])
        ],
        width=6
    ),

    dbc.Col(
        [
            "Select B-Part: ",
            dcc.Dropdown(bparts, id='b-part',value="D_OMR027_CAA000",
                        style={'width': '100%'}
                        ),
            "Or search by alias: ",
            dcc.Dropdown(options=aliases, id='alias',
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
                  dcc.Graph(id='bar-plot-annual')
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

    html.Button('Load', id='btn-refresh-tbl', n_clicks=0),

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
])

@app.callback(
  Output(component_id='dummy-div', component_property='children'),
  Input(component_id='btn-load-study-1', component_property='n_clicks'),
  prevent_initial_call=True
)
def load(n_clicks):
    load_data_mult(scenarios,var_dict)
    return


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
    scenarios = (scenario for scenario in [s1,s2,s3,s4] if scenario.active==1)
    for scenario in scenarios:
        #print(scenario[1])
        df1 = df0.loc[df0['Scenario']==scenario[1],b_part]
        #print(df1)
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario[1]]=df1
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
    
    print(yw)
    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    cfs_taf(df0,var_dict)
    df0 = df0.groupby(['Scenario',yw]).sum()
    print(df0)
    scenarios = (scenario for scenario in [s1,s2,s3,s4] if scenario.active==1)
    for scenario in scenarios:
        df1 = df0.loc[df0.index.get_level_values(0)==scenario[1],b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario[1]]=df1
    fig = px.line(df2)
    print(df2)

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
    fig = px.bar(df1, x = df1.index.get_level_values(1), y = b_part, 
                 color=df1.index.get_level_values(0), barmode='group')
    print(wytchecklist)
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
    fig = px.bar(df1, x = df1.index.get_level_values(0), y = b_part, 
                 color=df1.index.get_level_values(0),text_auto=True)
    fig.update_layout(barmode='relative')
    return fig

# Summary tables
@callback(
    Output(component_id='sum_tbl', component_property='data'),
    Input(component_id='slider-yr-range', component_property='value'),
    Input(component_id='monthchecklist', component_property='value')
)
def update_table(slider_yr_range,monthchecklist):
    monthfilter = []
    for v in monthchecklist:
        monthfilter.append(month_map[v])

    df_tbl = make_summary_df(df,var_dict,
                             start_yr=slider_yr_range[0],end_yr=slider_yr_range[1],
                             monthfilter=monthfilter)
    data=df_tbl.to_dict(orient='records')
    return data

@callback(
    Output(component_id='sum_tbl_res', component_property='data'),
    Input(component_id='slider-yr-range', component_property='value'),
    Input(component_id='monthradio', component_property='value')
)
def update_table2(slider_yr_range,monthradio):
    monthradio=[month_map[monthradio]]

    df_tbl = make_ressum_df(df,var_dict,
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

if __name__ == '__main__':
    app.run(debug=True)
