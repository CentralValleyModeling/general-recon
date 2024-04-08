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

register_page(
    __name__,
    #name='Page 4',
    top_nav=True,
    path='/summary'
)



with open('constants/vars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)
df = pd.read_csv('data/temp.csv', index_col=0, parse_dates=True)

exp_tbl = make_summary_df(df,var_dict,bparts=['C_CAA003'])

table_order = [{"name": 'Description', "id": 'Description'},
          {"name": 'B-Part', "id": 'index'}]

table_order.extend([{"name": i, "id": i} for i in exp_tbl.columns if i not in['Description','index']])

def layout():
    layout = dbc.Container([
        dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Results Dashboard"),
        dcc.Markdown("### Summary Table"),

        dbc.Row(
            dash_table.DataTable(
                id='sum_tbl',
                columns=table_order,
                data=exp_tbl.to_dict(orient='records'),
                style_header={
                        'backgroundColor': 'rgb(200, 200, 200)',
                        'fontWeight': 'bold'
                },
                style_cell={
                'width': '{}%'.format(len(exp_tbl.columns)),
                'textOverflow': 'ellipsis',
                'overflow': 'hidden'
                },
            )
        )
    ])
    return layout