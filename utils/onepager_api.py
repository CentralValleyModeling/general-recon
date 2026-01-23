import logging
import pandas as pd
import pandss as pdss
import numpy as np
from functools import lru_cache
import yaml
import math

# Inputting file
logging.basicConfig(level=logging.INFO)

@lru_cache
def get_scenarios(csv_filename):
    """Creates list of the different climate scenarios by getting the scenarios from TBD.

    Returns:
        list: List of the different unique climate scenarios.
    """
    df = load_data(csv_filename)
    return df["Scenario"].unique()

def take_yaml(filename):
    return YamlConfig(filename)

class YamlConfig:
    def __init__(self, filename):
        self.filename = filename
        self.period_info = {} # key = period_type, value = (start year, end year, heading)
        self.load_data()

    def get_period_info(self, period_type):
        return self.period_info.get(period_type, [])
    
    def get_period_types(self):
        return self.period_info.keys()

    def print(self):
        print("filename:", self.filename)
        print("period info:", self.period_info)

    def str_to_int(self, string):
        try:
            return int(string)
        except:
            return None

    def load_data(self):
        with open(self.filename, 'r') as file:
            yaml_data = yaml.safe_load(file)
            for key, data_list in yaml_data.items():
                for data in data_list:
                    heading = data['Heading']
                    year_range = data['YrRange']
                    period_type = data['Type']
                    start_year = None
                    end_year = None
                    if year_range:
                        years = year_range.split(',')
                        if len(years) == 2:
                            start_year = self.str_to_int(years[0])
                            end_year = self.str_to_int(years[1])
                        elif len(years) == 1:
                            start_year = self.str_to_int(years[0])
                    if period_type in self.period_info:
                        self.period_info[period_type].append((heading, start_year, end_year))
                    else:
                        self.period_info[period_type] = [(heading, start_year, end_year)]

                
def cfs_to_taf(df: pd.DataFrame) -> pd.DataFrame:
    df['VALUE'] = df['VALUE'] * df["cfs_taf"]
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
        # AZ
        calendar_year_df = calendar_year_df.loc[mask].copy()

    # Calculate the annual average (use rounding, not truncation)
    calendar_year_sum_avg = int(round(calendar_year_df["VALUE"].mean()))
    calendar_year_sum_avg_percent = int(round((calendar_year_sum_avg / 4113) * 100))
    return (calendar_year_sum_avg, calendar_year_sum_avg_percent)


