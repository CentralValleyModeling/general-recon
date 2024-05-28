import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.query_data import df, scen_aliases, var_dict
from utils.tools import convert_wyt_nums, cfs_taf, convert_cm_nums


def card_bar_plot(b_part='C_CAA003',startyr=1922,endyr=2021):

    df0=df.loc[df['WYT_SAC_'].isin([1,2,3,4,5,6,7,8,9,10,11,12]) &
               df['Scenario'].isin(["Hist","AdjHist"])]

    cfs_taf(df0,var_dict)
    df1 = round(df0.groupby(['Scenario']).sum()/(endyr-startyr+1))
    
    #print(df1[b_part])
    fig = px.bar(df1[b_part],text = df1[b_part],color=df1.index,orientation='h')
    
    fig.update_layout(barmode='relative',plot_bgcolor='white',
                      width = 600,
                      height = 200,
                      showlegend=False,
                      xaxis_title='',
                      yaxis_title='')

    layout = html.Div([dcc.Graph(figure=fig)])
    return layout

def ann_bar_plot(b_part='C_CAA003',startyr=1922,endyr=2021):

    df0=df.loc[df['WYT_SAC_'].isin([1,2,3,4,5,6,7,8,9,10,11,12])]
    
    cfs_taf(df0,var_dict)
    
    df1 = round(df0.groupby(['Scenario']).sum()/(endyr-startyr+1))
    df1 = df1.reindex(scen_aliases, level='Scenario')
    fig = px.bar(df1, x = df1.index.get_level_values(0), y = b_part, 
                 color=df1.index.get_level_values(0),text_auto=True)
    fig.update_layout(barmode='relative')

    layout = html.Div([
        dbc.Col([dcc.Markdown("**Annual Average**"),
            dcc.Graph(figure=fig),
        ]),
    ])
    return layout

def mon_exc_plot(b_part,monthchecklist):
    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    for scenario in scen_aliases:
        df1 = df0.loc[df0['Scenario']==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1
    fig = px.line(df2)

    layout = html.Div([
        dbc.Col([dcc.Markdown("**Monthly Exceedance**"),
            dcc.Graph(figure=fig),
        ]),
    ])
    return layout