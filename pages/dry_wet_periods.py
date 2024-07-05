from dash import html, register_page, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from charts.chart_layouts import ta_dry_wet_barplot
from pages.styles import GLOBAL_MARGIN
from utils.query_data import df_dv, scen_aliases, var_dict
from utils.tools import (make_summary_df,common_pers,month_list)

register_page(
    __name__,
    name='Dry and Wet Periods',
    top_nav=True,
    path='/dry_wet_periods'
)

#afig=ta_dry_wet_barplot(df_dv,common_pers,bpart="SWP_TA_CO_SOD",scens=scen_aliases)

def layout():
    layout = dbc.Container([
        dcc.Dropdown(["SWP_TA_CO_SOD"], id='b-part2',value="SWP_TA_CO_SOD",
            style={'width': '100%'}
            ),
        dcc.Graph(id='ta-dry-wet-pers')
    ])
    return layout


@callback(
    Output(component_id='ta-dry-wet-pers', component_property='figure'),
    Input(component_id='b-part2', component_property='value'),
)
def makefigures(bpart):

    #fig=ta_dry_wet_barplot(df_dv,common_pers,bpart="SWP_TA_CO_SOD",scens=scen_aliases)
    return #fig
