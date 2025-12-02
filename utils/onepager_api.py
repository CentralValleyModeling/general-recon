import logging
import pandas as pd
import pandss as pdss
import numpy as np
from functools import lru_cache
import yaml

# Inputting file
logging.basicConfig(level=logging.INFO)

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


def table_a_from_csv(
    df: pd.DataFrame,
    path_string_swp: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:

    # Create a mask for the data within the desired range of dates
    mask = (df.index >= start_date) & (df.index <= end_date)

    # Filter out any data that is not within the range indicated by the mask
    df = df.loc[mask]

    # We don't know the unit so just assuming that the conversion is needed
    df = cfs_to_taf(df, col="VALUE")

    return df


deliveries2bpart = {
    "Table A":["SWP_TA_TOTAL", "SWP_CO_TOTAL", "SWP_TA_FEATH", "SWP_CO_FEATH"],
    "Article 21":["SWP_IN_TOTAL", "SWP_IN_FEATH"]
}

def read_run_to_structure_csv(df: pd.DataFrame, delivery_type = "Article 21", period_type = "Dry Periods") -> dict:   
    # Structure to return
    table = {}

    # DSS key path for timeseries
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

    # Convert df from monthly to yearly
    calendar_year_df = df_A.resample(pd.offsets.YearEnd()).sum()
    print(calendar_year_df.head())

    # Read yaml file
    config = take_yaml("utils/op.yaml")
    period_info = config.get_period_info(period_type)
    for heading, start_year, end_year in period_info:
        table[heading] = period_avg(calendar_year_df, start_year, end_year)
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

    # Get the yaml config
    config = take_yaml("utils/op.yaml")

    # get the types
    period_types = config.get_period_types()

    data = []

    for period_type in period_types:
        table_1 = read_run_to_structure_csv(df_1, delivery_type, period_type)
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
    print("df_onepager =")
    print(df_onepager.head())

    return df_onepager
