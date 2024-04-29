from dash import html, register_page, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc

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

#s1 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_Hist_v1.1.dss', 'Hist',1)
#s2 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_Adj_v1.2.dss', 'AdjHist',1)
#s3 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_CC50_v1.2.1.dss', 'CC50',1)
#s4 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_CC75_v1.2.1.dss', 'CC75',1)
#s5 = Scenario('dcr_analysis/DCR2023_DV_9.0.0_Danube_CC95_v1.2.1.dss', 'CC95',1)
#s6 = Scenario('lto_analysis/DCR2023_DV_8.13.3_Nile_Adj_v7_2000TAF_Post_WSIDI.dss', 'LGBR_Test2',1)
#s7 = Scenario('lto_analysis/DCR2023_DV_8.15.5_Nile_Adj_v15_LBGR.dss', 'LGBR_Test1',0)
#s8 = Scenario('lto_analysis/DCR2023_DV_8.15.5_Nile_Hist_v14_orov_sens.dss', 'OrovSens',1)
#s9 = Scenario('lto_analysis/LTO_NAA_2022MED_06302023_DV.dss', 'LTO_NAA_2022MED',1)
#s10 = Scenario('lto_analysis/LTO_Study1.12.13.dss', 'LTO_1.12.13',1)
#s11 = Scenario('lto_analysis/LTO_Study1.12.13b.dss', 'LTO_1.12.13b',1)
#s12 = Scenario('lto_analysis/LTO_Study2.5.dss', 'LTO_2.5',1)
#s13 = Scenario('lto_analysis/LTO_Study7.14.13.dss', 'LTO_7.14.13',1)
#s14 = Scenario('lto_analysis/LTO_Study7.14.13b.dss', 'LTO_7.14.13b',1)
#s15 = Scenario('lto_analysis/LTO_Study10.12.18.dss', 'LTO_10.12.18',1)

# s1 = Scenario('lto_analysis/LTO_Study7U.15.09_adjhist.dss', 'adj_S9bv2',1)
# s2 = Scenario('lto_analysis/LTO_Study7U.15.09_adjhist_ShasPA.dss', 'adj_S9bv2_ShasPA',1)
# s3 = Scenario('lto_analysis/LTO_Study11a.14.22alt_noShasPA1.dss', 'hist_S7',1)
# s4 = Scenario('lto_analysis/LTO_Study11a.14.22alt_ShasPA.dss', 'hist_S7_ShasPA',1)

#s1 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1.dss', 'DCR_Hist',1)
#s2 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_1.dss', 'DCR_Hist_OA',1)
#s3 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_1_split.dss', 'DCR_Hist_OA_Split',1)
#s4 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_2.dss', 'OA_runflat',1)
#s5 = Scenario('oa_analysis/cc_adapt_dv_3.0.3_runflat_hist.dss', 'OA_runflat_switch',1)
#s6 = Scenario('oa_analysis/cc_adapt_dv_Danube_Hist_v1.3.dss', 'cca_hist',1)
#s7 = Scenario('oa_analysis/cc_adapt_dv_Danube_Hist_v1.3_runflat.dss', 'cca_runflat',1)


s1 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1.dss', 'DCR_hist',1)
s2 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_2.dss', 'DCR_hist_runflat',1)
s3 = Scenario('oa_analysis/cc_adapt_dv_Danube_Hist_v1.3.dss', 'cca_hist',1)
s4 = Scenario('oa_analysis/cc_adapt_dv_Danube_Hist_v1.3_runflat.dss', 'cca_runflat',1)

date_map = pd.read_csv('constants/date_map.csv', index_col=0, parse_dates=True)

scenarios = (scenario for scenario in [s1,s2,s3,s4] if scenario.active==1)

scen_aliases = []
scen_dict={}
for s in scenarios:
    if s.active==1:
        scen_aliases.append(s.alias)
        scen_dict[s.alias] = s.pathname

#print(scen_dict)

#for s in scen_dict:
#    print (scen_dict[s])

def layout():
    layout = dbc.Container([

        dbc.Row([
            dbc.Col(
                [
                    dcc.Upload(
                        id='upload-data',
                        children=html.Button('Drag and Drop or Browse DV DSS Files'),  # Text on the browse button
                        style={
                            'width': '100%',
                            'height': '100px',
                            'lineHeight': '20px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=False
                    ),
                    dash_table.DataTable(
                        id='file-table',
                        columns=[{'name': 'Filename', 'id': 'filename'}],
                        data=[],
                        editable=True
                    ),
                    html.Button('Clear List', id='clear-button', style={'margin-top': '10px'}),  # Button to clear the list
                    html.Button('Load into CSV Family', id='submit-val', n_clicks=0),
                ],
                width=6
            ),
        ])
    ])
    return layout




