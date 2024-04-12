from dash import html, register_page, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from utils.tools import load_data_mult
from collections import namedtuple
import yaml
import pandas as pd

register_page(
    __name__,
    #name='Page 2',
    top_nav=True,
    path='/study_selection'
)

# Scenario management
Scenario = namedtuple('Scenario',['pathname','alias','active'])
with open('constants/vars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)

s1 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_Hist_v1.1.dss', 'Hist',1)
s2 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_Adj_v1.2.dss', 'AdjHist',1)
s3 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_CC50_v1.2.1.dss', 'CC50',1)
s4 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_CC75_v1.2.1.dss', 'CC75',1)
s5 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_CC95_v1.2.1.dss', 'CC95',1)
s6 = Scenario('lto_analysis/DCR2023_DV_8.13.3_Nile_Adj_v7_2000TAF_Post_WSIDI.dss', 'LGBR_Test2',1)
s7 = Scenario('lto_analysis/DCR2023_DV_8.15.5_Nile_Adj_v15_LBGR.dss', 'LGBR_Test1',0)
s8 = Scenario('lto_analysis/DCR2023_DV_8.15.5_Nile_Hist_v14_orov_sens.dss', 'OrovSens',1)
s9 = Scenario('lto_analysis/LTO_NAA_2022MED_06302023_DV.dss', 'LTO_NAA_2022MED',1)
s10 = Scenario('lto_analysis/LTO_Study1.12.13.dss', 'LTO_1.12.13',1)
s11 = Scenario('lto_analysis/LTO_Study1.12.13b.dss', 'LTO_1.12.13b',1)
s12 = Scenario('lto_analysis/LTO_Study2.5.dss', 'LTO_2.5',1)
s13 = Scenario('lto_analysis/LTO_Study7.14.13.dss', 'LTO_7.14.13',1)
s14 = Scenario('lto_analysis/LTO_Study7.14.13b.dss', 'LTO_7.14.13b',1)
s15 = Scenario('lto_analysis/LTO_Study10.12.18.dss', 'LTO_10.12.18',1)

date_map = pd.read_csv('constants/date_map.csv', index_col=0, parse_dates=True)

# Generator object for Scenarios
scenarios = (scenario for scenario in [s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s14,s15] if scenario.active==1)

scen_aliases = []
for s in scenarios:
    if s.active==1:
        scen_aliases.append(s.alias)

def layout():
    layout = dbc.Container([

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
        ])
    ])
    return layout



#@callback(
#  Output(component_id='dummy-div', component_property='children'),
#  Input(component_id='btn-load-study-1', component_property='n_clicks'),
#  prevent_initial_call=True
#)
#def load(n_clicks):
#    load_data_mult(scenarios,var_dict)
#    return
