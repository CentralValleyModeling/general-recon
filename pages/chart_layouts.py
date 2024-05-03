import plotly.express as px
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from pages.study_selection import scen_aliases, var_dict, df
from utils.tools import convert_wyt_nums, cfs_taf


def ann_bar_plot(b_part='C_CAA003',startyr=1922,endyr=2021):

    startyr=1922
    endyr=2021
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
