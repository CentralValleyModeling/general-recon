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

sac_four_ri_card_ann = CardWidget("Sacramento River Runoff",
                     button_id=None,
                     button_label=None,
                     chart=card_bar_plot(df_sv,b_part="SAC4"),
                     height="30rem",
                     text="")

sjr_four_ri_card_ann = CardWidget("San Joaquin River Runoff",
                     button_id=None,
                     button_label=None,
                     chart=card_bar_plot(df_sv,b_part="SJR4"),
                     height="30rem",                    
                     text="")

eight_ri_card_mon = CardWidget("Eight River Index",
                     button_id=None,
                     button_label=None,
                     chart=card_mon_plot(df_sv,b_part="8RI",yaxis_title = "Eight River Index (TAF)"),
                     height="35rem",
                     text="Eight River Index is the sum of Sacramento River Runoff and San Joaquin River Runoff")

sac_four_ri_card_mon = CardWidget("Sacramento River Runoff",
                     button_id=None,
                     button_label=None,
                     chart=card_mon_plot(df_sv,b_part="SAC4", yaxis_title = "Sacramento River Runoff (TAF)"),
                     height="35rem",
                     text="""Sacramento River Runoff is the sum of Sacramento River at Bend Bridge, 
                        Feather River inflow to Lake Oroville, Yuba River at Smartville, 
                        and American River inflow to Folsom Lake.""")

sjr_four_ri_card_mon = CardWidget("San Joaquin River Runoff",
                     button_id=None,
                     button_label=None,
                     chart=card_mon_plot(df_sv,b_part="SJR4", yaxis_title = "San Joaquin River Runoff (TAF)"),
                     height="35rem",
                     text="""San Joaquin River Runoff is the sum of Stanislaus River inflow to New Melones
                        Lake, Tuolumne River inflow to New Don Pedro Reservoir, Merced River inflow
                        to Lake McClure, and San Joaquin River inflow to Millerton Lake""")
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
