import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from navbar import create_navbar
from utils.tools import load_data_mult
#from pages.home import layout as create_home_layout
#from pages.hydrology import create_hydrology_layout

NAVBAR = create_navbar()
# To use Font Awesome Icons
FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "CalSim 3 Results Console"

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.SPACELAB,  # Dash Themes CSS
        FA621,  # Font Awesome Icons CSS
    ],
    title=APP_TITLE,
    use_pages=True,
    #pages_folder="pages"
)




app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1('SWP Delivery Capability Report 2023 Results Console (Beta)'),
    #html.Div(create_home_layout(app)),
    dbc.Row([
        dbc.Col(
            dcc.Link(f"{page['name']}", href=page["relative_path"]), width="auto"
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
],
style={'margin': '20px'}
)

#print(app)



server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


