from dash import html, register_page, dcc
from utils.query_data import df, scen_aliases, var_dict
import dash_bootstrap_components as dbc
from charts.chart_layouts import ann_bar_plot, mon_exc_plot, card_bar_plot

register_page(
    __name__,
    name='Home',
    top_nav=True,
    path='/'
)

dcr_cover_path = 'assets/draft_dcr_2023_cover.png'

title_text = ("""This Delivery Capability Report presents California Department of Water
Resources (DWR) analysis of the State Water Project (SWP) system and
provides important planning information for users of SWP water. The
analysis provides information about how changing climate, regulatory, and
operational considerations impact SWP delivery capability.""")

tablea_text = ("""Table A Water is an exhibit to the SWP's water supply contracts. The
maximum Table A amount is the basis for apportioning water supply and
costs to the SWP contractors. Once the total amount of water to be delivered
is determined for the year, all available water is allocated in proportion to
each contractor's annual maximum SWP Table A amount. Table A water is
given priority for delivery over other types of SWP water. Contractors have
several options for what to do with the water that is allocated to them: use
it, store it for later use, or transfer it to another contractor.""")

a21_text = ("""Article 21 Water (so named because it is described in Article 21 of the water
contracts) is water that SWP contractors may receive on intermittent,
interruptible basis in addition to their Table A water, if they request it. Article
21 water is used by many SWP contractors to help meet demands when
allocations are less than 100 percent. The availability and delivery of Article
21 water cannot impact the Table A allocation of the any contractor's water,
nor can it negatively impact normal SWP operations.""")

class CardWidget():
    def __init__(self,title,chart=None,text=None,image=None) -> None:
        self.title = title
        self.chart = chart #Div
        self.text = text
        self.image = image

    def create_card(self):

        card = dbc.Card(
            [
                dbc.CardImg(src=self.image, top=True),
                dbc.CardBody(
                    [
                        html.H4(self.title, className="card-title"),
                        self.chart,
                        html.P(self.text, className="card-text"),
                        dbc.Button("Explore", color="primary"),
                    ]
                ),
            ],
            #style={"width": "2rem"}
        )

        return card


ta_card = CardWidget("SWP Table A Deliveries",card_bar_plot(b_part="SWP_TA_TOTAL"))
a21_card = CardWidget("SWP Article 21 Deliveries")
a56_card = CardWidget("SWP Article 56 Deliveries")
exp_card = CardWidget("Total Banks Exports")
orovl_card = CardWidget("Oroville Carryover Storage")
sluis_card = CardWidget("San Luis Storage")


def layout():
    layout = html.Div([
        html.H2(["Results At-A-Glance"]),
        
        html.Hr(),
        #html.Div(card_bar_plot()),

        html.A(title_text),
                dbc.Row([
            dbc.Col([
                html.Img(src=dcr_cover_path, height="400"),
            ],width="auto"),
            dbc.Col([
                html.H3(["State Water Project Table A Deliveries"]),
                html.A(tablea_text),
            ]),
        ],style={'background-color': '#F9F9F9'}),

        html.Hr(),

        dbc.Row([

            dbc.Col([ 
                ta_card.create_card(),
            ]),
            dbc.Col([ 
                a21_card.create_card(),
            ]),
            dbc.Col([ 
                a56_card.create_card(),
            ]),
        ],style={'background-color': '#F2F2F2'}),
        dbc.Row([
            dbc.Col([ 
                exp_card.create_card(),
            ]),
            dbc.Col([ 
                orovl_card.create_card(),
            ]),
            dbc.Col([ 
                sluis_card.create_card(),
            ]),
        ],style={'background-color': '#F2F2F2'}),
        
        html.Hr(),


        

    ])
    return layout