def table_a_from_csv(
    df: pd.DataFrame,
    path_string_swp: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:

    # Create a mask for the data within the desired range of dates
    mask = (df.index >= start_date) & (df.index <= end_date)

    # Filter out any data that is not within the range indicated by the mask
    # AZ
    df = df.loc[mask].copy()

    # We don't know the unit so just assuming that the conversion is needed
    df = cfs_to_taf(df)

    return df


deliveries2bpart = {
    "Table A":["SWP_TA_TOTAL", "SWP_CO_TOTAL", "SWP_TA_FEATH", "SWP_CO_FEATH"],
    "Article 21":["SWP_IN_TOTAL"]
}

import datetime
import time
def annual_delivery_by_type(df: pd.DataFrame, delivery_type = "Article 21") -> pd.DataFrame:
    # DSS key path for timeseries
    path_swp_list = deliveries2bpart[delivery_type]

    # date range we are interested in (YYYY-MM-DD)
    start = pd.to_datetime("1922-01-01")
    end = pd.to_datetime("2021-12-31")

    frames: list[pd.DataFrame] = []

    for path_string_swp in path_swp_list:
        # Create a new dataframe with values only
        df1 = df[[path_string_swp, 'cfs_taf']].copy()
        df1 = df1.rename(columns={path_string_swp: "VALUE"})

        # Get the data frame for the given path
        df2 = table_a_from_csv(df1, path_string_swp, start, end)
        df2.drop(columns=['cfs_taf'], inplace=True)
        print(f"annual_delivery_by_type(delivery_type = {delivery_type}): path_string_swp = {path_string_swp}, df2.head():\n", df2.head(15))    

        # Now add the dataframe to our list of frames
        frames.append(df2)

    # Now calculate- the timeseries for Table A
    if delivery_type == "Table A":
        df_A = frames[0] + frames[1]
        df_A = df_A - frames[2]
        df_A = df_A - frames[3]
    if delivery_type == 'Article 21':
        df_A = frames[0]

        # 2003 and 2015 Jan-Dec deliveries are calculated by taking the
        # average of Jan-Sep deliveries and multiplying by 12
        # Filter out rows matching the year and month
        # indexes_to_remove = [
        #     pd.to_datetime("2003-10-31 23:59:59"),
        #     pd.to_datetime("2003-11-30 23:59:59"),
        #     pd.to_datetime("2003-12-31 23:59:59"),
        #     pd.to_datetime("2015-10-31 23:59:59"),
        #     pd.to_datetime("2015-11-30 23:59:59"),
        #     pd.to_datetime("2015-12-31 23:59:59")
        # ]
        # df_A = df_A.drop(index=indexes_to_remove)


    # print(f"annual_delivery_by_type(delivery_type = {delivery_type}): 1 df_A.head():\n", df_A.head(15))

    calendar_year_df = df_A.resample(pd.offsets.YearEnd()).agg(VALUE = ('VALUE', 'sum'), COUNT = ('VALUE', 'count'))
    # print(f"annual_delivery_by_type(delivery_type = {delivery_type}): 2 calendar_year_df.head():\n", calendar_year_df.head(100))

    calendar_year_df['VALUE'] = calendar_year_df['VALUE'] * (12.0 / calendar_year_df['COUNT'])


    return calendar_year_df


def read_run_to_structure_csv(df: pd.DataFrame, delivery_type = "Article 21", period_type = "Dry Periods") -> dict:   
    print(f"read_run_to_structure_csv(delivery_type = {delivery_type}, period_type = {period_type}):")
    
    # Structure to return
    table = {}

    calendar_year_df = annual_delivery_by_type(df, delivery_type)
    # DEBUG
    # calendar_year_df.to_csv(f"auhona_caldf_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    # time.sleep(1)
    
    # Read yaml file
    config = take_yaml("utils/op.yaml")
    period_info = config.get_period_info(period_type)
    for heading, start_year, end_year in period_info:
        # print(f"read_run_to_structure_csv: {heading}: {start_year}- {end_year}")
        table[heading] = period_avg(calendar_year_df, start_year, end_year)
    return table


@lru_cache
def load_data(csv_filename: str):
    df = pd.read_csv(csv_filename, index_col=0, parse_dates=True)
    return df

def build_likelihood_by_taf(csv_filename: str, delivery_type, scen1, scen2) -> pd.DataFrame:
    # Create dataframe from the given file
    df = load_data(csv_filename)

    final_df_list = []
    for scen in [scen1, scen2]:
        df_1 = annual_delivery_by_type(df.loc[df["Scenario"] == scen], delivery_type)
        df_1 = df_1.sort_values(by="VALUE", ascending=False)
        # print(f"df_1 for {scen} =\n", df_1.head())

        # Create a dataframe for the final output
        df_2 = pd.DataFrame({
            "RANGE": ["0-20", "20-100", "100-200", "200-300", "300-400", "400-500", "500-600", "600-700", "More than 700"], 
            "SCENARIO": [scen] * 9, 
            "FREQ": [0] * 9, 
            "LIKELIHOOD": [0] * 9
        })

        for index, row in df_1.iterrows():
            val = row["VALUE"]
            if val < 20:
                df_2.loc[0, "FREQ"] += 1
            elif val < 100:
                df_2.loc[1, "FREQ"] += 1
            elif val < 200:
                df_2.loc[2, "FREQ"] += 1    
            elif val < 300:
                df_2.loc[3, "FREQ"] += 1
            elif val < 400:
                df_2.loc[4, "FREQ"] += 1
            elif val < 500:
                df_2.loc[5, "FREQ"] += 1
            elif val < 600:
                df_2.loc[6, "FREQ"] += 1
            elif val < 700:
                df_2.loc[7, "FREQ"] += 1    
            else:
                df_2.loc[8, "FREQ"] += 1

        freq_sum = sum(df_2["FREQ"])
        if freq_sum != 0:
            df_2["LIKELIHOOD"] = df_2["FREQ"] / freq_sum
            df_2["LIKELIHOOD"] = df_2["LIKELIHOOD"] * 100
            df_2["LIKELIHOOD"] = df_2["LIKELIHOOD"].round(0).astype(int)

        final_df_list.append(df_2)
    return pd.concat(final_df_list, axis=0, ignore_index=True)


@lru_cache
def read_all_runs_to_structure_csv(csv_filename: str, delivery_type, scen1, scen2) -> dict:
    # Create dataframe from the given file
    df = load_data(csv_filename)

    # Get the finalized df
    df_1 = df.loc[df["Scenario"] == scen1]
    df_2 = df.loc[df["Scenario"] == scen2]

    # DEBUG
    # df_2.to_csv(f"auhona_{scen2}_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    # time.sleep(1)

    print(f"read_all_runs_to_structure_csv(): scen2 = {scen2}, df_2.head():\n", df_2.head(100))

    # Get the yaml config
    config = take_yaml("utils/op.yaml")

    # get the types
    period_types = config.get_period_types()

    data = []

    for period_type in period_types:
        print(f"read_all_runs_to_structure_csv(): scen1 = {scen1}, period_type = {period_type}")
        table_1 = read_run_to_structure_csv(df_1, delivery_type, period_type)

        print(f"read_all_runs_to_structure_csv(): scen2 = {scen2}, period_type = {period_type}")
        table_2 = read_run_to_structure_csv(df_2, delivery_type, period_type)

        # Build the rows for dry year
        for item in table_1.keys():
            val_1, perc_1 = table_1[item]
            val_2, perc_2 = table_2[item]
            row = [period_type, item, val_1, perc_1, val_2, perc_2, val_2 - val_1]
            data.append(row)

    # Create the df
    df_onepager = pd.DataFrame(
        data,
        columns=["YEAR_TYPE", "ITEM", "VAL_1", "PERC_1", "VAL_2", "PERC_2", "CHANGE"]
    )

    return df_onepager
