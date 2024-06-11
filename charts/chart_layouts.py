import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.query_data import df, scen_aliases, var_dict
from utils.tools import convert_wyt_nums, cfs_taf, convert_cm_nums


def card_bar_plot(b_part='C_CAA003',startyr=1922,endyr=2021):
    
    # This is VERY specific to the DCR 2021
    df_dcr21=df.loc[df['WYT_SAC_'].isin([1,2,3,4,5]) &
               df['Scenario'].isin(["DCR_21_Hist"])]
    cfs_taf(df_dcr21,var_dict)
    df_dcr21_ann = round(df_dcr21.groupby(['Scenario']).sum()/(2015-1922+1))

    df0=df.loc[df['WYT_SAC_'].isin([1,2,3,4,5]) &
               df['Scenario'].isin(["DCR_23_Adj",
                                    "DCR_23_CC50",
                                    "DCR_23_CC75",
                                    "DCR_23_CC95",])]

    cfs_taf(df0,var_dict)
    df1 = round(df0.groupby(['Scenario']).sum()/(endyr-startyr+1))

    df_plot = pd.concat([df_dcr21_ann,df1])

    fig = px.bar(df_plot[b_part],text = df_plot[b_part],color=df_plot.index,orientation='h')
    
    fig.update_layout(barmode='relative',plot_bgcolor='white',
                      width = 600,
                      height = 300,
                      showlegend=False,
                      xaxis_title='TAF/Year',
                      yaxis_title='',
                      xaxis_tickformat=',d')

    layout = html.Div([dcc.Graph(figure=fig)])
    return layout

def card_mon_exc_plot(b_part,monthchecklist):
    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    for scenario in scen_aliases:
        df1 = df0.loc[df0['Scenario']==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1

    fig = px.line(df2,labels={'variable':"Scenarios"})

    fig.update_layout(plot_bgcolor='white',
                      width = 600,
                      height = 400,
                      showlegend=True,
                      xaxis_title='Non-Exceedance Percentage',
                      yaxis_title='',
                      xaxis_tickformat=',d')

    layout = html.Div([
        dbc.Col([dcc.Markdown("**Monthly Exceedance**"),
            dcc.Graph(figure=fig),
        ]),
    ])
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