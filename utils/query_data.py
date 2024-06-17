import pandas as pd
import yaml


date_map = pd.read_csv('constants/date_map.csv', index_col=0, parse_dates=True)
df = pd.read_csv('data/dv_data.csv', index_col=0, parse_dates=True)
scen_aliases = df.Scenario.unique()

with open('constants/dvars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)


df_sv = pd.read_csv('data/sv_data.csv', index_col=0, parse_dates=True)
with open('constants/svars.yaml', 'r') as file:
    svar_dict = yaml.safe_load(file)