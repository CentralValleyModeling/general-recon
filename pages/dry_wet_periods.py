import dash_bootstrap_components as dbc
from dash import dcc, html, register_page

from charts.chart_layouts import ta_dry_wet_barplot
from pages.styles import GLOBAL_MARGIN
from utils.query_data import df_dv, scen_aliases
from utils.tools import common_pers

register_page(
    __name__, name="TA Dry and Wet Periods", top_nav=True, path="/dry_wet_periods"
)

title_ta_dry_wet_text = (
    """This page shows % of Maximum Table A amount during select dry and wet periods
      included in the DCR 2023 Main Report.""",
    html.Br(),
    html.Br(),
)

drypers = [
    "Six Year Drought (1929-1934)",
    "Single Dry Year (1977)",
    "Two-Year Drought (1976-1977)",
    "Six Year Drought (1987-1992)",
    "Single Dry Year (2014)",
    "Two-Year Drought (2014-2015)",
]

wetpers = [
    "Single Wet Year (1983)",
    "Single Wet Year (1998)",
    #'Single Wet Year (2006)',
    "Two Year Wet Sequence (1982-1983)",
    "Four Year Wet Sequence (1980-1983)",
    "Six Year Wet Sequence (1978-1983)",
    "Ten Year Wet Sequence (1978-1987)",
    "Single Wet Year (2017)",
]
ta_periods_text = dbc.Row(
        [
            html.A(title_ta_dry_wet_text),
        ],
        class_name="m-3",
)

dry_pers = ta_dry_wet_barplot(
    df_dv, common_pers, bpart="SWP_TA_CO_SOD", scens=scen_aliases, perlist=drypers
)
wet_pers = ta_dry_wet_barplot(
    df_dv, common_pers, bpart="SWP_TA_CO_SOD", scens=scen_aliases, perlist=wetpers
)


def layout():
    layout = dbc.Container(
        [
            dbc.Row(
                [   
                    html.A(title_ta_dry_wet_text),
                    dcc.Markdown("### Table A % of Maximum Table A Amount - Dry Periods"),
                    dcc.Markdown(
                        "Estimated Dry-Period Percent of Maximum SWP, "
                        + "Table A Amount, 4,133 TAF/year, "
                        + "excluding Butte County, Yuba City, and Plumas County FCWCD."
                    ),
                    dcc.Graph(figure=dry_pers),
                    dcc.Markdown("### Table A % of Maximum Table A Amount - Wet Periods"),
                    dcc.Markdown(
                        "Estimated Wet-Period Percent of Maximum SWP, "
                        + "Table A Amount, 4,133 TAF/year, "
                        + "excluding Butte County, Yuba City, and Plumas County FCWCD."
                    ),
                    dcc.Graph(figure=wet_pers),
                ]
            )
        ]
    )
    return layout
