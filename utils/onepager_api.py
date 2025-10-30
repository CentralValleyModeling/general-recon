# import and common setups

import logging
import pandas as pd
import pandss as pdss
import numpy as np
import matplotlib.pyplot as plt
from functools import lru_cache
import yaml

# Inputting file
logging.basicConfig(level=logging.INFO)


def cfs_to_taf(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    periods = pd.PeriodIndex(data=df.index, freq="1M")
    days = periods.days_in_month

    df[col] = df[col] * days  # CFS/sec to CFS/Day
    df[col] = df[col] * (24 * 60 * 60)  # CFS/Day to CFS/sec
    df[col] = df[col] / 43_560  # CFS/sec to AF/sec
    df[col] = df[col] / 1000  # AF/sec to TAF/sec
    return df


def table_a(
    dss_obj: pdss.DSS,
    path_string_swp: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    df = None
    path_swp = pdss.DatasetPath.from_str(path_string_swp)

    with dss_obj:
        # Get the rts for the given path from the given dss object
        rts = dss_obj.read_rts(path_swp)

        # Convert rts to a dataframe
        df = rts.to_frame()

        # Rename the column to "VALUE"
        df.columns = ["VALUE"]

        # Convert the unit if necessary
        if rts.units.lower() == "cfs":
            df = cfs_to_taf(df, col="VALUE")
        # TODO: implement 12/9 multiplication

        # Create a mask for the data within the desired range of dates
        mask = (df.index >= start_date) & (df.index <= end_date)

        # Filter out any data that is not within the range indicated by the mask
        df = df.loc[mask]

    return df


def period_avg(
    calendar_year_df: pd.DataFrame, start_year: int = None, end_year: int = None
) -> tuple:
    # Filter out unnecessary years
    if start_year is not None and end_year is not None:
        start = pd.to_datetime(str(start_year) + "-12-31")
        end = pd.to_datetime(str(end_year) + "-12-31")

        mask = (calendar_year_df.index >= start) & (calendar_year_df.index <= end)
        calendar_year_df = calendar_year_df.loc[mask]

    # Calculate the annual average
    calendar_year_sum_avg = int(calendar_year_df["VALUE"].mean())
    calendar_year_sum_avg_percent = int((calendar_year_sum_avg / 4113) * 100)
    return (calendar_year_sum_avg, calendar_year_sum_avg_percent)


def rank_and_pick_year(df: pd.DataFrame, year_type: str) -> pd.DataFrame:
    df1 = df.copy(deep=True)
    if year_type == "Wet":
        df1 = df1.sort_values(by=["VALUE"], ascending=False)
    if year_type == "Dry":
        df1 = df1.sort_values(by=["VALUE"])
    return df1


def dryest_wettest_year(df: pd.DataFrame, rank: int) -> tuple:
    row = df.iloc[rank]
    val = int(row["VALUE"])
    percent = int((val / 4113) * 100)
    year = row.name.year

    return (year, val, percent)



def table_a_from_csv(
    df: pd.DataFrame,
    path_string_swp: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    # df1 = df.loc[df["Scenario"] == "AdjHist"]
    # df2 = df1["SWP_TA_TOTAL"]
    # return df2

    # Check the unit and convert if necessary
    # if rts.units.lower() == "cfs":
    #    df = cfs_to_taf(df, col=path_string_swp)

    # Create a mask for the data within the desired range of dates
    mask = (df.index >= start_date) & (df.index <= end_date)

    # Filter out any data that is not within the range indicated by the mask
    df = df.loc[mask]

    # We don't know the unit so just assuming that the conversion is needed
    df = cfs_to_taf(df, col="VALUE")

    # Rename the column containing the data to VALUE
    # df = df.rename(columns={path_string_swp : 'VALUE'})

    return df


deliveries2bpart = {
    "Table A":["SWP_TA_TOTAL", "SWP_CO_TOTAL", "SWP_TA_FEATH", "SWP_CO_FEATH"],
    "Article 21":["SWP_IN_TOTAL", "SWP_IN_FEATH"]
}

def read_run_to_structure_csv(df: pd.DataFrame, delivery_type = "Article 21", year_type = "Dry") -> dict:
    # Structure to return
    table = {}

    # DSS key path for timeseries
    # path_swp_list = ["SWP_TA_TOTAL", "SWP_CO_TOTAL", "SWP_TA_FEATH", "SWP_CO_FEATH"]
    path_swp_list = deliveries2bpart[delivery_type]

    # date range we are interested in
    start = pd.to_datetime("1921-10-01")
    end = pd.to_datetime("2021-09-30")

    frames: list[pd.DataFrame] = []

    for path_string_swp in path_swp_list:
        # Create a new dataframe with values only
        df1 = df[[path_string_swp]]
        df1 = df1.rename(columns={path_string_swp: "VALUE"})

        # Get the data frame for the given path
        df2 = table_a_from_csv(df1, path_string_swp, start, end)

        # Now add the dataframe to our list of frames
        frames.append(df2)

    # Now calculate- the timeseries for Table A
    if delivery_type == "Table A":
        df_A = frames[0] + frames[1]
        df_A = df_A - frames[2]
        df_A = df_A - frames[3]
    if delivery_type == 'Article 21':
        df_A = frames[0] - frames[1]
    # else:
    #     df_A = frames[0] - frames[1]
    

    # print(df_A)

    # Convert df from monthly to yearly
    calendar_year_df = df_A.resample(pd.offsets.YearEnd()).sum()
    print(calendar_year_df.head())


    # Column 1. long term average
    table["Long-term Average"] = period_avg(calendar_year_df)

    # Column 4: 2 year annual average from 1982-1983
    table["2-Year (1982-1983)"] = period_avg(calendar_year_df, 1982, 1983)

    # Column 5: 4 year annual average from 1982-1983
    table["4-Year (1980-1983)"] = period_avg(calendar_year_df, 1980, 1983)

    # Column 6: 6 year annual average from 1978-1983
    table["6-Year (1978-1983)"] = period_avg(calendar_year_df, 1978, 1983)

    # Column 7: 10 year annual average from 1978-1987
    table["10-Year (1978-1987)"] = period_avg(calendar_year_df, 1978, 1987)

    # Calculate the rank of calendar_year_df for wet
    ranked_df = rank_and_pick_year(calendar_year_df, year_type)


    # Column 2: Single Wettest Year (most)
    wettest_yr, wettest_val, wettest_perc = dryest_wettest_year(ranked_df, 0)
    # table["dry_wet_data_1"] = (wettest_val, wettest_perc)
    # table["dry_wet_label_1"] = f"Single {year_type} Year ({wettest_yr})"
    table[f"Single {year_type} Year ({wettest_yr})"] = (wettest_val, wettest_perc)

    # Column 3: Single Wettest Year (2nd most)
    wettest_yr, wettest_val, wettest_perc = dryest_wettest_year(ranked_df, 1)
    # table["dry_wet_data_2"] = (wettest_val, wettest_perc)
    # table["dry_wet_label_2"] = f"Single {year_type} Year ({wettest_yr})"
    table[f"Single {year_type} Year ({wettest_yr})"] = (wettest_val, wettest_perc)

    # Column 8: Single Wettest Year (3rd most)
    wettest_yr, wettest_val, wettest_perc = dryest_wettest_year(ranked_df, 2)
    # table["dry_wet_data_3"] = (wettest_val, wettest_perc)
    # table["dry_wet_label_3"] = f"Single {year_type} Year ({wettest_yr})"
    table[f"Single {year_type} Year ({wettest_yr})"] = (wettest_val, wettest_perc)

    return table


@lru_cache
def load_data(csv_filename: str):
    df = pd.read_csv(csv_filename, index_col=0, parse_dates=True)
    return df

@lru_cache
def read_all_runs_to_structure_csv(csv_filename: str, delivery_type, scen1, scen2) -> dict:
    # Create dataframe from the given file
    df = load_data(csv_filename)

    # Get the finalized df
    df_1 = df.loc[df["Scenario"] == scen1]
    df_2 = df.loc[df["Scenario"] == scen2]

    table_1 = read_run_to_structure_csv(df_1, delivery_type, "Dry")
    table_2 = read_run_to_structure_csv(df_1, delivery_type, "Wet")
    
    table_3 = read_run_to_structure_csv(df_2, delivery_type, "Dry")
    table_4 = read_run_to_structure_csv(df_2, delivery_type, "Wet")

    # Build the rows for dry year
    data = []
    for item in table_1.keys():
        val_1, perc_1 = table_1[item]
        val_2, perc_2 = table_3.get(item, (0, 0))
        row = ["Dry", item, val_1, perc_1, val_2, perc_2, val_2 - val_1]
        data.append(row)
    
    # Build the rows for wet year
    for item in table_2.keys():
        val_1, perc_1 = table_2[item]
        val_2, perc_2 = table_4.get(item, (0, 0))
        row = ["Wet", item, val_1, perc_1, val_2, perc_2, val_2 - val_1]
        data.append(row)

    # Create the df
    df_onepager = pd.DataFrame(
        data,
        columns=["YEAR_TYPE", "ITEM", "VAL_1", "PERC_1", "VAL_2", "PERC_2", "CHANGE"]
    )
    print("df_onepager =")
    print(df_onepager.head())

    return df_onepager

    # Read all the scenarios
    # scen_aliases = df.Scenario.unique()
    # combined_struct = dict()
    # for scenario in scen_list:
    #     print("processing scenario: ", scenario)
    #     # Get the df for the scenario
    #     df1 = df.loc[df["Scenario"] == scenario]

    #     # Dictionary for current table from the current file: key = table_1
    #     table = read_run_to_structure_csv(df1, delivery_type, year_type)

    #     # Add table_1 to combined_struct
    #     combined_struct[scenario] = table

    # return combined_struct


def read_run_to_structure(dss_filename: str) -> dict:
    # Structure to return
    table = {}

    # Create DSS object for the given file
    dss_object = pdss.DSS(dss_filename)

    # DSS key path for timeseries
    path_swp_list = [
        "/CALSIM/SWP_TA_TOTAL/SWP_DELIVERY/.*/1MON/L2020A/",
        "/CALSIM/SWP_CO_TOTAL/SWP_DELIVERY/.*/1MON/L2020A/",
        "/CALSIM/SWP_TA_FEATH/SWP_DELIVERY/.*/1MON/L2020A/",
        "/CALSIM/SWP_CO_FEATH/SWP_DELIVERY/.*/1MON/L2020A/",
    ]

    # date range we are interested in
    start = pd.to_datetime("1921-10-01")
    end = pd.to_datetime("2021-09-30")

    frames: list[pd.DataFrame] = []

    for path_string_swp in path_swp_list:
        # Get the data frame for the given path
        df = table_a(dss_object, path_string_swp, start, end)

        # Now add the dataframe to our list of frames
        frames.append(df)

    # Now calculate- the timeseries for Table A
    df_A = frames[0] + frames[1]
    df_A = df_A - frames[2]
    df_A = df_A - frames[3]
    # print(df_A)

    # Convert df from monthly to yearly
    calendar_year_df = df_A.resample(pd.offsets.YearEnd()).sum()

    # Column 1. long term average
    table["Long-term Average"] = period_avg(calendar_year_df)

    # Column 4: 2 year annual average from 1982-1983
    table["2-Year (1982-1983)"] = period_avg(calendar_year_df, 1982, 1983)

    # Column 5: 4 year annual average from 1982-1983
    table["4-Year (1980-1983)"] = period_avg(calendar_year_df, 1980, 1983)

    # Column 6: 6 year annual average from 1978-1983
    table["6-Year (1978-1983)"] = period_avg(calendar_year_df, 1978, 1983)

    # Column 7: 10 year annual average from 1978-1987
    table["10-Year (1978-1987)"] = period_avg(calendar_year_df, 1978, 1987)

    # Calculate the rank of calendar_year_df
    ranked_df_wet = rank_and_pick_year(calendar_year_df, "wet")

    # Column 2: Single Wettest Year (most)
    wettest_yr, wettest_val, wettest_perc = dryest_wettest_year(ranked_df_wet, 0)
    wettest_key = f"Single Wet Year ({wettest_yr})"
    table[wettest_key] = (wettest_val, wettest_perc)

    # Column 3: Single Wettest Year (2nd most)
    wettest_yr, wettest_val, wettest_perc = dryest_wettest_year(ranked_df_wet, 1)
    wettest_key = f"Single Wet Year ({wettest_yr})"
    table[wettest_key] = (wettest_val, wettest_perc)

    # Column 8: Single Wettest Year (3rd most)
    wettest_yr, wettest_val, wettest_perc = dryest_wettest_year(ranked_df_wet, 2)
    wettest_key = f"Single Wet Year ({wettest_yr})"
    table[wettest_key] = (wettest_val, wettest_perc)

    return table


def read_all_runs_to_structure_1(runs: dict[str, str]) -> dict:
    # Dictionary to represent the combined structure
    combined_struct = {}
    for name, path in runs.items():
        # Dictionary for current table from the current file: key = table_1
        table_1 = {}

        # Build the row_1 (Adjusted Historical) of table_1
        structure = read_run_to_structure(path)

        # Assign the Adjusted Historical structure to table_1
        table_1["Adjusted Historical (1922-2021)"] = structure

        # Calculate and assign the CC 50% structure to table_1
        # TODO: table_1['CC 50% (1922-2021)'] = ...

        # Calculate and assign the CC 75% structure to table_1
        # TODO: table_1['CC 75% (1922-2021)'] = ...

        # Calculate and assign the 95% structure to table_1
        # TODO: table_1['CC 95% (1922-2021)'] = ...

        # Add table_1 to combined_struct
        combined_struct["table_1"] = table_1

    return combined_struct


def read_all_runs_to_structure(runs: dict[str, str]) -> dict:
    # Dictionary to represent the combined structure
    combined_struct = {}
    for name, path in runs.items():
        # Dictionary for current table from the current file: key = table_1
        table_1 = {}

        # Build the row_1 (Adjusted Historical) of table_1
        structure = read_run_to_structure(path)

        # Assign the Adjusted Historical structure to table_1
        table_1["Adjusted Historical (1922-2021)"] = structure

        # Calculate and assign the CC 50% structure to table_1
        # TODO: table_1['CC 50% (1922-2021)'] = ...

        # Calculate and assign the CC 75% structure to table_1
        # TODO: table_1['CC 75% (1922-2021)'] = ...

        # Calculate and assign the 95% structure to table_1
        # TODO: table_1['CC 95% (1922-2021)'] = ...

        # Add table_1 to combined_struct
        combined_struct["table_1"] = table_1

    return combined_struct


def print_structure(combined_struct: dict[str, dict]) -> None:
    print(combined_struct)


if __name__ == "__main__":
    # # DSS filename to read
    # dss_filenames = {
    #     "hist": "2023DCR_Hist_DV.dss"
    # }
    # struct = read_all_runs_to_structure(dss_filenames)

    # # DEBUG
    # print_structure(struct)

    # TODO: hand the struct to a frontend
    # TODO: write the frontend

    # pseudo code below
    # structrure = {
    #    "table_1": {
    #        "dvr_2023_hist":{
    #            (1977, 1977): (wettest_val, wettest_perc)
    #        }
    #    }
    # }

    # value, percent = structrure['table_name']['dssname'][(1977, 1977)]

    csv_filename = "data\\dv_data.csv"
    # start = pd.to_datetime("1921-10-01")
    # end = pd.to_datetime("2021-09-30")
    # df = table_a_from_csv(csv_filename, start, end)
    # print(df.head())

    result = read_all_runs_to_structure_csv(csv_filename)
    for k, v in result.items():
        print(f"key = '{k}':")
        print(v)
