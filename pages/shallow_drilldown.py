# Imports
from collections import namedtuple

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback, dcc, html, register_page

from charts.chart_layouts import ann_exc_plot, mon_exc_plot
from pages.styles import ASSUMPTION_ORDER, CLIMATE_ORDER, PLOT_COLORS, SCENARIO_COLORS
from utils.query_data import date_map, df_dv, scen_aliases, var_dict
from utils.tools import (
    cfs_taf,
    convert_wyt_nums,
    list_files,
    load_data_mult,
    make_ressum_df,
    make_summary_df,
    month_list,
    month_map,
    monthfilter,
    wyt_list,
)

register_page(
    __name__,
    name="Shallow Drilldown",
    top_nav=True,
    path="/shallow-drilldown",
    order=99,
)


def create_button_filter(
    label: str,
    filter_id: str,
    options: list[str],
) -> html.Div:
    return html.Div(
        children=[
            dbc.Label(label),
            dbc.Checklist(
                id=filter_id,
                value=[],
                options=[{"label": v, "value": v} for v in options],
            ),
        ],
        className="m-1 p-2 border-top",
    )


def create_dropdown(
    label: str,
    filter_id: str,
    options: list[str],
) -> html.Div:
    return html.Div(
        children=[
            dbc.Label(label),
            dbc.Select(
                id=filter_id,
                options=[{"label": v, "value": v} for v in options],
            ),
        ],
        className="m-1 p-2 border-top",
    )


def layout():
    filter_pane = dbc.Col(
        id="filter_pane",
        children=[
            html.H4("Data Filters"),
            create_button_filter(
                label="Scenarios",
                filter_id="filter-assumption",
                options=ASSUMPTION_ORDER,
            ),
            create_button_filter(
                label="Climate",
                filter_id="filter-climate",
                options=CLIMATE_ORDER,
            ),
            create_dropdown(
                label="Variable",
                filter_id="filter-variable",
                options=var_dict.keys(),
            ),
        ],
        class_name="col-4 col-md-2 bg-light py-3",
    )

    view_pane = dbc.Col(
        id="view_pane",
        children=[dcc.Graph(id="graph-monthly")],
        class_name="bg-transparent py-3",
    )

    return dbc.Row(
        children=[
            filter_pane,
            view_pane,
        ],
        class_name="h-100",
    )


@callback(
    Output("graph-monthly", "figure"),
    Input("filter-assumption", "value"),
    Input("filter-climate", "value"),
    Input("filter-variable", "value"),
)
def update_monthly(assumption, climate, variable):
    mask = df_dv["Assumption"].isin(assumption) & df_dv["Climate"].isin(climate)
    df = df_dv.loc[mask, :]
    endyr = df.index.max().year
    startyr = df.index.min().year

    df: pd.DataFrame = round(
        df.groupby(["Assumption"]).sum(numeric_only=True) / (endyr - startyr + 1)
    )
    df = df.reindex(ASSUMPTION_ORDER, level="Assumption")
    fig = px.bar(
        df,
        x=df.index.get_level_values(0),
        y=variable,
        color=df.index.get_level_values(0),
        text_auto=True,
        color_discrete_map=SCENARIO_COLORS,
    )
    fig.update_layout(
        legend_title="Scenario",
        barmode="relative",
        plot_bgcolor="white",
    )
    return fig
