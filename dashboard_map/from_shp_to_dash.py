import sys
import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import pyproj
import pandas as pd
import plotly.graph_objects as go
import yaml
from functools import lru_cache
import shapely.geometry
import numpy as np

sys.path.append(".")
import utils.query_data as qd
from pages.styles import PLOT_COLORS, ASSUMPTION_ORDER, ASSUMPTION_COLORS
from utils.tools import monthfilter, month_list, cfs_taf, convert_cm_nums

import time
import functools

def log_execution_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed:.4f} seconds")
        return result
    return wrapper


swp2convention = {
    "SWP_TA_AVEK": "SWC_AVEKWA",
    "SWP_TA_CVWD": "SWC_CVWD",
    "SWP_TA_CLA": "SWC_CLAWA",
    "SWP_TA_DESERT": "SWC_DWA",
    "SWP_TA_DUDLEY": "SWC_DRWD",
    "SWP_TA_EMPIRE": "SWC_EWSID",
    "SWP_TA_KERNMI": "SWC_KCWA",
    "SWP_TA_KERNAG": "SWC_KCWA",
    "SWP_TA_KINGS": "SWC_KGCC",
    "SWP_TA_LCID": "SWC_LCID",
    "SWP_TA_MWD": "SWC_MWDSC",
    "SWP_TA_MWA": "SWC_MWA",
    "SWP_TA_PWD": "SWC_PWD",
    "SWP_TA_SBV": "SWC_SBVMWD",
    "SWP_TA_SGV": "SWC_SGVMWD",
    "SWP_TA_SGP": "SWC_SGPWA",
    "SWP_TA_SLO": "SWC_SLOCFCWCD",
    "SWP_TA_SB": "SWC_SBCFCWCD",
    "SWP_TA_SCV": "SWC_SCVWD",
    "SWP_TA_CLWA1": "SWC_SCVWA",
    "SWP_TA_CLWA2": "SWC_SCVWA",
    "SWP_TA_TULARE": "SWC_TLBWSD",
    "SWP_TA_VC": "SWC_VCWPD",
    "SWP_TA_ACFC": "SWC_ACFCWCDZ7",
}


agencyname2convention = {
    "Antelope Valley - East Kern Water Agency": "SWC_AVEKWA",
    "Coachella Valley Water District": "SWC_CVWD",
    "Crestline - Lake Arrowhead Water Agency": "SWC_CLAWA",
    "Desert Water Agency": "SWC_DWA",
    "Dudley Ridge Water District": "SWC_DRWD",
    "Empire West Side Irrigation District": "SWC_EWSID",
    "Kern County Water Agency": "SWC_KCWA",
    "Kings County": "SWC_KGCC",
    "Littlerock Creek Irrigation District": "SWC_LCID",
    "Metropolitan Water District Of Southern California": "SWC_MWDSC",
    "Mojave Water Agency": "SWC_MWA",
    "Palmdale Water District": "SWC_PWD",
    "San Bernardino Valley Municipal Water District": "SWC_SBVMWD",
    "San Gabriel Valley Municipal Water District": "SWC_SGVMWD",
    "San Gabriel Valley Municipal  Water District": "SWC_SGVMWD",
    "San Gorgonio Pass Water Agency": "SWC_SGPWA",
    "San Luis Obispo County Flood Control And Water Conservation District": "SWC_SLOCFCWCD",
    "Santa Barbara County Flood Control and Water Conservation District": "SWC_SBCFCWCD",
    "Santa Clarita Valley Water Agency": "SWC_SCVWA",
    "Tulare Lake Basin Water Storage District": "SWC_TLBWSD",
    "Ventura County Watershed Protection District": "SWC_VCWPD",
}


name2tablename = {
    "Lake Shasta": "Shasta Storage",
    "Trinity Lake": "Trinity Storage",
    "Folsom Lake": "Folsom Storage",
    "Lake Oroville": "Oroville Storage",
    "San Luis Reservoir": "San Luis Storage",
}


tablename2calsimname = {
    "Shasta Storage": "S_SHSTA",
    "Trinity Storage": "S_TRNTY",
    "Folsom Storage": "S_FOLSM",
    "Oroville Storage": "S_OROVL",
    "San Luis Storage": "S_SLUIS_SWP",  # this is for SWP, not CVP
}


