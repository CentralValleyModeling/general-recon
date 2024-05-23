import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from navbar import create_navbar
from utils.tools import load_data_mult
#import dash_uploader as du

#from pages.study_selection import scenarios, var_dict, date_map

# Toggle the themes at [dbc.themes.LUX]
# The full list of available themes is:
# BOOTSTRAP, CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN,
# LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR,
# SPACELAB, SUPERHERO, UNITED, YETI, ZEPHYR.
# To see all themes in action visit:
# https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/

NAVBAR = create_navbar()
# To use Font Awesome Icons
FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "CalSim 3 Results Dashboard"

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.SPACELAB,  # Dash Themes CSS
        FA621,  # Font Awesome Icons CSS
    ],
    title=APP_TITLE,
    use_pages=True,  # New in Dash 2.7 - Allows us to register pages
)

app.layout = html.Div([
    html.H1('CalSim Results Dashboard'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


