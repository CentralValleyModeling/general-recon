# Imports
from collections import namedtuple
import pandss as pdss
import pandas as pd
import numpy as np
import yaml

from dash import Dash, html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from utils import make_summary_df


Scenario = namedtuple('Scenario',['pathname','alias','active'])
with open('dictionary.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)


dv_files = ["DCR2023_DV_8.15.5_Nile_Hist_v14.dss","DCR2023_DV_8.15.5_Nile_Hist_v14_orov_sens.dss"]

s1 = Scenario('DCR2023_DV_8.15.5_Nile_Hist_v14.dss', 'Baseline',1)
s2 = Scenario('DCR2023_DV_8.15.5_Nile_Hist_v14_orov_sens.dss', 'Orov_Sens',1)
s3 = Scenario(None,None,0)
s4 = Scenario(None,None,0)

# Generator object for Scenarios
scenarios = (scenario for scenario in [s1,s2,s3,s4] if scenario.active==1)

bparts = []
for var in var_dict:
    bparts.append(var_dict[var]['bpart'])

df = pd.read_csv('temp_mult.csv', index_col=0, parse_dates=True)

df_tbl = make_summary_df(df,var_dict)

app = Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children="CalSim 3 Results Dashboard"),
    html.H2("A General dashboard for reviewing CalSim 3 Results"),
    dcc.Upload(id='upload-data',children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
    ]),
    ),
    html.Button('Load', id='btn-load-study-1', n_clicks=0),
    html.Div(id='dummy-div'),
    html.Div([
        "B-Part: ",
        dcc.Dropdown(bparts, id='b-part')
    ]),
    html.Br(),
    html.Div(id='my-output'),
    html.H5("Timeseries Plot"),
    dcc.Graph(id='timeseries-plot'),

    dcc.Markdown("#### Table Controls"),
    
    dcc.Checklist(
    ['Oct', 'Nov', 'Dec',
    'Jan', 'Feb', 'Mar',
    'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep'],
    inline=True, id = 'monthchecklist'
    ),

    dcc.RangeSlider(1922, 2021, 1, value=[1922, 2021],
                    marks={i: '{}'.format(i) for i in range(1922,2021,5)},
                    pushable=True,
                    id='slider-yr-range'),
    html.Div(id='output-container-range-slider'),
    html.Button('Load', id='btn-refresh-tbl', n_clicks=0),
    dash_table.DataTable(
        id='sum_tbl',
        columns=[{"name": i, "id": i} 
                 for i in df_tbl.columns],
        data=df_tbl.to_dict(orient='records'),
        style_header={
                'backgroundColor': 'rgb(200, 200, 200)',
                'fontWeight': 'bold'
        },
        style_cell={
        'width': '{}%'.format(len(df_tbl.columns)),
        'textOverflow': 'ellipsis',
        'overflow': 'hidden'
        },
    )
])

@app.callback(
  Output(component_id='dummy-div', component_property='children'),
  Input(component_id='btn-load-study-1', component_property='n_clicks'),
  prevent_initial_call=True
)
def load_data_mult(n_clicks):
    """
    # Load data from the selected DSS files into a .csv
    """
    dfi = pd.DataFrame()
    df = pd.DataFrame()
    appended_data = []

    for scenario in scenarios:
        print(scenario.pathname,scenario.alias)
        with pdss.DSS(scenario.pathname) as dss:
  
            # Loop to read all paths into DataFrame
            for var in var_dict:
                pn = var_dict[var]['pathname']
                path_i = pdss.DatasetPath.from_str(pn)
                print (pn)

                for regular_time_series in dss.read_multiple_rts(path_i):
                    dfi['Scenario'] = scenario.alias
                    dfi[regular_time_series.path.b] = regular_time_series.to_frame()
        
        # Make a list of the DataFrames associated with each DV file
        appended_data.append(dfi)
        dfi = pd.DataFrame()

    # concatenate the individual DataFrames into one big DataFrame
    df = pd.concat(appended_data)
        
    date_map = pd.read_csv('date_map.csv', index_col=0, parse_dates=True)
    df = pd.merge(df,date_map, left_index=True, right_index=True)
    df.to_csv('temp_mult.csv')
    print(df)
    return


@callback(
    Output(component_id='timeseries-plot', component_property='figure'),
    Input(component_id='b-part', component_property='value')
)
def update_timeseries(b_part):
    fig = px.line(df, x=df.index, y=b_part, color='Scenario')
    print(df)
    return fig

#@callback(
#    Output(component_id='sum_tbl', component_property='data'),
#    Input(component_id='btn-refresh-tbl', component_property='n_clicks')
#)
@callback(
    Output(component_id='sum_tbl', component_property='data'),
    #Output(component_id='output-container-range-slider', component_property='children'),
    Input(component_id='slider-yr-range', component_property='value')
)
def update_table(value):
    df_tbl = make_summary_df(df,var_dict,start_yr=value[0],end_yr=value[1])
    data=df_tbl.to_dict(orient='records')
    return data
    #return value[0],str('-'),value[1]

if __name__ == '__main__':
    app.run(debug=True)