swp2description = {
    "SWP_TA_AVEK": "Antelope Valley-East Kern WA",
    "SWP_TA_CVWD": "Coachella Valley WD",
    "SWP_TA_CLA": "Crestline-Line Arrowhead WA",
    "SWP_TA_DESERT": "Desert WA",
    "SWP_TA_DUDLEY": "Dudley Ridge WD",
    "SWP_TA_EMPIRE": "Empire West Side ID",
    "SWP_TA_KERNMI": "Kern County WA (MI)",
    "SWP_TA_KERNAG": "Kern County WA (Ag)",
    "SWP_TA_KINGS": "County of Kings",
    "SWP_TA_LCID": "Littlerock Creek ID",
    "SWP_TA_MWD": "Metropolitan WDSC",
    "SWP_TA_MWA": "Mojave WA",
    "SWP_TA_PWD": "Palmdale WD",
    "SWP_TA_SBV": "San Bernadino Valley MWD",
    "SWP_TA_SGV": "San Gabriel Valley MWD",
    "SWP_TA_SGP": "San Gorgonio Pass WA",
    "SWP_TA_SLO": "San Luis Obispo County FC&WCD",
    "SWP_TA_SB": "Santa Barbara County FC&WCD",
    "SWP_TA_SCV": "Santa Clara Valley WD",
    "SWP_TA_CLWA1": "Santa Clarita WA (San Joaquin)",
    "SWP_TA_CLWA2": "Santa Clarita WA (South Coast)",
    "SWP_TA_TULARE": "Tulare Lake Basin WSD",
    "SWP_TA_VC": "Ventura County FCD",
    "SWP_TA_ACFC": "Alameda County FC&WCD, Zone 7",
}


def create_pool2bpart_map():
    """Maps alias name to corresponding bpart for the pools.

    Returns:
        dict: Python dictionary mapping alias name to bpart name for the pools on the map.
    """
    pool2bpart = {}
    with open("dashboard_map/dvars.yaml", "r") as file:
        var_dict = yaml.safe_load(file)
        for key, val in var_dict.items():
            alias = val['alias']
            if alias.startswith("Pool"):
                pool2bpart[alias] = val['bpart']
    return pool2bpart

pool2bpart = create_pool2bpart_map()


@lru_cache
def calc_mean():
    """Calculates the average annual sum for each scenario.

    Returns:
        pd.DataFrame: Average annual sum and associated metadata as a pandas DataFrame.
    """
    combined_df = pd.DataFrame(
        columns=["Scenario", "CONTRACTOR_CONVENTION", "icy", "VAL"]
    )

    for code in swp2convention:
        # Create a dataframe using the Scenario and code from df_dv
        df = qd.df_dv[["Scenario", "icy", code, "cfs_taf"]].copy()

        # Convert cfs to taf and drop cfs_taf column
        df[code] = df[code] * df["cfs_taf"]
        df = df.drop(columns=["cfs_taf"])

        # Rename code column to "VAL"
        df.rename(columns={code: "VAL"}, inplace=True)

        # Add contractor convention
        contractor_convention = swp2convention[code]
        df["CONTRACTOR_CONVENTION"] = contractor_convention

        # Concatenate data for this agency to the combined df
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Calculate sum of val for Scenario, Agency name, and water year
    combined_df = combined_df.groupby(
        ["Scenario", "CONTRACTOR_CONVENTION", "icy"]  # change to icy
    ).sum()

    # Remove iwy column
    combined_df = combined_df.reset_index()
    combined_df = combined_df.drop(columns=["icy"])

    # Calculate mean
    combined_df = combined_df.groupby(["Scenario", "CONTRACTOR_CONVENTION"]).mean()

    # Reset the index
    combined_df = combined_df.reset_index()

    # Round
    combined_df["VAL"] = combined_df["VAL"].round()
    combined_df["VAL"] = combined_df["VAL"].astype(int)

    # add bpart
    combined_df["BPART"] = "TBD"
    combined_df["BPART_SUFFIX"] = "TBD"
    for key, val in swp2convention.items():
        combined_df.loc[combined_df["CONTRACTOR_CONVENTION"] == val, "BPART"] = key

        # Add suffix of bpart for display
        combined_df.loc[combined_df["CONTRACTOR_CONVENTION"] == val, "BPART_SUFFIX"] = (
            key[7:]
        )

    # Return the dataframe containing the average annual sum
    return combined_df


