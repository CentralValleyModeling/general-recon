from dash import html, register_page  #, callback # If you need callbacks, import it here.

register_page(
    __name__,
    #name='Page 4',
    top_nav=True,
    path='/summary'
)


def layout():
    layout = html.Div([
        html.H1(
            [
                "Summary"
            ]
        )
    ])
    return layout