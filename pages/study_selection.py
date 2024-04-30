from dash import html, register_page, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import dash_uploader as du
from collections import namedtuple
import yaml
import pandas as pd

register_page(
    __name__,
    #name='Page 2',
    top_nav=True,
    path='/study_selection'
)
scen_dict = {} # Global variable to store scenario pathnames and aliases, as entered by user

df = pd.read_csv('data/temp.csv', index_col=0, parse_dates=True)
date_map = pd.read_csv('constants/date_map.csv', index_col=0, parse_dates=True)
scen_aliases = df.Scenario.unique()

with open('constants/vars.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)


def layout():
    layout = dbc.Container([
        dcc.Markdown("# ![](/assets/cs3_icon_draft.png) CalSim 3 Dashboard - Study Selection"),
        dbc.Row([
            html.Hr(),
            dcc.Markdown("## Upload Studies to Temporary Database"),
            dbc.Col(
                [
                    du.Upload(
                        id='dash-uploader',
                        max_files=30,
                        filetypes=['dss'],
                    ),
                    dash_table.DataTable(
                        id='file-table',
                        columns=[
                                #{'name': 'Path', 'id': 'pathname'},
                                {'name': 'Filename', 'id': 'filename'},
                                {'name': 'Alias', 'id': 'alias', 'editable': True}
                        ],
                        data=[],
                        editable=True
                    ),
                    
                    html.Button('Refresh Table', id='populate-table', n_clicks=0),
                    html.Button('Clear List', id='clear-button', style={'margin-top': '10px'}),  # Button to clear the list
                    
                    dbc.Row([
                    dcc.Input("temp.csv", id = 'csv-name'),
                    html.Button('Load Studies into CSV', id='load-studies', n_clicks=0),
                    ]),
                    
                    html.Div('',id='dummy-div1'),
                    html.Div(id='table-update-output'),
                    html.Div(id='output-data-upload'),

                ],
                width=6
            ),
        dbc.Row([
            html.Hr(),
            dcc.Markdown("## Retrieve Existing CSV Database"),

        ]),
    ])
    ])
    return layout




