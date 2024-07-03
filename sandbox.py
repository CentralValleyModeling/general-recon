from dash import Dash, html, dcc, Input, Output, callback, dash_table, register_page
import plotly.express as px
#import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import yaml
import pandas as pd
from charts.chart_layouts import ann_exc_plot
from utils.tools import (make_summary_df,common_pers,month_list)
from utils.query_data import df_dv, scen_aliases, var_dict



fig =ann_exc_plot(df_dv,"SWP_TA_SB",monthchecklist=month_list,yearwindow="Calendar Year")
fig.show()