def area_from_geodf(geodf: gpd.GeoDataFrame):
    """Calculates the area of each geometric shape in the given GeoDataFrame.

    Args:
        geodf (gpd.GeoDataFrame): The GeoDataFrame containing the shapes.

    Returns:
        gpd.GeoDataFrame: A new GeoDataFrame containing the areas under a column named AREA.
    """
    area_df = geodf.geometry.to_crs(epsg=32618)
    area_projected = area_df.geometry.area

    # create a new geodf to get the area
    area_geodf = geodf.copy()

    # Create the area column
    # area_geodf["AREA"] = geodf["geometry"].area
    area_geodf["AREA"] = area_projected

    # Return the new column
    return area_geodf["AREA"]


@lru_cache
def load_shp_contractors() -> gpd.GeoDataFrame:
    """Converts the shapefile into a GeoDataFrame for the contractors. Add columns for the CONTRACTOR_CONVENTION,
      AGENCYNAME, AREA, and RANK to the geodf.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame for the contractors.
    """
    geodf = gpd.read_file("assets/qgis/SWP_Contractors.shp")
    geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    # Add a column for conventions to geodf
    geodf["CONTRACTOR_CONVENTION"] = "TBD"

    # Using the agencyname2convention map, update CONTRACTOR_CONVENTION column val for each row
    for name in geodf["AGENCYNAME"]:
        # Get the contractor convention for the agency name
        convention = agencyname2convention[name]

        # Update the convention of the row
        geodf.loc[geodf["AGENCYNAME"] == name, "CONTRACTOR_CONVENTION"] = convention

    # Add area to the geodf
    geodf["AREA"] = area_from_geodf(geodf)

    # Add rank column based on area
    # geodf = geodf.dropna()
    geodf["RANK"] = geodf["AREA"].rank(method="first").fillna(0).astype(int)

    # geodf = geodf[geodf["BPART"].isin(qd.df_dv.columns)]

    return geodf


def load_shp_reservoir() -> gpd.GeoDataFrame:
    """Converts the shapefile into a GeoDataFrame for the reservoirs. Add columns for TABLENAME, CALSIMNAME, and DATA_TYPE to the geodf.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame for the reservoirs.
    """
    geodf = gpd.read_file("assets/qgis/calsim_lakes_for_visualization.shp")
    geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    # filter out uneccesary reservoirs
    geodf = geodf[geodf["NAME"].isin(name2tablename)]

    # add columns for table name and calsim name
    geodf["TABLENAME"] = "TBD"
    for key, val in name2tablename.items():
        geodf.loc[geodf["NAME"] == key, "TABLENAME"] = val

    geodf["CALSIMNAME"] = "TBD"
    for key, val in tablename2calsimname.items():
        geodf.loc[geodf["TABLENAME"] == key, "CALSIMNAME"] = val
    
    geodf["DATA_TYPE"] = "RESERVOIRS"

    # set index
    geodf = geodf.reset_index()
    geodf = geodf.set_index("DFGWATERID")

    return geodf


arc_id2bpart = {
    "C_CAA003": "C_CAA003",
    "C_DMC003": "C_DMC000"
}


arc_id2alias = {
    "C_CAA003": "Total Banks Exports",
    "C_DMC003": "Total Jones Exports"
}


def load_shp_export() -> gpd.GeoDataFrame:
    """Converts the shapefile into a GeoDataFrame for the exports. Add columns for BPART, ALIAS, and DATA_TYPE to the geodf.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame for the exports.
    """
    geodf = gpd.read_file("assets/qgis/main_exports.shp")
    geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    # filter for ARC_ID = C_CAA003, C_DMC000
    geodf = geodf[geodf["Arc_ID"].isin(["C_CAA003", "C_DMC003"])]

    # bpart column
    geodf["BPART"] = "TBD"
    for key, val in arc_id2bpart.items():
        geodf.loc[geodf["Arc_ID"] == key, "BPART"] = val

     # alias column
    geodf["ALIAS"] = "TBD"
    for key, val in arc_id2alias.items():
        geodf.loc[geodf["Arc_ID"] == key, "ALIAS"] = val

    geodf = geodf[geodf["BPART"].isin(qd.df_dv.columns)]
    
    geodf["DATA_TYPE"] = "EXPORTS"

    return geodf


arc_id2bpart_up = {
    "C_LWSTN": "C_LWSTN",
    "D_LWSTN_CCT011": "D_LWSTN_CCT011",
    "C_WKYTN": "C_WKYTN",
    "C_KSWCK": "C_KSWCK",
    "C_SAC097": "C_SAC097",
    "C_FTR059": "C_FTR059",
    "C_FTR003": "C_FTR003",
    "C_YUB006": "C_YUB006",
    "C_SAC083": "C_SAC083",
    "C_NTOMA": "C_NTOMA",
    "C_AMR004": "C_AMR004"
}


