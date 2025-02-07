from collections import namedtuple

import pandas as pd
import yaml
from utils import list_files, load_data_mult, load_data
from pathlib import Path

# Scenario management
Study = namedtuple("Scenario", ["dv_path", "sv_path", "alias", "assumptions", "climate", "color"])



with open("constants/dvars.yaml", "r") as file:
    var_dict_dv = yaml.safe_load(file)
with open("constants/svars.yaml", "r") as file:
    var_dict_sv = yaml.safe_load(file)
with open("study_ledger.yaml", "r") as file:
    study_ledger = yaml.safe_load(file)

studies = [

    Study(r"dss_files\CCA1_v3.7.0__Baseline_LU100_SLR0_20241219",
          "",
          "CCA1", "Baseline", "Historical", 1),



    Study(r"dss_files\CCA2_v3.7.0_BE_2043_50CC_LU100_SLR15_20241218.dss",
          "",
          "CCA2", "Degradation", "2043_CC50", 1),

    Study(r"dss_files\CCA4_v3.7.0__2043_50CC_LU100_SLR15_20241220.dss",
          "",
          "CCA4", "Maintain", "2043_CC50", 1),

    Study(r"dss_files\CCA8_v3.7.0_D_2043_50CC_LU100_SLR15_20241223.dss",
          "",
          "CCA8", "FIRO", "2043_CC50", 1),  

    Study(r"dss_files\CCA10_v3.7.0_C_2043_50CC_LU100_SLR15_20241226.dss",
          "",
          "CCA10", "SOD Storage", "2043_CC50", 1),

    Study(r"dss_files\CCA12_v3.7.0_ACD_2043_50CC_LU100_SLR15_20241226.dss",
          "",
          "CCA12", "Combo", "2043_CC50", 1),



    Study(r"dss_files\CCA3_v3.7.0_BE_2043_95CC_LU100_SLR30_20241220.dss",
          "",
          "CCA3", "Degradation", "2043_CC95", 1),

    Study(r"dss_files\CCA5_v3.7.0__2043_95CC_LU100_SLR30_20241227.dss",
          "",
          "CCA5", "Maintain", "2043_CC95", 1),

    Study(r"dss_files\CCA7_v3.7.0_A_2043_95CC_LU100_SLR30_20241222.dss",
          "",
          "CCA7", "DCP", "2043_CC95", 1),

    Study(r"dss_files\CCA9_v3.7.0_D_2043_95CC_LU100_SLR30_20241223.dss",
          "",
          "CCA9", "FIRO", "2043_CC95", 1),  

    Study(r"dss_files\CCA11_v3.7.0_C_2043_95CC_LU100_SLR30_20241226.dss",
          "",
          "CCA11", "SOD Storage", "2043_CC95", 1),

    Study(r"dss_files\CCA13_v3.7.0_ACD_2043_95CC_LU100_SLR30_20241226.dss",
          "",
          "CCA13", "Combo", "2043_CC95", 1),
]

date_map = pd.read_csv("constants/date_map.csv", index_col=0, parse_dates=True)

load_data(studies, var_dict_dv, date_map, "dv", "dv_data.csv")