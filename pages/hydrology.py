from dash import html, register_page, dcc, Input, Output, ALL, callback, callback_context, page_registry
import dash_bootstrap_components as dbc
from charts.chart_layouts import ann_bar_plot, card_mon_exc_plot, card_bar_plot, card_mon_plot, CardWidget
from urllib.parse import urlencode, parse_qs
from pages.styles import GLOBAL_MARGIN
from utils.query_data import df_sv, scen_aliases, var_dict

register_page(
    __name__,
    name='Hydrology',
    top_nav=True,
    path='/hydrology'
)

# Cards

eight_ri_card_ann = CardWidget("Eight River Index",
                     button_id=None,
                     button_label=None,
                     chart=card_bar_plot(df_sv,b_part="8RI"),
                     height="30rem",
                     text="")

sac_four_ri_card_ann = CardWidget("Sac Four River Index",
                     button_id=None,
                     button_label=None,
                     chart=card_bar_plot(df_sv,b_part="SAC4"),
                     height="30rem",
                     text="")

sjr_four_ri_card_ann = CardWidget("SJR Four River Index",
                     button_id=None,
                     button_label=None,
                     chart=card_bar_plot(df_sv,b_part="SJR4"),
                     height="30rem",                    
                     text="")

eight_ri_card_mon = CardWidget("Eight River Index - Monthly Average",
                     button_id=None,
                     button_label=None,
                     chart=card_mon_plot(df_sv,b_part="8RI",yaxis_title = "Eight River Index (TAF)"),
                     height="30rem",
                     text="")

sac_four_ri_card_mon = CardWidget("Sacramento Four River Index - Monthly Average",
                     button_id=None,
                     button_label=None,
                     chart=card_mon_plot(df_sv,b_part="SAC4"),
                     height="30rem",
                     text="")

sjr_four_ri_card_mon = CardWidget("San Joaquin Four River Index - Monthly Average",
                     button_id=None,
                     button_label=None,
                     chart=card_mon_plot(df_sv,b_part="SJR4"),
                     height="30rem",
                     text="")
# Layout

def layout():
    layout = html.Div([
        html.H2(["Hydrology Comparison"]),
        dbc.Row([
            dbc.Col([eight_ri_card_ann.create_card(),]),
            dbc.Col([sac_four_ri_card_ann.create_card(),]),
            dbc.Col([sjr_four_ri_card_ann.create_card(),]),
        ]),
            eight_ri_card_mon.create_card(),
            sac_four_ri_card_mon.create_card(),
            sjr_four_ri_card_mon.create_card(),


    ],
    style=GLOBAL_MARGIN
    )
    return layout
