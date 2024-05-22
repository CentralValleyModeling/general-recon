from utils.tools import load_data_mult
from collections import namedtuple
import yaml
import pandas as pd

# Scenario management
Scenario = namedtuple('Scenario',['pathname','alias','active'])
with open('constants/vars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)


s1 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1.dss', 'DCR_hist',1)
s2 = Scenario('oa_analysis/9.0.0_Danube_Hist_v1.1_oa_2.dss', 'DCR_hist_runflat',1)
s3 = Scenario('oa_analysis/cc_adapt_dv_Danube_Hist_v1.3.dss', 'cca_hist',1)
s4 = Scenario('oa_analysis/cc_adapt_dv_Danube_Hist_v1.3_runflat.dss', 'cca_runflat',1)

date_map = pd.read_csv('constants/date_map.csv', index_col=0, parse_dates=True)

scenarios = (scenario for scenario in [s1,s2,s3,s4] if scenario.active==1)

scen_dict={}
for s in scenarios:
    if s.active==1:
        scen_dict[s.alias] = s.pathname

load_data_mult(scen_dict,var_dict,date_map)