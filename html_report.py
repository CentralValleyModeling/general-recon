# Imports
import pandss as pdss
import pandas as pd
import numpy as np

from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

file = "DCR2023_DV_8.15.5_Nile_Hist_v14.dss"
file2 = "DCR2023_DV_8.15.5_Nile_Hist_v14.dss"
files = ["DCR2023_DV_8.15.5_Nile_Hist_v14.dss","DCR2023_DV_8.15.5_Nile_Hist_v14_orov_sens.dss"]


def load_data_mult():
    dfi = pd.DataFrame()
    df = pd.DataFrame()
    appended_data = []

    paths = [
            "/CALSIM/S_OROVL/STORAGE//.*/.*/",
            "/CALSIM/S_FOLSM/STORAGE//.*/.*/",
            "/CALSIM/S_SHSTA/STORAGE//.*/.*/",            
            "/CALSIM/S_TRNTY/STORAGE//.*/.*/",            
            ]

    for n, file in enumerate(files):
        print(file,n)
        with pdss.DSS(file) as dss:
  
            # Loop to read all paths into DataFrame
            for path in paths:
                print (path)
                path_i = pdss.DatasetPath.from_str(path)

                for regular_time_series in dss.read_multiple_rts(path_i):
                    dfi['study'] = n
                    dfi[regular_time_series.path.b] = regular_time_series.to_frame()
        
        # Make a list of the DataFrames associated with each DV file
        appended_data.append(dfi)
        dfi = pd.DataFrame()

    # concatenate the individual DataFrames into one big DataFrame
    df = pd.concat(appended_data)
        
    #date_map = pd.read_csv('date_map.csv', index_col=0, parse_dates=True)
    #df = pd.merge(df,date_map, left_index=True, right_index=True)
    df.to_csv('temp_mult.csv')
    print(df)

    return


catalog = pdss.read_catalog(file)
df = pd.DataFrame()
df = pd.read_csv('temp_mult.csv', index_col=0, parse_dates=True)

# Wildcard paths
#path_wc = pdss.DatasetPath.from_str("/CALSIM/.*/APPLIED-WATER//.*/.*/")
#path_wc = pdss.DatasetPath.from_str("/CALSIM/.*/GW-PUMPING//.*/.*/")

app = Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children="CalSim 3 Results Dashboard"),
    html.H2("A General dashboard for reviewing CalSim 3 Results"),
    dcc.Upload(id='upload-data',children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),),
    html.Button('Load', id='btn-load-study-1', n_clicks=0),
    html.Div(id='dummy-div'),
    html.Div([
        "B-Part: ",
        dcc.Dropdown(['S_OROVL', 'S_FOLSM'], id='b-part')
    ]),
    html.Br(),
    html.Div(id='my-output'),
    html.H5("Timeseries Plot"),
    dcc.Graph(id='timeseries-plot'),
    ]
)

# Load data from the selected DSS files into a .csv
@app.callback(
  Output(component_id='dummy-div', component_property='children'),
  Input(component_id='btn-load-study-1', component_property='n_clicks'),
  prevent_initial_call=True
)
def load_data(n_clicks):
    df = pd.DataFrame()

    paths = ["/CALSIM/S_OROVL/STORAGE//.*/.*/",
            "/CALSIM/S_FOLSM/STORAGE//.*/.*/"]

    # Loop to read all paths into DataFrame
    for path in paths:
        print (path)
        path_i = pdss.DatasetPath.from_str(path)

        for regular_time_series in pdss.read_multiple_rts(file, path_i):
            df[regular_time_series.path.b] = regular_time_series.to_frame()
        
    date_map = pd.read_csv('date_map.csv', index_col=0, parse_dates=True)
    df = pd.merge(df,date_map, left_index=True, right_index=True)
    df.to_csv('temp.csv')
    print(df)
    return

@callback(
    Output(component_id='timeseries-plot', component_property='figure'),
    Input(component_id='b-part', component_property='value')
)
def update_timeseries(b_part):
    #x = np.arange(10)
    fig = px.line(df, x=df.index, y=b_part, color='study')
    #fig = go.Figure(data=go.Scatter(x=x, y=x**2))
    #fig.add_trace(go.scatter.Line(df, x=df.index, y=b_part))
    print(df)
    return fig


if __name__ == '__main__':
    app.run(debug=True)
