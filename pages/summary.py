from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page
import plotly.express as px
#import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import yaml
import pandas as pd

from utils.tools import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums,
                   wyt_list, convert_wyt_nums, cfs_taf)

from utils.query_data import df_dv, scen_aliases, var_dict



register_page(
    __name__,
    #name='Page 4',
    top_nav=True,
    path='/summary'
)


exp_tbl = make_summary_df(scen_aliases,df_dv,var_dict,bparts=[
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
    'CVPTOTALDEL'])

# Determine the table order
# Descriptive stuff goes first
table_order = [{"name": 'Type', "id": 'type'},
               {"name": 'Description', "id": 'description'},
               {"name": 'B-Part', "id": 'bpart'}]

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