# Imports
from collections import namedtuple
import pandss as pdss
import pandas as pd
import numpy as np
import yaml

from dash import Dash, html, dcc, Input, Output, callback, dash_table
import plotly.express as px
#import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from utils import (make_summary_df, month_map, load_data_mult, 
                   make_ressum_df, month_list, convert_cm_nums)


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
        html.H2("A General dashboard for reviewing CalSim 3 Results")
        ]

)

app.run(debug=True)