arc_id2alias_up = {
    "C_LWSTN": "Trinity Release",
    "D_LWSTN_CCT011": "Trinity Export",
    "C_WKYTN": "Clear Creek below Whiskeytown",
    "C_KSWCK": "Release - Sacramento at Keswick",
    "C_SAC097": "Sac R. Flow at Wilkins Slough",
    "C_FTR059": "Feather below Thermalito",
    "C_FTR003": "Feather Mouth",
    "C_YUB006": "Yuba River at Marysville",
    "C_SAC083": "Sac R. Flow at Verona",
    "C_NTOMA": "Release-American Nimbus",
    "C_AMR004": "American River at H-Street"
}


def load_shp_upstream_flows() -> gpd.GeoDataFrame:
    """Converts the shapefile into a GeoDataFrame for the upstream flows. Add columns for BPART, ALIAS, and DATA_TYPE to the geodf.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame for the upstream flows.
    """
    geodf = gpd.read_file("assets/qgis/upstream_flows.shp")
    geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    # filter for ARC_ID = C_CAA003, C_DMC000
    geodf = geodf[geodf["Arc_ID"].isin([
        "C_LWSTN", 
        "D_LWSTN_CCT011", 
        "C_WKYTN", 
        "C_KSWCK", 
        "C_SAC097", 
        "C_FTR059", 
        "C_FTR003", 
        "C_YUB006",
        "C_SAC083",
        "C_NTOMA",
        "C_AMR004"
        ])]

    # bpart column
    geodf["BPART"] = "TBD"
    for key, val in arc_id2bpart_up.items():
        geodf.loc[geodf["Arc_ID"] == key, "BPART"] = val

     # alias column
    geodf["ALIAS"] = "TBD"
    for key, val in arc_id2alias_up.items():
        geodf.loc[geodf["Arc_ID"] == key, "ALIAS"] = val
    
    geodf = geodf[geodf["BPART"].isin(qd.df_dv.columns)]
    
    geodf["DATA_TYPE"] = "UP_FLOWS"

    return geodf


def load_shp_pool() -> gpd.GeoDataFrame:
    """Converts the shapefile into a GeoDataFrame for the pools. Add columns for BPART, AssetReg_2, and DATA_TYPE to the geodf.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame for the pools.
    """
    geodf = gpd.read_file("assets/qgis/caa_pools.shp")
    geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    # bpart column
    geodf["BPART"] = ""
    for key, val in pool2bpart.items():
        geodf.loc[geodf["AssetReg_2"] == key, "BPART"] = val

    geodf = geodf[geodf["BPART"] != ""]

    geodf = geodf[geodf["BPART"].isin(qd.df_dv.columns)]
    
    geodf["DATA_TYPE"] = "POOL"

    return geodf


@lru_cache
def create_ca_plot():
    """Creates choropleth plot of California State Border.

    Returns:
        plotly.graph_objects.Figure: Plotly figure of California State Border.
    """
    # read shapefile for california state boundary
    # downloaded from https://data.ca.gov/dataset/ca-geographic-boundaries
    geodf = gpd.read_file("assets/qgis/CA_State.shp")
    geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    figca = px.choropleth_mapbox(
        geodf,
        geojson=geodf.geometry,
        locations=geodf.index,
        color_discrete_sequence=["rgba(255, 255, 255, 0)"]
    )

    figca.update_traces(
        showlegend=False,
        hoverinfo="skip",
        hovertemplate=None
    )

    return figca


