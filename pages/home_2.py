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
    card_bar_plot_wy_vert
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

dcr_cover_path = "assets/final_dcr_2023_cover.png"

ta_card = CardWidget(
    "Total SWP Table A and Carryover Deliveries",
    button_id="table_a_btn",
    button_label="View Table A by Contractor",
    button_id2="ta_wet_dry",
    button_label2="Wet and Dry Periods",
    popover_label="table-a-info",
    popover_content=load_markdown("page_text/info-table-a.md"),
    chart=card_bar_plot_cy(df_dv, b_part="SWP_TA_CO_SOD"),
    text=None,
)
exp_card = CardWidget(
    "Total Banks SWP Exports",
    button_id="C_CAA003_SWP",
    button_label="Details",
    popover_label="exp-info",
    popover_content=load_markdown("page_text/info-swp-exports.md"),
    chart=card_bar_plot_wy_vert(df_dv, b_part="C_CAA003_SWP"),
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
                ],
            ),
        ],
    )
    return layout
