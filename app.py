import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "SWP Climate Adaptation Plan Dashboard"
CS3_ICON = "assets/cs3_icon_draft.png"


class ReconNavbarBrand(dbc.NavbarBrand):
    def __init__(self, label: str, **kwargs):
        img = html.Img(
            src=str(CS3_ICON),
            height="30px",
        )
        label = dbc.NavbarBrand(label, className="m-0")
        children = dbc.Row(
            [
                dbc.Col(img),
                dbc.Col(label),
            ],
            align="center",
            className="g-2",
        )
        # Update kwargs
        kwargs = {
            "href": "/",
            "children": children,
            "style": {
                "textDecoration": "none",
                "margin": "0",
            },
        } | kwargs
        super().__init__(**kwargs)


app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.SPACELAB,  # Dash Themes CSS
        FA621,  # Font Awesome Icons CSS
    ],
    title=APP_TITLE,
    use_pages=True,
)

pages = [
    dbc.NavItem(dbc.NavLink(page["name"], href=page["relative_path"]))
    for page in dash.page_registry.values()
]

navbar = dbc.NavbarSimple(
    brand=ReconNavbarBrand("SWP Climate Adaptation Plan"),
    children=pages,
    color="light",
    dark=False,
    className="mb-0 flex-shrink-0",
)

# The default page_container does not allow for flexboxes to fill the vertical
# space on a page because of a div without an id, the below code re-creates what
# the page_container div is, and adds an "id=parent_page_content" to that node.
# The solution was taken from the discussion below:
# https://community.plotly.com/t/adjust-height-of-page-container/73029/3
dash.page_container = html.Div(
    [
        dcc.Location(id="_pages_location", refresh="callback-nav"),
        html.Div(id="_pages_content", disable_n_clicks=True, style={"height": "100%"}),
        dcc.Store(id="_pages_store"),
        html.Div(id="_pages_dummy", disable_n_clicks=True),
    ],
    style={"height": "100%"},
    id="parent_page_content",
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        dbc.Container(
            dash.page_container, fluid=True, className="flex-grow-1 d-flex flex-column"
        ),
    ],
    className="vh-100 d-flex flex-column",
)

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
