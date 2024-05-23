import pandas as pd
import yaml

df = pd.read_csv('data/temp.csv', index_col=0, parse_dates=True)
date_map = pd.read_csv('constants/date_map.csv', index_col=0, parse_dates=True)
scen_aliases = df.Scenario.unique()

with open('constants/vars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)