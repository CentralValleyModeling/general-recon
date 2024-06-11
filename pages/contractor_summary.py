from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page
import plotly.express as px
#import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import yaml
import pandas as pd

from utils.tools import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums,
                   wyt_list, convert_wyt_nums, cfs_taf)

from utils.query_data import df, scen_aliases, var_dict



register_page(
    __name__,
    #name='Page 4',
    top_nav=True,
    path='/contractor_summary'
)

# Determine the table order
# Descriptive stuff goes first
table_order = [{"name": 'Type', "id": 'type'},
               {"name": 'Description', "id": 'description'},
               {"name": 'B-Part', "id": 'bpart'}]

# Scenarios go next
table_order.extend([{"name": s, "id": s, "type": "numeric","format": { "specifier": ",.0f"}} 
                    for s in scen_aliases if s not in['description','index','type']])

typefilter_dict = {'table_a_btn':'Delivery - TA','a21_btn':'Delivery - IN','a56_btn':'Delivery - CO'}

def layout(**kwargs): 
    s=str(kwargs.get('type','table_a_btn'))
    typefilter = typefilter_dict[s]
    b = []
    for i in var_dict:
        if var_dict[i]['type']==typefilter:
            b.append(i)
    exp_tbl = make_summary_df(scen_aliases,df,var_dict,bparts=b)
    layout = dbc.Container([
        dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Summary Table"),
    
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