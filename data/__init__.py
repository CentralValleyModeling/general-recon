from pathlib import Path
from typing import Callable

import dash_bootstrap_components as dbc
from dash import dcc, html
from plotly.graph_objects import Figure

DATA_DIR = Path(__file__).parent
CHART_REGISTRY: dict[str, Callable[[], html.Div]] = {
    # key: value
    # component-id: callable that returns a plotly.graph_objects.Figure
}


def create_download_button(
    registry_id: str,
    chart: html.Div | Figure,
    button_text: str = "Download Data",
) -> dbc.Button:
    btn = dbc.Button(
        button_text,
        id=registry_id,
        rel="noopener",
        target="_blank",
    )
    CHART_REGISTRY[registry_id] = lambda *_: chart

    return btn


def load_markdown(
    file: str | Path,
    relative_to_data_dir: bool = True,
) -> dcc.Markdown:
    if relative_to_data_dir is True:
        p = DATA_DIR / file
    else:
        p = Path(file).resolve()

    if not p.exists():
        raise FileNotFoundError(p)

    with open(p, "r") as P:
        content = P.read()
    return dcc.Markdown(
        children=content,
        id=f"markdown-content-{p.stem}",
    )
