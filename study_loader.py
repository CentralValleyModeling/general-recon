from collections import namedtuple

import pandas as pd
import yaml
from utils import list_files, load_data_mult
from pathlib import Path

# Scenario management
Study = namedtuple("Scenario", ["dv_path", "sv_path", "alias", "active"])

with open("constants/dvars.yaml", "r") as file:
    var_dict_dv = yaml.safe_load(file)
with open("constants/svars.yaml", "r") as file:
    var_dict_sv = yaml.safe_load(file)
with open("study_ledger.yaml", "r") as file:
    study_ledger = yaml.safe_load(file)





print(list_files(Path(r'C:\jobs\20240426_CCA\20240920_models')))


s1 = Study(r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\CCA1_v3.6.x__Baseline_LU100_SLR0_20240806.dss",
           r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\CCA_SV_Danube_Adj_v1.9.dss",
           "CCA1_HistAdj", 1)

s2 = Study(r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\CCA4_v3.6.x__2043_50CC_LU100_SLR15_20240806.dss",
           r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\DCR2023_SV_Danube_2043_cc50_v1.9.dss",
           "CCA4_2043_50CC", 1)

s3 = Study(r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\CCA6_v3.6.x_A_2043_50CC_LU100_SLR15_20240806.dss",
           r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\DCR2023_SV_Danube_2043_cc50_v1.9.dss",
           "CCA6_2043_50CC", 1)

s4 = Study(r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\CCA8_v3.6.x_D_2043_50CC_LU100_SLR15_20240806.dss",
           r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\DCR2023_SV_Danube_2043_cc50_v1.9.dss",
           "CCA8_2043_50CC", 1)

s5 = Study(r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\CCA10_v3.6.x_C_2043_50CC_LU100_SLR15_20240806.dss",
           r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\DCR2023_SV_Danube_2043_cc50_v1.9.dss",
           "CCA10_2043_50CC", 1)

s6 = Study(r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\CCA12_v3.6.x_ACD_2043_50CC_LU100_SLR15_20240806.dss",
           r"C:\Users\ycheng\Desktop\ClimateAdaptation\ReCon\2043-50CC\20240807\DCR2023_SV_Danube_2043_cc50_v1.9.dss",
           "CCA12_2043_50CC", 1)

date_map = pd.read_csv("constants/date_map.csv", index_col=0, parse_dates=True)

studies = (s for s in [s1, s2, s3, s4, s5, s6] if s.active == 1)

scen_dict_dv = {}
scen_dict_sv = {}
for s in studies:
    if s.active == 1:
        scen_dict_dv[s.alias] = s.dv_path
        scen_dict_sv[s.alias] = s.sv_path

print(scen_dict_dv)
print(scen_dict_sv)

# Load DV
#load_data_mult(scen_dict_dv, var_dict_dv, date_map, "dv_data.csv")

# Load SV
#load_data_mult(scen_dict_sv, var_dict_sv, date_map, "sv_data.csv")
