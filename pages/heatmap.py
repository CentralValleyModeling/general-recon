import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page
import dash_bootstrap_components as dbc
import pandas as pd

from utils.tools import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums,
                   wyt_list, convert_wyt_nums, cfs_taf)

from pages.study_selection import scenarios, scen_aliases, var_dict

register_page(
    __name__,
    top_nav=True,
    path='/heatmap'
)

# Make dataframe heatmap

df = pd.read_csv('data/temp.csv', index_col=0, parse_dates=True)

def make_heatmap_df(scenlist,df,var_dict,start_yr=1922,end_yr=2021,
                    monthfilter=[1,2,3,4,5,6,7,8,9,10,11,12],bparts=None):


    df1 = df.loc[(df['icm'].isin(monthfilter)) &
                (df['iwy']>=start_yr) &(df['iwy']<=end_yr)
                ] 

    for var in var_dict:
        if var_dict[var]['table_convert']=='cfs_taf':
            df1[var]=df1[var]*df1['cfs_taf']
        else:
            continue
    
    # Annual Average
    df_tbl = round(df1.groupby(["Scenario"]).sum()/(end_yr-start_yr+1))

    df_tbl = (df_tbl - df_tbl.iloc[0])


    # Time slicing is done; drop the index columns
    df_tbl.drop(['icy','icm','iwy','iwm','cfs_taf'],axis=1,inplace=True)

    if bparts != None:
        df1 = df_tbl.loc[:,bparts]
        df_tbl = df1

    # Make a dictionary of just aliases to map to the dataframe
    alias_dict = {}
    type_dict = {}
    for key in var_dict:
        alias_dict[key]=var_dict[key]['alias']
        type_dict[key]=var_dict[key]['type']

    return df_tbl


bparts=[
    'C_LWSTN',
    'D_LWSTN_CCT011',
    'C_WKYTN',
    'C_KSWCK',
    'C_SAC097',
    'C_FTR059',
    'C_FTR003',
    'C_YUB006',
    'C_SAC083',
    'C_NTOMA',
    'C_AMR004',
#   '----'
    'DELTAINFLOWFORNDOI',
#    '----'
    'C_CAA003',
    'C_CAA003_SWP',
    'C_CAA003_CVP',
    'C_CAA003_WTS',
    'C_DMC000',
    'C_DMC000_CVP',
    'C_DMC000_WTS',
#    '----',
    'SWP_TA_TOTAL',
    'SWP_IN_TOTAL',
    'SWP_CO_TOTAL',
    'CVPTOTALDEL']
heatmap_df = make_heatmap_df(scen_aliases,df,var_dict,bparts=bparts)

print(heatmap_df)

def layout():
    layout = dbc.Container([
        dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Results: Heat Map"),
        dcc.Graph(id='heatmap'),
        html.P("Variables Included:"),
        dcc.Checklist(
            id='vars',
            options=bparts,
            value=bparts,
        )
    ])
    return layout

@callback(
    Output("heatmap", "figure"), 
    Input("vars", "value"))
def filter_heatmap(cols):
    #df = px.data.medals_wide(indexed=True) # replace with your own data source
    df = heatmap_df
    fig = px.imshow(df[cols])
    return fig

layout()