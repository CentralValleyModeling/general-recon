from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page
import plotly.express as px
#import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import yaml
import pandas as pd

from utils.tools import (make_summary_df,common_pers)

from utils.query_data import df_dv, scen_aliases, var_dict



register_page(
    __name__,
    #name='Page 4',
    top_nav=True,
    path='/contractor_summary'
)

b = []

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
    global b
    b = []
    s=str(kwargs.get('type','table_a_btn'))
    typefilter = typefilter_dict[s]
    
    
    for i in var_dict:
        if var_dict[i]['type']==typefilter:
            b.append(i)
    exp_tbl = make_summary_df(scen_aliases,df_dv,var_dict,bparts=b,start_yr=1922,end_yr=2021)

    layout = dbc.Container([
        dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Summary Table"),
        dcc.RangeSlider(1922, 2021, 1, value=[1922, 2015],
                        marks={i: '{}'.format(i) for i in range(1922,2021,5)},
                        pushable=False,
                        id='slider-yr-range'),
        dcc.Dropdown(options = common_pers,id='dropdown_common_pers_csum', placeholder="Select the Averaging Period (Years)"),
        html.Div(id='output-container-range-slider_2'),
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


# Update Summary Table
@callback(
    Output(component_id='exp_tbl', component_property='data'),
    Input(component_id='slider-yr-range', component_property='value'),
)
def update_table(slider_yr_range):
    df_tbl = make_summary_df(scen_aliases,df_dv,var_dict,bparts=b,
                             start_yr=slider_yr_range[0],end_yr=slider_yr_range[1])
    data=df_tbl.to_dict(orient='records')
    return data

@callback(
    Output(component_id='output-container-range-slider_2', component_property='children'),
    Input(component_id='slider-yr-range', component_property='value')
)
def update_table(value):
    return str('Average Period: '),value[0],str('-'),value[1]

@callback(
    Output(component_id='slider-yr-range', component_property='value'),
    Input(component_id='dropdown_common_pers_csum', component_property='value')
)
def slider(dropdown_val):
    startyr = common_pers[dropdown_val][0]
    endyr = common_pers[dropdown_val][-1]
    return startyr,endyr