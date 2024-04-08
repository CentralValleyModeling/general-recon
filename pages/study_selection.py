from dash import html, register_page, dcc
import dash_bootstrap_components as dbc

register_page(
    __name__,
    #name='Page 2',
    top_nav=True,
    path='/study_selection'
)


def layout():
    layout = dbc.Container([

        dbc.Row([
            dbc.Col(
                [
                    dcc.Upload(id='upload-data',
                        children=html.Div([
                            'Connect to SQL Database ',
                            html.A('or Select DSS Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '120px',
                            'lineHeight': '120px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        }
                    ),
                    html.Button('Load', id='btn-load-study-1', n_clicks=0),
                    html.Div(id='dummy-div',children=[])
                ],
                width=6
            ),
        ])
    ])
    return layout