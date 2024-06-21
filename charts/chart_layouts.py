import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.query_data import scen_aliases, var_dict
from utils.tools import convert_wyt_nums, cfs_taf, convert_cm_nums, monthfilter, month_list
from pages.styles import PLOT_COLORS



class CardWidget():
    def __init__(self,title,button_id,button_label="Explore",
                 chart=None,text=None,image=None) -> None:
        self.title = title
        self.button_id = button_id
        self.button_label = button_label
        self.chart = chart
        self.text = text
        self.image = image

    def create_card(self,height="35rem",wyt=[1,2,3,4,5],startyr=1922,endyr=2021,):

        card = dbc.Card(
            [
                dbc.CardImg(src=self.image, top=True),
                dbc.CardBody(
                    [
                        html.H4(self.title, className="card-title"),
                        self.chart,
                        html.P(self.text, className="card-text"),
                        dbc.Button(self.button_label, id={'type': 'dynamic-btn', 'index': self.button_id}, color="primary") 
                            if self.button_label is not None else None,
                    ]
                ),
            ],
            style={"height": height}
        )

        return card

def card_mon_plot(df,b_part='C_CAA003',yaxis_title=None,
                  startyr=1922,endyr=2021,wyt=[1,2,3,4,5]):
    #try:
    #    df1=df.loc[df['WYT_SAC_'].isin(wyt)]
    #except:
    #    print("WYT_SAC_ timeseries not found")
    df1 = df.loc[df['WYT_SAC_'].isin(wyt)]
    df1 = round(df1.groupby(['Scenario','iwm']).mean())
    df1 = df1.reindex(scen_aliases, level='Scenario')
    fig = px.line(df1, x = df1.index.get_level_values(1), y = b_part, 
                 color=df1.index.get_level_values(0),
                 labels={'color':"Scenario"},
                 color_discrete_sequence=PLOT_COLORS,)
    
    fig.update_layout(
        plot_bgcolor='white',
        xaxis=dict(
        tickmode='array',
        tickvals= monthfilter,
        ticktext= month_list,
        showgrid=True,
        gridcolor='LightGray',
        ),
        yaxis=dict(
        showgrid=True,
        gridcolor='LightGray',
        ),        
        yaxis_tickformat=',d',
        xaxis_title="Month",
        yaxis_title=yaxis_title if yaxis_title is not None else b_part,
        
    )
    layout = html.Div([dcc.Graph(figure=fig)])
    return layout


def card_bar_plot_wy(df,b_part='C_CAA003',wyt=[1,2,3,4,5],startyr=1922,endyr=2021):
    
    # This is VERY specific to the DCR 2021
    df_dcr21=df.loc[(df['Scenario'].isin(["DCR_21_Hist"])) & (df['icy'] >=startyr)]
    try:
        cfs_taf(df_dcr21,var_dict)
    except:
        print("Unable to convert from CFS to TAF")

    df_dcr21_ann = round(df_dcr21.groupby(['Scenario']).sum()/(2015-1922+1))




    df0=df.loc[df['Scenario'].isin(["DCR_23_Adj",
                                    "DCR_23_CC50",
                                    "DCR_23_CC75",
                                    "DCR_23_CC95",])
                                    & (df['icy'] >=startyr)]

    try:
        cfs_taf(df0,var_dict)
    except:
        print("Unable to convert from CFS to TAF")

    # For the last year

    #df_annual = df0.groupby(['icy']).sum()
    #print(df_annual)

    df1 = round(df0.groupby(['Scenario']).sum()/(endyr-startyr+1))

    df_plot = pd.concat([df_dcr21_ann,df1])

    fig = px.bar(df_plot[b_part],text = df_plot[b_part],color=df_plot.index,orientation='h',
                 color_discrete_sequence=PLOT_COLORS,)
    
    fig.update_layout(barmode='relative',plot_bgcolor='white',
                      width = 600,
                      height = 300,
                      showlegend=False,
                      xaxis_title='TAF/Year',
                      yaxis_title='',
                      xaxis_tickformat=',d')

    layout = html.Div([dcc.Graph(figure=fig)])
    return layout

def card_mon_exc_plot(df,b_part,monthchecklist):
    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    for scenario in scen_aliases:
        df1 = df0.loc[df0['Scenario']==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1

    fig = px.line(df2,labels={'variable':"Scenarios"},
                  color_discrete_sequence=PLOT_COLORS)

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

def ann_bar_plot(df,b_part='C_CAA003',startyr=1922,endyr=2021,wyt=[1,2,3,4,5]):

    try:
        df0=df.loc[df['WYT_SAC_'].isin(wyt)]
    except KeyError as e:
        print(e)
    
    cfs_taf(df0,var_dict)
    
    df1 = round(df0.groupby(['Scenario']).sum()/(endyr-startyr+1))
    df1 = df1.reindex(scen_aliases, level='Scenario')
    fig = px.bar(df1, x = df1.index.get_level_values(0), y = b_part, 
                 color=df1.index.get_level_values(0),text_auto=True,
                 color_discrete_sequence=PLOT_COLORS)
    fig.update_layout(barmode='relative')

    layout = html.Div([
        dbc.Col([dcc.Markdown("**Annual Average**"),
            dcc.Graph(figure=fig),
        ]),
    ])
    return layout

def mon_exc_plot(df,b_part,monthchecklist):
    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    for scenario in scen_aliases:
        df1 = df0.loc[df0['Scenario']==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1
    fig = px.line(df2,
                  color_discrete_sequence=PLOT_COLORS)

    layout = html.Div([
        dbc.Col([dcc.Markdown("**Monthly Exceedance**"),
            dcc.Graph(figure=fig),
        ]),
    ])
    return layout