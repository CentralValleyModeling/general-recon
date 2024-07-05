import pandas as pd
import plotly.express as px
#import plotly.figure_factory as ff
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.query_data import scen_aliases, var_dict
from pages.styles import PLOT_COLORS
from utils.tools import (convert_wyt_nums, cfs_taf, convert_cm_nums,
                         monthfilter, month_list,wyt_list,common_pers)



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
                        #dcc.Dropdown(options = common_pers,id='dropdown_common_pers'),
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


def card_bar_plot_cy(df,b_part='C_CAA003',wyt=[1,2,3,4,5],startyr=1922,endyr=2021):
    
    # This is VERY specific to the DCR 2021
    df_dcr21=df.loc[(df['Scenario'].isin(["DCR_21_Hist"])) & (df['icy'] >=startyr)]
    try:
        df_dcr21=cfs_taf(df_dcr21,var_dict)
    except:
        print("Unable to convert from CFS to TAF")

    df_dcr21_ann = round(df_dcr21.groupby(['Scenario']).sum()/(2015-1922+1))

    df0=df.loc[df['Scenario'].isin(["DCR_23_Adj",
                                    "DCR_23_CC50",
                                    "DCR_23_CC75",
                                    "DCR_23_CC95",])
                                    & (df['icy'] >=startyr)]

    try:
        df0=cfs_taf(df0,var_dict)
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
    
    df0=cfs_taf(df0,var_dict)
    
    df1 = round(df0.groupby(['Scenario']).sum()/(endyr-startyr+1))
    df1 = df1.reindex(scen_aliases, level='Scenario')
    fig = px.bar(df1, x = df1.index.get_level_values(0), y = b_part, 
                 color=df1.index.get_level_values(0),text_auto=True,
                 color_discrete_sequence=PLOT_COLORS)
    fig.update_layout(barmode='relative',
                      plot_bgcolor='white',)
    #fig.update_xaxes(gridcolor='LightGrey')
    fig.update_yaxes(gridcolor='LightGrey')
    return fig

def mon_exc_plot(df,b_part,monthchecklist):
    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    for scenario in scen_aliases:
        df1 = df0.loc[df0['Scenario']==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1
    fig = px.line(df2,
                  color_discrete_sequence=PLOT_COLORS,
                  labels={'variable':"Scenario"})
    fig.update_layout(
                title=f"Monthly Non-Exceedance Chart for {b_part}",
                plot_bgcolor='white',
                showlegend=True,
                xaxis_title='Non-Exceedance Percentage',
                yaxis_title='',
                xaxis_tickformat=',d',)
    fig.update_xaxes(gridcolor='LightGrey')
    fig.update_yaxes(gridcolor='LightGrey')
    return fig

def ann_exc_plot(df,b_part,monthchecklist,yearwindow):
    if yearwindow=="Calendar Year":
        yw='icy'
    else:
        yw='iwy'

    df2 = pd.DataFrame()
    df0 = df.loc[df['icm'].isin(convert_cm_nums(monthchecklist))]
    df0=cfs_taf(df0,var_dict)

    df0 = df0.groupby(['Scenario',yw]).sum()

    for scenario in scen_aliases:
        df1 = df0.loc[df0.index.get_level_values(0)==scenario,b_part]
        df1 = df1.sort_values()
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1
    fig = px.line(df2,
                  color_discrete_sequence=PLOT_COLORS)
    fig.update_layout(
                    title=f"Non-Exceedance Chart for {b_part}, ({yearwindow})",
                    plot_bgcolor='white',
                    showlegend=True,
                    xaxis_title='Non-Exceedance Percentage',
                    yaxis_title='',
                    xaxis_tickformat=',d')
    fig.update_xaxes(gridcolor='LightGrey') #griddash='dot', minor_griddash="dot")
    fig.update_yaxes(gridcolor='LightGrey') #griddash='dot', minor_griddash="dot")
    return fig

def distplot(df,b_part):
    df2 = pd.DataFrame()
    df0 = df
    df0=cfs_taf(df0,var_dict)
    df0 = df0.groupby(['Scenario','iwy']).sum()

    for scenario in scen_aliases:
        df1 = df0.loc[df0.index.get_level_values(0)==scenario,b_part]
        df1 = df1.reset_index(drop=True)
        df2[scenario]=df1

    fig = px.histogram(df2,marginal="box",color_discrete_sequence=PLOT_COLORS,barmode="relative")
    return fig

def ta_dry_wet_barplot(df,common_pers,bpart="SWP_TA_CO_SOD",scens=["DCR_21_Hist"],ta_tot=4133):    
    df1=pd.DataFrame()
    df=cfs_taf(df,var_dict)
    l ={"scenario":[],"period":[],'avg':[],'pct':[]}
    l_df=pd.DataFrame()
    for s in scens:
        for c in common_pers:
            if c in list(common_pers.keys())[:2]:
                continue
            startyr = int(common_pers[c].split('-')[0])
            endyr = int(common_pers[c].split('-')[-1])
            df1=df.loc[df["Scenario"]==s,[bpart,'icy']]
            df2 = df1.loc[df1['icy'].between(startyr,endyr)]
            v = round(df2[bpart].sum()/(endyr-startyr+1),0)
            l['scenario'].append(s)
            l['period'].append(c)
            l['avg'].append(v)
            l['pct'].append(round((v/ta_tot),2))
    l_df=pd.DataFrame(l)
    #print(l_df)
    fig = px.bar(l_df,x='period',y='pct',
                    text='pct',
                    color='scenario',
                    barmode='group',
                    color_discrete_sequence=PLOT_COLORS,
                    hover_data={'avg':True})
    fig.update_layout(yaxis_tickformat = '.0%',
                        xaxis_title='Sub Periods',
                        yaxis_title='Percent',
                        yaxis = dict(tickmode='array',
                                    tickvals=[i/100 for i in range(0, 101, 10)],
                                    ticktext=[f'{i}%' for i in range(0, 101, 10)])
    )
    fig.update_traces(textposition='outside')

    
    return fig
