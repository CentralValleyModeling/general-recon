from collections import namedtuple

import pandas as pd
import yaml
from utils import list_files, load_data_mult, load_data
from pathlib import Path

# Scenario management
Study = namedtuple("Scenario", ["dv_path", "sv_path", "alias", "assumptions", "climate", "active"])



with open("constants/dvars.yaml", "r") as file:
    var_dict_dv = yaml.safe_load(file)
with open("constants/svars.yaml", "r") as file:
    var_dict_sv = yaml.safe_load(file)
with open("study_ledger.yaml", "r") as file:
    study_ledger = yaml.safe_load(file)

studies = [
    Study(r"dss_files\CCA1_v3.7.0__Baseline_LU100_SLR0_20241219",
          r"dss_files\CS3_2022MED_03102024_L2020A_LTO_NAA_SV.dss",
          "CCA0", "Current_Infrastructure", "Existing_Climate", 1),

    Study(r"dss_files\CCA1_v3.7.0__Baseline_LU100_SLR0_20241219",
          r"dss_files\CS3_2022MED_03102024_L2020A_LTO_NAA_SV.dss",
          "CCA1", "Degradation", "2043_CC50", 1),

    Study(r"dss_files\CCA4_v3.7.0__2043_50CC_LU100_SLR15_20241220.dss",
          r"dss_files\CS3_2022MED_03102024_L2020A_LTO_NAA_SV.dss",
          "CCA4", "Maintain", "2043_CC50", 1)
]

date_map = pd.read_csv("constants/date_map.csv", index_col=0, parse_dates=True)

load_data(studies, var_dict_dv, date_map, "dv_data_test.csv")

# Load SV
#load_data_mult(scen_dict_sv, var_dict_sv, date_map, "sv_data.csv")
