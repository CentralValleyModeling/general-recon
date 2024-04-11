from dash import html, register_page  #, callback # If you need callbacks, import it here.
from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page
import plotly.express as px
#import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import yaml
import pandas as pd

from utils.tools import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums,
                   wyt_list, convert_wyt_nums, cfs_taf)

from pages.study_selection import scenarios, scen_aliases



register_page(
    __name__,
    #name='Page 4',
    top_nav=True,
    path='/summary'
)

with open('constants/vars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)
df = pd.read_csv('data/temp.csv', index_col=0, parse_dates=True)

exp_tbl = make_summary_df(scen_aliases,df,var_dict,bparts=[
    'C_CAA003',
    'C_CAA003_SWP',
    'C_CAA003_CVP',
    'C_CAA003_WTS',
    'C_DMC000',
    'C_DMC000_CVP',
    'C_DMC000_WTS',
    #'----',
    'SWP_TA_TOTAL',
    'SWP_IN_TOTAL',
    'SWP_CO_TOTAL'])

# Determine the table order
# Descriptive stuff goes first
table_order = [{"name": 'Type', "id": 'type'},
               {"name": 'Description', "id": 'description'},
               {"name": 'B-Part', "id": 'index'}]

# Scenarios go next
table_order.extend([{"name": s, "id": s, "type": "numeric","format": { "specifier": ",.0f"}} 
                    for s in scen_aliases if s not in['description','index','type']])


def layout():
    layout = dbc.Container([
        dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Results One Pager"),
        dcc.Markdown("### Summary Table"),
        
        dbc.Row([
            dcc.Markdown("#### "),
            dash_table.DataTable(
                id='exp_tbl',
                columns=table_order,
                data=exp_tbl.to_dict(orient='records'),
                style_header={
                        'backgroundColor': 'rgb(200, 200, 200)',
                        'fontWeight': 'bold'
                },
                style_cell={
                'width': '{}%'.format(len(exp_tbl.columns)),
                #'width': '1000px',
                'textOverflow': 'ellipsis',
                'overflow': 'hidden',
                'textAlign': 'left',
                },
            ),
        ])
    ])
    return layout
layout()