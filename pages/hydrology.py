import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, register_page

from charts.chart_layouts import CardWidget, card_bar_plot, card_mon_plot
from data import load_markdown, universal_data_download
from utils.query_data import df_sv

register_page(
    __name__,
    name="Hydrology",
    top_nav=True,
    path="/hydrology",
    order=1,
)

# Cards

hydrology_text = load_markdown("page_text/hydrology.md")

eight_ri_card_ann = CardWidget(
    "Eight River Index (April-July)",
    button_id=None,
    button_label=None,
    charts=card_bar_plot(df_sv, b_part="8RI", cy_wy="wy", cm=[4,5,6,7]),
    text=load_markdown("page_text/hydrology-8ri.md"),
)

sac_four_ri_card_ann = CardWidget(
    "Sacramento River Runoff (April-July)",
    button_id=None,
    button_label=None,
    charts=card_bar_plot(df_sv, b_part="SAC4", cy_wy="wy", cm=[4,5,6,7]),
    text=load_markdown("page_text/hydrology-sacramento-4ri.md"),
)

sjr_four_ri_card_ann = CardWidget(
    "San Joaquin River Runoff (April-July)",
    button_id=None,
    button_label=None,
    charts=card_bar_plot(df_sv, b_part="SJR4", cy_wy="wy", cm=[4,5,6,7]),
    text=load_markdown("page_text/hydrology-san-joaquin-4ri.md"),
)

orov_inflow_card_ann = CardWidget(
    "Oroville Reservoir Inflow (April-July)",
    button_id=None,
    button_label=None,
    charts=card_bar_plot(df_sv, b_part="OROVI", cy_wy="wy", cm=[4,5,6,7]),
    text="",
)

eight_ri_card_mon = CardWidget(
    "Eight River Index",
    button_id=None,
    button_label=None,
    charts=card_mon_plot(df_sv, b_part="8RI", yaxis_title="Eight River Index (TAF)"),
    text="",
)

sac_four_ri_card_mon = CardWidget(
    "Sacramento River Runoff",
    button_id=None,
    button_label=None,
    charts=card_mon_plot(
        df_sv, b_part="SAC4", yaxis_title="Sacramento River Runoff (TAF)"
    ),
    text="",
)

sjr_four_ri_card_mon = CardWidget(
    "San Joaquin River Runoff",
    button_id=None,
    button_label=None,
    charts=card_mon_plot(
        df_sv, b_part="SJR4", yaxis_title="San Joaquin River Runoff (TAF)"
    ),
    text="",
)

orov_inflow_card_mon = CardWidget(
    "Oroville Reservoir Inflow - All Years",
    button_id=None,
    button_label=None,
    charts=card_mon_plot(
        df_sv,
        b_part="OROVI",
        wyt=[1, 2, 3, 4, 5],
        yaxis_title="Oroville Reservoir Inflow (TAF)",
    ),
    text="""All Years (Sacramento Valley Index)""",
)

orov_inflow_card_drier_mon = CardWidget(
    "Oroville Reservoir Inflow - Drier Years",
    button_id=None,
    button_label=None,
    charts=card_mon_plot(
        df_sv, b_part="OROVI", wyt=[4, 5], yaxis_title="Oroville Reservoir Inflow (TAF)"
    ),
    text="""Dry and Critical years (Sacramento Valley Index)""",
)

orov_inflow_card_wetter_mon = CardWidget(
    "Oroville Reservoir Inflow - Wetter Years",
    button_id=None,
    button_label=None,
    charts=card_mon_plot(
        df_sv, b_part="OROVI", wyt=[1, 2], yaxis_title="Oroville Reservoir Inflow (TAF)"
    ),
    text="""Wet and Above Normal years (Sacramento Valley Index)""",
)


def layout():
    layout = dbc.Container(
        class_name="my-3",
        children=[
            dcc.Download(id="download-response-hydrology"),
            dbc.Col(
                [
                    html.A(hydrology_text),
                    dcc.Markdown("##### Summary climate and hydrologic metrics (change from current conditions) for selected scenarios"),
                    html.Img(src="/assets/hyd_assumptions_table.png",
                             alt="Hydrology Assumptions Table",
                             style={"width": "100%", "height": "auto"}
                    ),
                    html.P(
                        [
                            html.Sup("a"),
                            " Change in extreme precipitation is modeled using Clausius-Clapeyron scaling of 7% per degree Celsius (WGEN reference). "
                            "As the atmosphere warms, the largest precipitation events (above the 99th percentile) are expected to grow larger. "
                            "The percent increase value represents the change in daily precipitation of events above the 99th percentile. "
                            "Events below the 99th percentile are also scaled (usually downward) to fit within the overall metric of average precipitation change.",
                            html.Br(),
                            html.Sup("b"),
                            " See SWP Climate Adaptation Plan Appendix A: Modeling Assumptions for additional analysis and documentation of "
                            "snow water equivalent and snow-covered area evaluations."
                        ],
                        style={"fontSize": "0.8rem", "marginTop": "0.5rem", "color": "#555"}
                    ),
                    html.Hr(style={"margin": "0.5rem 0"}),
                    dbc.Row(
                        [
                            dbc.Col(eight_ri_card_ann.create_card(height="25rem")),
                            dbc.Col(sac_four_ri_card_ann.create_card(height="25rem")),
                            html.Hr(style={"margin": "0.5rem 0"}),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(sjr_four_ri_card_ann.create_card(height="25rem")),
                            dbc.Col(orov_inflow_card_ann.create_card(height="25rem")),
                            html.Hr(style={"margin": "0.5rem 0"}),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                eight_ri_card_mon.create_card(
                                    registry_id="monthly-8RI",
                                )
                            ),
                            dbc.Col(
                                sac_four_ri_card_mon.create_card(
                                    registry_id="monthly-sacramento-4RI",
                                )
                            ),
                            html.Hr(style={"margin": "0.5rem 0"}),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                sjr_four_ri_card_mon.create_card(
                                    registry_id="monthly-san-joaquin-4RI",
                                )
                            ),
                            dbc.Col(
                                orov_inflow_card_mon.create_card(
                                    registry_id="monthly-oroville-inflow",
                                )
                            ),
                            html.Hr(style={"margin": "0.5rem 0"}),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                orov_inflow_card_drier_mon.create_card(
                                    registry_id="monthly-oroville-inflow-dry",
                                )
                            ),
                            dbc.Col(
                                orov_inflow_card_wetter_mon.create_card(
                                    registry_id="monthly-oroville-inflow-wet",
                                )
                            ),
                            html.Hr(style={"margin": "0.5rem 0"}),
                        ]
                    ),
                ],
            ),
        ],
    )
    return layout


# Callbacks
@callback(
    Output("download-response-hydrology", "data"),
    Input("monthly-8RI", "n_clicks"),
    Input("monthly-sacramento-4RI", "n_clicks"),
    Input("monthly-san-joaquin-4RI", "n_clicks"),
    Input("monthly-oroville-inflow", "n_clicks"),
    Input("monthly-oroville-inflow-dry", "n_clicks"),
    Input("monthly-oroville-inflow-wet", "n_clicks"),
    prevent_initial_call=True,
)
def home_data_download(*args):
    return universal_data_download()
