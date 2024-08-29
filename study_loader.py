from collections import namedtuple

import pandas as pd
import yaml
from pathlib import Path
from utils.tools import load_data_mult

# Scenario management
Scenario = namedtuple("Scenario", ["pathname", "alias", "active"])
with open("constants/svars.yaml", "r") as file:
#with open("constants/dvars.yaml", "r") as file:
    var_dict = yaml.safe_load(file)


#s1 = Scenario(r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_1_wsidi_danubeadjv1.8.2\DSS\output\LTO_7.23.0_1_wsidi_danubeadjv1.8.2.dss", "7.23.0_S1", 1)
#s2 = Scenario(r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_12av2_wsidi_danubeadjv1.8.2\DSS\output\LTO_7.23.0_12av2_wsidi_danubeadjv1.8.2.dss", "7.23.0_S12aV2", 1)

s1 = Scenario(r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_1_wsidi_danubeadjv1.8.2\DSS\input\LTO_CCA_SV_Danube_Adj_v1.8.2_noshaspa.dss", "7.23.0_S1", 1)
s2 = Scenario(r"C:\jobs\20230426_LTO\modeling\LTO_Study_7.23.0_12av2_wsidi_danubeadjv1.8.2\DSS\input\LTO_CCA_SV_Danube_Adj_v1.8.2.dss", "7.23.0_S12aV2", 1)

date_map = pd.read_csv("constants/date_map.csv", index_col=0, parse_dates=True)

scenarios = (scenario for scenario in [s1, s2] if scenario.active == 1)

scen_dict = {}
for s in scenarios:
    if s.active == 1:
        scen_dict[s.alias] = s.pathname

print(scen_dict)


load_data_mult(scen_dict, var_dict, date_map)