@lru_cache
def create_contractor_plot(scen1, scen2):
    """Creates choropleth plot of SWP Contractors with each contractor having hoverdata displaying the contractor convention, 
      agency name, and difference of the average annual sum of the first climate scenario minus the second climate scenario.

    Args:
        scen1 (str): First climate scenario.
        scen2 (str): Second climate scenario.

    Returns:
        plotly.graph_objects.Figure: Plotly figure for the SWP contractors.
    """
    geodf = load_shp('contractors')
    data_df = calc_mean()
    scen_geodf = create_df_for_scen(data_df, geodf, scen1, scen2)

    # Set the index to match the original geodf for proper geometry alignment
    scen_geodf = scen_geodf.set_index(geodf.index)

    fig = px.choropleth_mapbox(
        scen_geodf,
        geojson=scen_geodf.geometry,
        locations=scen_geodf.index,
        custom_data=[
            "BPART",
            "VAL_DIFF",
            "VAL_PERC",
            "AGENCYNAME",
            "CONTRACTOR_CONVENTION",
            "DATA_TYPE"
        ],
        color="VAL_PERC",
        labels={"color": "VAL DIFF %"},
    )

    my_hovertemplate = "<b>%{customdata[4]}<br>AGENCYNAME=%{customdata[3]}</b><br><br>VAL_DIFF=%{customdata[1]}<br>VAL_PERC=%{z}<extra></extra>"
    fig.update_traces(
        hovertemplate=my_hovertemplate, 
        marker={"opacity": 0.7}
    )

    return fig


@lru_cache
def create_del_outflows_centroid():
    """Creates centroid plot for the delta outflow at Martinez with hoverdata displaying the delta outflow bpart 'NDOI'.

    Returns:
         plotly.graph_objects.Scatter: Plotly centroid figure of delta outflow at Martinez.
    """
    data = {
        'BPART': ['NDOI'],
        'lat': [37.997417],
        'lon': [-122.133598],
        'DATA_TYPE': ['FLOWS']
    }

    df = pd.DataFrame(data)
    
    my_hovertemplate = "<b>%{customdata[0]}</b><extra></extra>"
    fig1 = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        custom_data= ["BPART", "DATA_TYPE"]
    )

    fig1.update_traces(
        textposition='middle center', 
        hovertemplate=my_hovertemplate, 
        showlegend=False,
        mode='markers',
        marker=dict(size=15, color='rgb(0, 93, 131)', symbol="circle")
    )

    fig1.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')

    return fig1


@lru_cache
def create_contractor_centroid(scen1, scen2):
    """Creates centroid plot for the SWP Contractors with hoverdata displaying the CONTRACTOR_CONVENTION, BPART, water delivery average annual sum
    difference, and water delivery average annual sum difference percentage, for each contractor. 

    Args:
        scen1 (str): First climate scenario.
        scen2 (str): Second climate scenario.

    Returns:
        plotly.graph_objects.Scatter: Plotly centroid figure of SWP Contractors.
    """
    geodf = load_shp('contractors')
    data_df = calc_mean()
    scen_geodf = create_df_for_scen(data_df, geodf, scen1, scen2)

    # Set the index to match the original geodf for proper geometry alignment
    scen_geodf = scen_geodf.set_index(geodf.index)

    centroid_df = scen_geodf.geometry.to_crs(epsg=32618)
    centroid_projected = centroid_df.geometry.centroid
    centroid_geographic = centroid_projected.to_crs(epsg=4326)

    hoverdf = scen_geodf[
        ["BPART", "CONTRACTOR_CONVENTION", "AGENCYNAME", "VAL_DIFF", "VAL_PERC", "DATA_TYPE"]
    ].copy()
    my_hovertemplate = "<b>%{customdata[1]}<br>AGENCYNAME=%{customdata[2]}</b><br><br>VAL_DIFF=%{customdata[3]}<br>VAL_PERC=%{customdata[4]}<extra></extra>"
    fig1 = px.scatter_mapbox(
        scen_geodf,
        lat=centroid_geographic.y,
        lon=centroid_geographic.x,
        text=scen_geodf["VAL_DIFF_SIGN"].astype(str) + "%" + "<br>" + scen_geodf["BPART_SUFFIX"],
        custom_data=["BPART", "CONTRACTOR_CONVENTION", "AGENCYNAME", "VAL_DIFF", "VAL_PERC", "DATA_TYPE"],
    )

    fig1.update_traces(
        textposition='middle center', 
        hovertemplate=my_hovertemplate, 
        showlegend=False,
        mode='text'
    )

    fig1.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')

    return fig1


