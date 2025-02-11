from urllib.parse import urlencode

import dash_bootstrap_components as dbc
from dash import (
    ALL,
    Input,
    Output,
    callback,
    callback_context,
    dcc,
    html,
    register_page,
)

from charts.chart_layouts import (
    CardWidget, card_bar_plot_cy, 
    card_mon_exc_plot, 
    card_bar_plot_wy_vert,
    cap_scenario_card
)

from data import load_markdown, universal_data_download
from utils.query_data import df_dv

register_page(
    __name__,
    name="Home",
    top_nav=True,
    path="/",
    title="Results Console",
    order=0,
)

CLIMATE_ORDER = ["Historical",
                 "2043_CC50",
                 "2043_CC95",
                 "2085_CC50",
                 "2085_CC75"
                ]

exp_card = CardWidget(
    "Total Delta Exports (TAF/year)",
    button_id="EXPORTACTUALTDIF",
    button_label="Drilldown",
    popover_label="exp-info",
    popover_content=load_markdown("page_text/info-total-exports.md"),
    charts=card_bar_plot_wy_vert(df_dv, b_part="EXPORTACTUALTDIF", climate_order=CLIMATE_ORDER),
)

ta_card = CardWidget(
    "SWP Table A Deliveries (TAF/year)",
    button_id="C_CAA003_SWP",
    button_label="Drilldown",
    popover_label="ta-info",
    popover_content=load_markdown("page_text/info-table-a.md"),
    charts=card_bar_plot_wy_vert(df_dv, b_part="SWP_TA_CO_SOD", climate_order=CLIMATE_ORDER),
)

ndoi_card = CardWidget(
    "Total Delta Outflow (TAF/year)",
    button_id="NDOI",
    button_label="Drilldown",
    popover_label="ndoi-info",
    popover_content=load_markdown("page_text/info-ndoi.md"),
    charts=card_bar_plot_wy_vert(df_dv, b_part="NDOI", climate_order=CLIMATE_ORDER),
)

scen_card = CardWidget(
    "Scenario Card",
    button_id="C_CAA003_SWP",
    button_label="Details",
    popover_label="exp-info",
    popover_content=load_markdown("page_text/info-swp-exports.md"),
    charts=cap_scenario_card(df_dv, b_part="SWP_TA_TOTAL", climate_order=CLIMATE_ORDER),
)

orovl_sep_card = CardWidget(
    "Oroville End-of-September Storage",
    button_id="S_OROVL",
    button_label="Details",
    charts=card_mon_exc_plot(df_dv, b_part="S_OROVL", monthchecklist=["Sep"]),
)

def layout():
    layout = dbc.Container(
        id="home-container",
        class_name="my-3",
        children=[
            dcc.Download(id="download-response-home"),
            dbc.Row(),
            html.Hr(),
            dbc.Col(
                id="home-cards",
                className="d-grid gap-2",
                children=[
                    dbc.Row(
                        id="home-cards-row-0",
                        children=[
                            dbc.Col(
                                class_name="col-md-12", children=[exp_card.create_card()]
                            ),
                        ],
                    ),
                    dbc.Row(
                        id="home-cards-row-0",
                        children=[
                            dbc.Col(
                                class_name="col-md-12", children=[ta_card.create_card()]
                            ),
                        ],
                    ),
                    dbc.Row(
                        id="home-cards-row-0",
                        children=[
                            dbc.Col(
                                class_name="col-md-12", children=[ndoi_card.create_card()]
                            ),
                        ],
                    ),
#                    dbc.Row(
#                        id="home-cards-row-0",
#                        children=[
#                            dbc.Col(
#                                class_name="col-md-12", children=[scen_card.create_card()]
#                            ),
#                        ],
#                    ),                   
                ],
            ),
        ],
    )
    return layout
