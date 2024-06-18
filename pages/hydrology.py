from dash import html, register_page, dcc, Input, Output, ALL, callback, callback_context, page_registry
from utils.query_data import df, scen_aliases, var_dict
import dash_bootstrap_components as dbc
from charts.chart_layouts import ann_bar_plot, card_mon_exc_plot, card_bar_plot, CardWidget
from urllib.parse import urlencode, parse_qs
from pages.styles import GLOBAL_MARGIN

register_page(
    __name__,
    name='Hydrology',
    top_nav=True,
    path='/hydrology'
)


ta_card = CardWidget("Total SWP Table A Deliveries",
                     button_id="table_a_btn",
                     button_label="View by Contractor",
                     chart=card_bar_plot(b_part="SWP_TA_TOTAL"),
                     text="Hi")



def layout():
    layout = html.Div([
        html.H2(["Hydrology Comparison"]),

    ],
    style=GLOBAL_MARGIN
    )
    return layout