@lru_cache
def create_line_plot(data_type: str, data_filter: list=tuple(), line_color='rgb( 37, 170, 225)'):
    """Creates line plot on the map for the given data type.

    Args:
        data_type (str): Data type for plot to display.
        data_filter (list, optional): Filter to apply on the function. Defaults to tuple().
        line_color (str, optional): Line color. Defaults to 'rgb( 37, 170, 225)'.

    Returns:
        px.line_mapbox figure: Plotly Line Plot figure of given data type.
    """
    # Read the shape file into a geodf
    geodf = load_shp(data_type)

    # Apply the filters (if any)
    for f in data_filter:
        geodf = f(geodf)


    lats = []
    lons = []

    for feature in geodf.geometry:
        if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
        elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
        else:
            continue
        for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            lats = np.append(lats, None)
            lons = np.append(lons, None)
    
    df = pd.DataFrame({'lat': lats, 'lon': lons})
    
    fig = px.line_mapbox(
        df,
        lat='lat', 
        lon='lon', 
        color_discrete_sequence=[line_color],
    )

    fig.update_traces(
        hovertemplate=None,
        hoverinfo="skip",
        showlegend=False
    )

    return fig


@lru_cache
def create_centroid_plot(data_type: str, custom_data=("BPART", "ALIAS", "DATA_TYPE"), centroid_color='rgb( 37, 170, 225)'):
    """Creates a centroid plot on the map for given type of data.

    Args:
        data_type (str): Data type for plot to display.
        custom_data (tuple, optional): Customized data to recognize data type and display in hover. Defaults to ("BPART", "ALIAS", "DATA_TYPE").
        centroid_color (str, optional): Centroid marker color. Defaults to 'rgb( 37, 170, 225)'.

    Returns:
        plotly.graph_objects.Scatter: Plotly centroid figure of given data type.
    """
    geodf = load_shp(data_type)

    centroid_df = geodf.geometry.to_crs(epsg=32618)
    centroid_projected = centroid_df.geometry.centroid
    centroid_geographic = centroid_projected.to_crs(epsg=4326)

    my_hovertemplate = "<b>%{customdata[1]}</b><br>%{customdata[0]}<extra></extra>"
    fig1 = px.scatter_mapbox(
        geodf,
        lat=centroid_geographic.y,
        lon=centroid_geographic.x,
        custom_data=custom_data
    )

    fig1.update_traces(
        textposition='middle center', 
        hovertemplate=my_hovertemplate, 
        showlegend=False,
        mode='markers',
        marker=dict(size=15, color=centroid_color, symbol="circle")
    )

    fig1.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')

    return fig1


@lru_cache
def create_choropleth_plot(data_type: str, custom_data=("BPART", "ALIAS", "DATA_TYPE")):
    """Creates a choropleth plot on the map for given type of data.

    Args:
        data_type (str): Data type for plot to display.
        custom_data (tuple, optional):  Customized data to recognize data type and display in hover. Defaults to ("BPART", "ALIAS", "DATA_TYPE").

    Returns:
        plotly.graph_objects.Figure: Plotly figure for the given data type.
    """
    geodf = load_shp(data_type)

    fig = px.choropleth_mapbox(
        geodf,
        geojson=geodf.geometry,
        locations=geodf.index,
        custom_data=custom_data,
    )

    my_hovertemplate = "<b>%{customdata[1]}</b><br>%{customdata[0]}<extra></extra>"
    fig.update_traces(
        hovertemplate=my_hovertemplate, 
        marker={"opacity": 0.7},
        showlegend=False
    )

    return fig


@lru_cache
def load_shp(data_type: str) -> gpd.GeoDataFrame:
    """Converts shapefile into a GeoDataFrame for the given data type, by calling the specific load_shp function corresponding to the data type.

    Args:
        data_type (str): Data type for shapefile to GeoDataFrame conversion.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame for the given data type.
    """
    geodf = None
    match data_type:
        case "contractors":
            geodf = load_shp_contractors()
        case "exports":
            geodf = load_shp_export()
        case "reservoirs":
            geodf = load_shp_reservoir()
        case "up_flows":
            geodf = load_shp_upstream_flows()
        case "pools":
            geodf = load_shp_pool()
        case "san_joaq_river":
            geodf = gpd.read_file("assets/qgis/san_joaq_river_smooth.shp")
            geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        case "amer_river":
            geodf = gpd.read_file("assets/qgis/amer_river_smooth.shp")
            geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        case "feath_river":
            geodf = gpd.read_file("assets/qgis/feath_river_smooth.shp")
            geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        case "sac_river":
            geodf = gpd.read_file("assets/qgis/sac_river_smooth.shp")
            geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        case "aqueducts":
            geodf = gpd.read_file("assets/qgis/caa_pools.shp")
            geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        case _:
            geodf=None

    return geodf


