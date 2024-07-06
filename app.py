import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = 'SWP Delivery Capability Report 2023 Results Console (ReCon)'
CS3_ICON = 'assets/cs3_icon_draft.png'

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


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page['name'], href=page["relative_path"])) for page in dash.page_registry.values()
    ],
    color="light",
    dark=False,
    className="mb-0",
)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Markdown("# ![](/assets/cs3_icon_draft.png) SWP Delivery Capability Report 2023 Results Console (ReCon)"),
    navbar,
    #html.Div(create_home_layout(app)),
    #dbc.Row([
    #    dbc.Col(
    #        dcc.Link(f"{page['name']}", href=page["relative_path"]), width="auto"
    #    ) for page in dash.page_registry.values()
    #]),
    dash.page_container
],
style={'margin': '20px'}
)

#print(app)



server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


