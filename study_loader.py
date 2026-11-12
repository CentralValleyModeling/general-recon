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

    Study(r"C:\jobs\20230428_DCR23\models\9.3.1_danube_adj\DSS\output\DCR2023_DV_9.3.1_v2a_Danube_Adj_v1.8.dss",
          r"C:\jobs\20230428_DCR23\models\9.3.1_danube_adj\DSS\input\DCR2023_SV_Danube_Adj_v1.8.dss",
          "DCR23_Baseline", "DCR 2023", "Current", 1),

    Study(r"C:\jobs\20230428_DCR23\models\9.3.1_danube_cc50\DSS\output\DCR2023_DV_9.3.1_Danube_cc50_v1.8.dss",
          r"C:\jobs\20230428_DCR23\models\9.3.1_danube_cc50\DSS\input\DCR2023_SV_Danube_cc50_v1.8.dss",
          "DCR23_CC50", "DCR 2023", "2043_CC50", 1),

    Study(r"C:\jobs\20230428_DCR23\models\9.3.1_danube_cc75\DSS\output\DCR2023_DV_9.3.1_Danube_CC75_v1.8.dss",
          r"C:\jobs\20230428_DCR23\models\9.3.1_danube_cc75\DSS\input\DCR2023_SV_Danube_cc75_v1.8.dss",
          "DCR23_CC75", "DCR 2023", "2043_CC75", 1),

    Study(r"C:\jobs\20230428_DCR23\models\9.3.1_danube_cc95\DSS\output\DCR2023_DV_9.3.1_Danube_CC95_v1.8.dss",
          r"C:\jobs\20230428_DCR23\models\9.3.1_danube_cc95\DSS\input\DCR2023_SV_Danube_cc95_v1.8.dss",
          "DCR23_CC95", "DCR 2023", "2043_CC95", 1),

    Study(r"C:\jobs\2025_DCR25\models\1.5.3_yukon_adj\DSS\output\DCR2025_DV_1.5.3_Yukon_Adj_v1.6.dss",
          r"C:\jobs\2025_DCR25\models\1.5.3_yukon_adj\DSS\input\DCR2025_SV_Yukon_Adj_v1.6.dss",
          "DCR25_Baseline", "DCR 2025", "Current", 1),

    Study(r"C:\jobs\2025_DCR25\models\1.5.3_yukon_cc50\DSS\output\DCR2025_DV_1.5.3_Yukon_CC50_v1.6.dss",
          r"C:\jobs\2025_DCR25\models\1.5.3_yukon_cc50\DSS\input\DCR2025_SV_Yukon_CC50_v1.6.dss",
          "DCR25_CC50", "DCR 2025", "2045_CC50", 1),

      Study(r"C:\jobs\2025_DCR25\models\1.5.3_yukon_cc75\DSS\output\DCR2025_DV_1.5.3_Yukon_CC75_v1.6.dss",
          r"C:\jobs\2025_DCR25\models\1.5.3_yukon_cc75\DSS\input\DCR2025_SV_Yukon_CC75_v1.6.dss",
          "DCR25_CC75", "DCR 2025", "2045_CC75", 1),

    Study(r"C:\jobs\2025_DCR25\models\1.5.3_yukon_cc95\DSS\output\DCR2025_DV_1.5.3_Yukon_CC95_v1.6.dss",
          r"C:\jobs\2025_DCR25\models\1.5.3_yukon_cc95\DSS\input\DCR2025_SV_Yukon_CC95_v1.6.dss",
          "DCR25_CC95", "DCR 2025", "2045_CC95", 1)
]

date_map = pd.read_csv("constants/date_map.csv", index_col=0, parse_dates=True)

load_data(studies, var_dict_dv, date_map, "dv", "dv_data.csv")
load_data(studies, var_dict_sv, date_map, "sv", "sv_data.csv")
