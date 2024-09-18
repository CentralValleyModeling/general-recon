from collections import namedtuple

import pandas as pd
import yaml
from utils.tools import load_data_mult

# Scenario management
Study = namedtuple("Scenario", ["dv_path", "sv_path", "alias", "active"])

with open("constants/dvars.yaml", "r") as file:
    var_dict_dv = yaml.safe_load(file)
with open("constants/svars.yaml", "r") as file:
    var_dict_sv = yaml.safe_load(file)

s1 = Study(r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_1_wsidi_danubeadjv1.8.2\DSS\output\LTO_7.23.0_1_wsidi_danubeadjv1.8.2.dss",
           r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_1_wsidi_danubeadjv1.8.2\DSS\input\LTO_CCA_SV_Danube_Adj_v1.8.2_noshaspa.dss",
           "7.23.0_S1", 1)

s2 = Study(r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_12av2_wsidi_danubeadjv1.8.2\DSS\output\LTO_7.23.0_12av2_wsidi_danubeadjv1.8.2.dss",
           r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_12av2_wsidi_danubeadjv1.8.2\DSS\input\LTO_CCA_SV_Danube_Adj_v1.8.2.dss",
           "7.23.0_S12aV2", 1)

s3 = Study(r"C:\monuments\9.3.1_danube_adj\DSS\output\DCR2023_DV_9.3.1_v2a_Danube_Adj_v1.8.dss",
           r"C:\monuments\9.3.1_danube_adj\DSS\input\DCR2023_SV_Danube_Adj_v1.8.dss",
           "DCR_23", 1)

date_map = pd.read_csv("constants/date_map.csv", index_col=0, parse_dates=True)

studies = (s for s in [s1, s2, s3] if s.active == 1)

scen_dict_dv = {}
scen_dict_sv = {}
for s in studies:
    if s.active == 1:
        scen_dict_dv[s.alias] = s.dv_path
        scen_dict_sv[s.alias] = s.sv_path

print(scen_dict_dv)
print(scen_dict_sv)

# Load DV
load_data_mult(scen_dict_dv, var_dict_dv, date_map, "dv_data.csv")

# Load SV
#load_data_mult(scen_dict_sv, var_dict_sv, date_map, "sv_data.csv")
