import dash_bootstrap_components as dbc
from dash import dcc, html, register_page

from data import load_markdown
from pathlib import Path


#register_page(
#    __name__,
#    name="Model Assumptions",
#    top_nav=True,
#    path="/assumptions",
#    order=99,
#)

modeling_assumptions = load_markdown("page_text/modeling_assumptions.md")
md_path = Path("data/page_text/modeling_assumptions.md")

def layout():
    with open(md_path, "r") as f:
        markdown_content = f.read()

    layout = dbc.Container(
        class_name="my-3",
        children=[
            dbc.Col(
                [   
                    dcc.Markdown("### Assumptions Table"),
                    html.Img(src="/assets/assumptions_table.png", alt="Assumptions Table"),
                    dcc.Markdown(markdown_content, dangerously_allow_html=True),
                ]
            ),
        ],
    )
    return layout
