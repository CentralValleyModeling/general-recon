import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page
import dash_bootstrap_components as dbc
import pandas as pd

from utils.tools import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums,
                   wyt_list, convert_wyt_nums, cfs_taf)

from pages.study_selection import scen_aliases, var_dict, df
from  pages.drilldown import layout as dd
from pages.chart_layouts import ann_bar_plot

register_page(
    __name__,
    top_nav=True,
    path='/heatmap'
)
print(df)
# Make dataframe for heatmap
def make_heatmap_df(scen_aliases,df,var_dict,start_yr=1922,end_yr=2021,
                    monthfilter=[1,2,3,4,5,6,7,8,9,10,11,12],wytfilter=[1,2,3,4,5],bparts=None):

    #df0=df.loc[df['WYT_SAC_'].isin(convert_wyt_nums(wytchecklist))]
    
    # Do Filters
    df1 = df.loc[(df['icm'].isin(monthfilter)) & # Filter cal months
                (df['iwy']>=start_yr) & (df['iwy']<=end_yr) & # Filter Start/End Year
                df['WYT_SAC_'].isin(wytfilter) #Filter Water Year Type (SVI)
                ] 

    for var in var_dict:
        if var_dict[var]['table_convert']=='cfs_taf':
            df1[var]=df1[var]*df1['cfs_taf']
        else:
            continue
    
    # Annual Average
    df_tbl = round(df1.groupby(["Scenario"]).sum()/(end_yr-start_yr+1))

    df_tbl = (df_tbl - df_tbl.iloc[0])/df_tbl.iloc[0]
    df_tbl = df_tbl[df_tbl.index.isin(scen_aliases)]


    # Time slicing is done; drop the index columns
    df_tbl.drop(['icy','icm','iwy','iwm','cfs_taf'],axis=1,inplace=True)

    if bparts != None:
        df1 = df_tbl.loc[:,bparts]
        df_tbl = df1

    # Make a dictionary of just aliases to map to the dataframe
    alias_dict = {}
    type_dict = {}
    for key in var_dict:
        alias_dict[key]=var_dict[key]['alias']
        type_dict[key]=var_dict[key]['type']

    return df_tbl

bparts=[
    'S_OROVL',
    'S_SLUIS_SWP',
    'C_KSWCK',
    'C_SAC097',
    'C_FTR059',
    'C_FTR003',
    'C_YUB006',
    'C_SAC083',
    'C_NTOMA',
    'C_AMR004',
#   '----'
#    'DELTAINFLOWFORNDOI',
#    '----'
    'C_CAA003',
    'C_DMC000',
    'NDOI',
    'NDOI_ADD',
#    '----',
    'SWP_TA_TOTAL',
    'SWP_IN_TOTAL',
    'SWP_CO_TOTAL',
    'CVPTOTALDEL']


#print(heatmap_df)

def layout():
    layout = dbc.Container([
        dbc.Row([
            dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Metric Heat Map"),
            dcc.RangeSlider(1922, 2021, 1, value=[1922, 2021],
                marks={i: '{}'.format(i) for i in range(1922,2021,5)},
                pushable=False,
                id='slider-yr-range-hm'),
            dbc.Col([
                html.P("Month"),
                dcc.Checklist(
                    options = month_list, value = month_list, inline=False,
                    id = 'monthchecklist-hm',
                    style={'fontSize':10},
                    
                ),
            ], width={"size": 1}),
            dbc.Col([
                html.P("Sac Valley Index"),
                dcc.Checklist(options = wyt_list,
                    value = wyt_list,
                    inline=False,
                    id = 'wytchecklist-hm',
                    style={'fontSize':10},
                    #inputStyle={"margin-right": "5px","margin-left": "30px"},
                ),
            ], width={"size": 1}),

            dbc.Col([
                html.P("Variables Included"),
                dcc.Checklist(
                        id='vars',
                        options=bparts,
                        value=bparts,
                        inline=False,
                        style={'fontSize':10},
                    ),
            ], width={"size": 2}),



            dbc.Col([
                dcc.Graph(id='heatmap'),
                
                html.Pre(id='click-data'),      
            ], width={"size": 8}),
        ]),

        dbc.Row([
            html.Div(id='bar-plot-annual'),
        ]),

    ],
    )
    return layout

layout()

@callback(
    Output("heatmap", "figure"), 
    Input("vars", "value"),
    Input('slider-yr-range-hm','value'),
    Input('monthchecklist-hm','value'),
    Input('wytchecklist-hm','value'),
)
def filter_heatmap(cols,slider_yr_range,monthchecklist,wytchecklist):
    start_yr=slider_yr_range[0]
    end_yr=slider_yr_range[1]
    print(wytchecklist)
    monthfilter=convert_cm_nums(monthchecklist)
    wytfilter=convert_wyt_nums(wytchecklist)
    df_hm = make_heatmap_df(scen_aliases,df,var_dict,
                            start_yr=start_yr,end_yr=end_yr,
                            monthfilter=monthfilter,
                            wytfilter=wytfilter,
                            bparts=bparts)
    fig = px.imshow(df_hm[cols])#,color_continuous_scale=px.colors.sequential.Viridis)
    fig.layout.height = 500
    fig.layout.width = 800
    fig.update_traces(dict(showscale=False, 
                       coloraxis=None, 
    ))
    #fig.update_layout(paper_bgcolor="WhiteSmoke")
    #fig.color_continuous_scale="Viridis"
    #fig.color_continuous_scale=[[0, 'red'], [0.5, 'yellow'], [1, 'blue']]
    return fig

@callback(
    Output('bar-plot-annual', 'children'),
    Input('heatmap', 'clickData'),
    prevent_initial_call=True
)
def display_click_data(clickData):
    if clickData is None:
        return 'Click on a cell'
    else:
        # Extract the coordinates of the clicked cell
        point = clickData['points'][0]
        x = point['x']
        #y = point['y']
        value = {var_dict[x]['alias']}
        return  ann_bar_plot(b_part=x)
