import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
from urllib.parse import urlencode, parse_qs

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout for each page
page1_layout = html.Div([
    html.H1('Page 1'),
    dbc.Button('Go to Page 2 with variable', id='navigate-button', n_clicks=0)
])

page2_layout = html.Div([
    html.H1('Page 2'),
    html.Div(id='variable-output'),
    dbc.Button('Go to Page 1', id='back-button', n_clicks=0)
])

# Define the overall app layout with a Location component
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

# Define the callback to control the page content
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'), Input('url', 'search')])
def display_page(pathname, search):
    if pathname == '/page-2':
        query_params = parse_qs(search.lstrip('?'))
        variable = query_params.get('variable', [''])[0]
        if variable == 'example_value':  # Add your validation logic here
            return html.Div([
                html.H1('Page 2'),
                html.Div(f'The passed variable is: {variable}', id='variable-output'),
                dbc.Button('Go to Page 1', id='back-button', n_clicks=0)
            ])
        else:
            return html.Div([
                html.H1('Page 2'),
                html.Div('Invalid variable passed. Ignoring query.', id='variable-output'),
                dbc.Button('Go to Page 1', id='back-button', n_clicks=0)
            ])
    else:
        return page1_layout

# Define the callback to change the URL and include a variable
@app.callback(Output('url', 'href'),
              [Input('navigate-button', 'n_clicks'),
               Input('back-button', 'n_clicks')])
def change_url_and_pass_variable(navigate_clicks, back_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return '/'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'navigate-button':
            variable = 'example_value'  # Example of a variable to pass
            url_params = urlencode({'variable': variable})
            return f'/page-2?{url_params}'
        elif button_id == 'back-button':
            return '/'
        else:
            return '/'

if __name__ == '__main__':
    app.run_server(debug=True)
