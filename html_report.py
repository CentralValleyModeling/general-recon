# Imports
from collections import namedtuple
import pandss as pdss
import pandas as pd
import numpy as np

from dash import Dash, html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


Scenario = namedtuple('Scenario',['pathname','alias','active'])

dv_files = ["DCR2023_DV_8.15.5_Nile_Hist_v14.dss","DCR2023_DV_8.15.5_Nile_Hist_v14_orov_sens.dss"]

s1 = Scenario('DCR2023_DV_8.15.5_Nile_Hist_v14.dss', 'Baseline',1)
s2 = Scenario('DCR2023_DV_8.15.5_Nile_Hist_v14_orov_sens.dss', 'Orov_Sens',1)
s3 = Scenario(None,None,0)
s4 = Scenario(None,None,0)

# Generator object for Scenarios
scenarios = (scenario for scenario in [s1,s2,s3,s4] if scenario.active==1)


paths = [
        # Storage
        "/CALSIM/S_OROVL/STORAGE//.*/.*/;",
        "/CALSIM/S_FOLSM/STORAGE//.*/.*/;",
        "/CALSIM/S_SHSTA/STORAGE//.*/.*/;",            
        "/CALSIM/S_TRNTY/STORAGE//.*/.*/;",            
        "/CALSIM/S_SLUIS_SWP/STORAGE//.*/.*/;",
        "/CALSIM/S_SLUIS_CVP/STORAGE//.*/.*/;",
        # River Flows
        "/CALSIM/C_LWSTN/.*//.*/.*/;1",
        "/CALSIM/D_LWSTN_CCT011/.*//.*/.*/;1",
        "/CALSIM/C_WKYTN/.*//.*/.*/;1",
        "/CALSIM/C_KSWCK/.*//.*/.*/;1",
        "/CALSIM/C_SAC097/.*//.*/.*/;1",
        "/CALSIM/C_FTR059/.*//.*/.*/;1",
        "/CALSIM/C_FTR003/.*//.*/.*/;1",
        "/CALSIM/C_YUB006/.*//.*/.*/;1",
        "/CALSIM/C_SAC083/.*//.*/.*/;1",
        "/CALSIM/C_NTOMA/.*//.*/.*/;1",
        "/CALSIM/C_AMR004/.*//.*/.*/;1",
        "/CALSIM/GP_SACWBA/.*//.*/.*/;1",
        #Exports
        "/CALSIM/C_CAA003/.*//.*/.*/;1",
        "/CALSIM/C_CAA003_SWP/.*//.*/.*/;1",
        "/CALSIM/C_CAA003_CVP/.*//.*/.*/;1",
        "/CALSIM/C_CAA003_WTS/.*//.*/.*/;1",
        "/CALSIM/C_DMC000/.*//.*/.*/;1",
        "/CALSIM/C_DMC000_CVP/.*//.*/.*/;1",
        "/CALSIM/C_DMC000_WTS/.*//.*/.*/;1",
        #Deliveries
        "/CALSIM/SWP_TA_TOTAL/.*//.*/.*/;1",
        "/CALSIM/SWP_IN_TOTAL/.*//.*/.*/;1",
        "/CALSIM/SWP_CO_TOTAL/.*//.*/.*/;1",
        ]

bparts = []
for path in paths:
    bparts.append(path.split('/')[2])

df = pd.DataFrame()
df = pd.read_csv('temp_mult.csv', index_col=0, parse_dates=True)

# Make Summary Table from dataframe
start_yr = 1922
end_yr = 2021
monthfilter = [1,2,3,4,5,6,7,8,9,10,11,12]
#monthfilter = [9]
df1 = df.loc[(df['icm'].isin(monthfilter)) &
             (df['iwy']>=start_yr) &(df['iwy']<=end_yr)
            ] 

# Do Conversions
for path in paths:
    print(path.split(';')[1]==str(1))
    if path.split(';')[1]==str(1):
        print(f'converted {path} to TAF')
        df1[path.split('/')[2]]=df1[path.split('/')[2]]*df1['cfs_taf']
    else:
        print(path)

# Annual Average
df_tbl = round(df1.groupby(["Scenario"]).sum()/(end_yr-start_yr+1))

# Drop the index columns
df_tbl.drop(['icy','icm','iwy','iwm','cfs_taf'],axis=1,inplace=True)

df_tbl = df_tbl.T
df_tbl['diff']=df_tbl['Orov_Sens']-df_tbl['Baseline']
df_tbl['perdiff'] = round((df_tbl['Orov_Sens']-df_tbl['Baseline'])/df_tbl['Baseline'],2)*100
df_tbl.reset_index(inplace=True)
print(df_tbl)

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
        dcc.Dropdown(bparts, id='b-part')
    ]),
    html.Br(),
    html.Div(id='my-output'),
    html.H5("Timeseries Plot"),
    dcc.Graph(id='timeseries-plot'),
    
    dash_table.DataTable(
        id='sum_tbl',
        columns=[{"name": i, "id": i} 
                 for i in df_tbl.columns],
        data=df_tbl.to_dict(orient='records'),
        style_header={
                'backgroundColor': 'rgb(200, 200, 200)',
                'fontWeight': 'bold'}
    )

    ]
)

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
            for path in paths:
                path = path.split(';')[0]
                path_i = pdss.DatasetPath.from_str(path)
                print (path)

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
'''
@callback(
    Output('sum_tbl', 'table'),
    Input(component_id='b-part', component_property='value')
)
def update_table(b_part):
    table = dash_table.DataTable(df.to_dict('records'),[{"name": i, "id": i} for i in df.columns])
    return table
'''

if __name__ == '__main__':
    app.run(debug=True)