def create_df_for_scen(
    data_df: pd.DataFrame, geodf: gpd.GeoDataFrame, scenario1: str, scenario2: str
):
    """Creates finalized GeoDataFrame for SWP Contractors with filtered scenarios and additional columns for getting
    the difference of the average annual sum for scenario 1 - scenario 2 for each SWP contractor (in value and percentage form), as well as the 
    DATA_TYPE column to specify the data type.

    Args:
        data_df (pd.DataFrame): Pandas DataFrame containing average annual sum and associated metadata.
        geodf (gpd.GeoDataFrame): Initial GeoDataFrame for SWP Contractors.
        scenario1 (str): First climate scenario.
        scenario2 (str): Second climate scenario.

    Returns:
        gpd.GeoDataFrame: Finalized GeoDataFrame for SWP Contractors.
    """
    scen_geodf = geodf.copy()
    scen_geodf = scen_geodf.set_index("CONTRACTOR_CONVENTION")

    # Create dataframes with each scenario filtered
    data_df_1 = data_df.loc[data_df["Scenario"] == scenario1]
    data_df_2 = data_df.loc[data_df["Scenario"] == scenario2]

    # Set the index of both dataframes to CONTRACTOR_CONVENTION
    data_df_1 = data_df_1.set_index("CONTRACTOR_CONVENTION")
    data_df_2 = data_df_2.set_index("CONTRACTOR_CONVENTION")

    # Create a column in scen_geodf for the difference of both scenarios' avg annual sum
    scen_geodf["VAL_1"] = data_df_1["VAL"]
    scen_geodf["VAL_2"] = data_df_2["VAL"]
    scen_geodf["VAL_DIFF"] = scen_geodf["VAL_2"] - scen_geodf["VAL_1"]
    scen_geodf["BPART"] = data_df_1["BPART"]
    scen_geodf["BPART_SUFFIX"] = data_df_1["BPART_SUFFIX"]

    # Create a column in scen_geodf for val_diff percentages
    scen_geodf["VAL_PERC"] = (
        ((scen_geodf["VAL_2"] - scen_geodf["VAL_1"]) / scen_geodf["VAL_1"]) * 100
    ).round()

    # If VAL_1 is 0, set VAL_PERC to None
    scen_geodf.loc[scen_geodf["VAL_1"] == 0, "VAL_PERC"] = None

    # create another column in scen_geodf for VAl_DIFF w/ respective signs
    scen_geodf["VAL_DIFF_SIGN"] = scen_geodf["VAL_DIFF"]
    for value in scen_geodf["VAL_DIFF"]:
        if value > 0:
            scen_geodf.loc[scen_geodf["VAL_DIFF"] == value, "VAL_DIFF_SIGN"] = (
                f"+{value}"
            )

    # create a column that shows what type of data is in the df
    scen_geodf["DATA_TYPE"] = "CONTRACTORS"

    # Reset index to ensure geometry alignment
    scen_geodf = scen_geodf.reset_index()

    return scen_geodf


@lru_cache
def get_scenarios():
    """Creates list of the different climate scenarios by getting the scenarios from data_df.

    Returns:
        list: List of the different unique climate scenarios.
    """
    data_df = calc_mean()
    return data_df["Scenario"].unique()


@lru_cache
def update_monthly_exc(b_part, slider_yr_range):
    """Updates monthly exceedance plot for given B-Part in given year range.

    Args:
        b_part (str): Specific B-Part.
        slider_yr_range (list): Start and end year.

    Returns:
        plotly.graph_objects.Scatter: Plotly figure for monthly exceedance data.
    """
    startyr = slider_yr_range[0]
    endyr = slider_yr_range[1]
    df = qd.df_dv.loc[
        (qd.df_dv["iwy"] >= startyr)
        & (qd.df_dv["iwy"] <= endyr)
    ]

    series_container = []
    # Filter the calendar months
    df0 = df.loc[df["icm"].isin(convert_cm_nums(month_list))]

    for assumption in ASSUMPTION_ORDER:
        series_i = df0.loc[df0["Assumption"] == assumption, b_part]
        series_i = series_i.sort_values()
        series_i = series_i.reset_index(drop=True)
        series_i.rename(assumption, inplace=True)
        series_container.append(series_i)

    df3 = pd.concat(series_container, axis=1)
    fig = go.Figure()

    for i, column in enumerate(df3.columns):
        series_sorted = df3[column].dropna()
        exceedance_prob = (series_sorted.index + 1) / len(series_sorted) * 100
        # linearly interpolate the line above so we get 100 points, from 1-100
        df = pd.DataFrame(data={"y": series_sorted, "x": exceedance_prob})
        integer_index = df["x"].round(decimals=0).astype(int)
        # This step should really be an interpolation using scipy.interp1d, but it works
        # with the dependencies that we have right now
        # TODO: 2024-07-18 Consider updating to an interpolation method
        df = df.groupby(integer_index).mean()
        df = df.reindex(index=range(1, 101, 1)).ffill()
        #print(df3)
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["y"],
                mode="lines",
                name=column,
                line=dict(color=ASSUMPTION_COLORS.get(column, "#cccccc")),
            )
        )

    fig.update_layout(
        plot_bgcolor="lightgray",
        xaxis_title="Non Exceedance Probability (%)",
        xaxis_tickformat=",d",
        yaxis_title="",
        legend_title="Scenario",
        showlegend=True,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="black"),
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, x1=1, y0=0, y1=1, line=dict(color='black', width=1), fillcolor='rgba(0,0,0,0)')],
    )

    return fig


