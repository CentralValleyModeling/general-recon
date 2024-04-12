from utils.tools import load_data_mult
from collections import namedtuple
import yaml
import pandas as pd

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
s7 = Scenario('lto_analysis/DCR2023_DV_8.15.5_Nile_Adj_v15_LBGR.dss', 'LGBR_Test1',1)
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

load_data_mult(scenarios,var_dict,date_map)