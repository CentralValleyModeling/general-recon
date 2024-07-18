from typing import Callable

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, callback_context, dcc, html, no_update
from plotly.graph_objects import Figure

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


def find_figure_in_div(obj: html.Div) -> Figure | None:
    for o in obj.children:
        if isinstance(o, Figure):
            return o
        elif isinstance(o, dcc.Graph):
            return o.figure
        elif hasattr(o, "children"):
            fig = find_figure_in_div(o)
            if fig is not None:
                return fig
    return None  # Nothing found


def create_dataframe_from_fig(fig: Figure) -> pd.DataFrame:
    frames = list()
    for data in fig.data:
        if data["mode"] == "lines":
            df = pd.DataFrame(
                data={data["name"]: data["y"], "X": data["x"]},
            )
            df = df.set_index("X")
            frames.append(df)
        else:
            raise NotImplementedError(
                f"figure trace mode not supported: {data['mode']}"
            )
    return pd.concat(frames, axis=1, join="outer").sort_index()


@callback(
    Output("download-response", "data"),
    Input("oroville-sept-exceedance", "n_clicks"),
    Input("oroville-may-exceedance", "n_clicks"),
    Input("sluis-exceedance", "n_clicks"),
    Input("swp-alloc-exceedance", "n_clicks"),
    prevent_initial_call=True,
)
def universal_data_download(*args):
    _id = callback_context.triggered_id
    if _id not in CHART_REGISTRY:
        print(f"Button(id={_id}) is not registered in the CHART_REGISTRY")
        return no_update
    div = CHART_REGISTRY[_id]()
    fig = find_figure_in_div(div)
    if fig is None:
        print(f"Could not find a Figure in Div for Button(id={_id})")
        return no_update
    df = create_dataframe_from_fig(fig)
    return dcc.send_data_frame(df.to_csv, f"{_id}.csv")