@lru_cache
def update_monthly(b_part, slider_yr_range):
    """Updates monthly plot for given B-Part in given year range.

    Args:
        b_part (str): Specific B-Part.
        slider_yr_range (list): Start and end year.

    Returns:
        px.line figure: Plotly Line Plot for monthly data.
    """
    startyr = slider_yr_range[0]
    endyr = slider_yr_range[1]
    df0 = qd.df_dv.loc[
        (qd.df_dv["iwy"] >= startyr)
        & (qd.df_dv["iwy"] <= endyr)
    ]

    df1 = round(df0.groupby(["Scenario", "iwm"]).mean(numeric_only=True))
    df1 = df1.reindex(qd.scen_aliases, level="Scenario")
    fig = px.line(
        df1,
        x=df1.index.get_level_values(1),
        y=b_part,
        color=df1.index.get_level_values(0),
        labels={"color": "Scenario"},
        color_discrete_sequence=PLOT_COLORS,
    )
    fig.update_layout(
        plot_bgcolor="lightgray",
        xaxis=dict(
            tickmode="array",
            tickvals=monthfilter,
            ticktext=month_list,
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="black",
        ),
        yaxis_tickformat=",d",
        xaxis_title="Month",
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, x1=1, y0=0, y1=1, line=dict(color='black', width=1), fillcolor='rgba(0,0,0,0)')],
    )

    return fig


@lru_cache
def update_timeseries(b_part):
    """Updates timeseries plot for given B-Part.

    Args:
        b_part (_type_): Specific B-Part.

    Returns:
        px.line figure: Plotly Line Plot for timeseries data.
    """
    fig = px.line(
        qd.df_dv,
        x=qd.df_dv.index,
        y=b_part,
        color="Scenario",
        color_discrete_sequence=PLOT_COLORS,
    )
    fig.update_layout(
        plot_bgcolor="lightgray",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="black"),
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, x1=1, y0=0, y1=1, line=dict(color='black', width=1), fillcolor='rgba(0,0,0,0)')],
    )

    return fig

@lru_cache
def update_bar_annual(b_part, slider_yr_range):
    """Updates annual plot for given B-Part in given year range.

    Args:
        b_part (str): Specific B-Part.
        slider_yr_range (list): Start and end year.

    Returns:
        px.bar figure: Plotly Bar Plot for annual data.
    """
    startyr = slider_yr_range[0]
    endyr = slider_yr_range[1]
    df1 = qd.df_dv.loc[
        (qd.df_dv["iwy"] >= startyr)
        & (qd.df_dv["iwy"] <= endyr)
    ]
    
    df1 = cfs_taf(df1, qd.var_dict)

    df2 = round(df1.groupby(["Scenario"]).sum(numeric_only=True) / (endyr - startyr + 1))
    
    df2 = df2.reindex(qd.scen_aliases, level="Scenario")

    fig = px.bar(
        df2,
        x=df2.index.get_level_values(0),
        y=b_part,
        color=df2.index.get_level_values(0),
        text_auto=True,
        color_discrete_sequence=PLOT_COLORS,
    )
    fig.update_layout(
        barmode="relative",
        plot_bgcolor="lightgray",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="black"),
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, x1=1, y0=0, y1=1, line=dict(color='black', width=1), fillcolor='rgba(0,0,0,0)')],
    )
    # show numeric labels above bars in black
    fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside', textfont=dict(color='black'), cliponaxis=False)
    return fig
