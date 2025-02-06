import pandas as pd
import yaml

date_map = pd.read_csv("constants/date_map.csv", index_col=0, parse_dates=True)
df_dv_orig = pd.read_csv("data/dv_data.csv", index_col=0, parse_dates=True)
df_dv = pd.read_csv("data/dv_data.csv", index_col=0, parse_dates=True)
#df_dv = df_dv.apply(pd.to_numeric, errors='coerce')
#df_dv["Scenario"] = df_dv["Scenario"].astype(str)
scen_aliases = df_dv.Scenario.unique()
print(df_dv)

with open("constants/dvars.yaml", "r") as file:
    var_dict = yaml.safe_load(file)

# DV Derived Timeseries

df_dv["SWP_TA_CO_SOD"] = (
    df_dv["SWP_TA_TOTAL"]
    - df_dv["SWP_TA_FEATH"]
    + df_dv["SWP_CO_TOTAL"]
    - df_dv["SWP_CO_FEATH"]
)

df_dv["SWP_CO_SOD"] = df_dv["SWP_CO_TOTAL"] - df_dv["SWP_CO_FEATH"]

df_dv["EXPORTACTUALTDIF"] = df_dv["EXPORTACTUALTD"] - df_dv["EXPORTACTUALIF"]

var_dict["SWP_TA_CO_SOD"] = {
    "alias": "Total SWP Table and Carryover Delivery from the Delta",
    "bpart": "SWP_TA_CO_SOD",
    "pathname": None,
    "table_convert": "cfs_taf",
    "table_display": "wy",
    "type": "Delivery",
}

var_dict["SWP_CO_SOD"] = {
    "alias": "Total Carryover Delivery from the Delta",
    "bpart": "SWP_CO_SOD",
    "pathname": None,
    "table_convert": "cfs_taf",
    "table_display": "wy",
    "type": "Delivery",
}

var_dict["SWP_CO_SOD"] = {
    "alias": "Total Carryover Delivery from the Delta",
    "bpart": "SWP_CO_SOD",
    "pathname": None,
    "table_convert": "cfs_taf",
    "table_display": "wy",
    "type": "Delivery",
}


var_dict["EXPORTACTUALTDIF"] = {
    "alias": "Total Exports from the Delta",
    "bpart": "EXPORTACTUALTDIF",
    "pathname": None,
    "table_convert": "cfs_taf",
    "table_display": "wy",
    "type": "Export",
}

# Special logic for the DCR:
# The DCR reports calendar year average of 1921 - 2021, but the full range of data
# does not exist for CY 2021 This logic extends the dataset by three months by
# averaging the last nine months of data
# Consistent with how the DCR excel report tool does it
df_dv_extended = pd.DataFrame()
for s in df_dv["Scenario"].unique():
    start_date_1 = "2021-01-31 23:59:59"
    end_date_1 = "2021-09-30 23:59:59"
    new_date_range = pd.date_range(
        start="2021-10-31 23:59:59", end="2021-12-31 23:59:59", freq="ME"
    )

    scenario_df = pd.DataFrame()
    lastpartialyear = pd.DataFrame()
    date_range = pd.date_range(
        start="2021-01-31 23:59:59", end="2021-09-30 23:59:59", freq="ME"
    )

    scenario_df = df_dv.loc[df_dv["Scenario"] == s]
    scenario_df.index = pd.to_datetime(scenario_df.index)

    lastpartialyear = scenario_df.loc[
        (scenario_df.index >= start_date_1) & (scenario_df.index <= end_date_1)
    ]
    # This is the average of the last nine months:
    lastpartialyearavg = lastpartialyear.groupby(["Scenario"]).mean(numeric_only=True)

    extended_df = pd.concat(
        [lastpartialyearavg] * len(new_date_range), ignore_index=True
    )
    extended_df["Scenario"] = s
    extended_df.index = new_date_range
    scenario_df = pd.concat([scenario_df, extended_df])
    df_dv_extended = pd.concat([df_dv_extended, scenario_df])
df_dv_extended.update(date_map)

df_dv = pd.DataFrame(df_dv_extended)