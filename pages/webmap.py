from dash import Dash, dcc, html, Input, Output, State, callback, register_page, ctx
import plotly.graph_objects as go
import dashboard_map.from_shp_to_dash as api
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


# get a list of the scenarios for the dropdown
scenario_list = api.get_scenarios()

# choropleth map for exports
fig_exp = api.create_choropleth_plot('exports')

# centroid map for exports
fig_exp_centroid = api.create_centroid_plot('exports', centroid_color='rgb(251, 184, 32)')

# choropleth map for upstream flows
fig_up_flows = api.create_choropleth_plot('up_flows')

# centroid map for upstream flows
fig_up_flows_centroid = api.create_centroid_plot('up_flows', centroid_color='rgb(0, 93, 131)')

# Get the figure for the state border
figca = api.create_ca_plot()

# choropleth map for reservoirs
fig_r = api.create_choropleth_plot('reservoirs', ("CALSIMNAME", "TABLENAME", "DATA_TYPE"))

# centroid map for reservoirs
fig_r_centroid = api.create_centroid_plot('reservoirs', custom_data=("CALSIMNAME", "TABLENAME", "DATA_TYPE"), centroid_color='rgb(141, 198, 63)')

# map for main rivers

fig_river_sj = api.create_line_plot("san_joaq_river", line_color='rgb( 37, 170, 225)')

fig_river_amer = api.create_line_plot("amer_river", line_color='rgb( 37, 170, 225)')

fig_river_feath = api.create_line_plot("feath_river", line_color='rgb( 37, 170, 225)')

fig_river_sac = api.create_line_plot("sac_river", line_color='rgb( 37, 170, 225)')

# choropleth map for pools
fig_p = api.create_choropleth_plot('pools', ("BPART","AssetReg_2", "DATA_TYPE"))

# centroid map for reservoirs
fig_p_centroid = api.create_centroid_plot('pools', custom_data=("BPART","AssetReg_2", "DATA_TYPE"), centroid_color='rgb(109, 129, 150)')

# map for aqueducts
fig_aqueducts = api.create_line_plot(
    "aqueducts", 
    line_color='rgb(192, 192, 192)',
    data_filter = (
        lambda g: g.dropna(subset=["Branch"]),
        lambda g: g[g["Branch"].str.contains('Aqueduct')]
    )
)

# centroid map for delta outflows
fig_del_outflows = api.create_del_outflows_centroid()

# list of NDOI bparts
ndoi_bparts = ["NDOI", "NDOI_ADD", "NDOI_ADD_ANN", "NDOI_ADD_CVP", "NDOI_ADD_SWP", "NDOI_MIN", "DELTAINFLOWFORNDOI"]

# Register the page webmap on the dashboard menu
register_page(
    __name__,
    name="Webmap",
    top_nav=True,
    path="/webmap",
)


graph_modal = html.Div([
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("")),
            dbc.ModalBody([html.Div(id="my_charts")]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)
            ),
        ],
        id="graph_modal",
        is_open=False,
        size="lg",
        style={'margin-left': '50px', 'margin-right': '50px'},
        scrollable=True
    )
])

# layout function
def layout():
    layout = html.Div([
        graph_modal,
        html.Div([html.H1("CalSim Webmap")]),
        html.Div([
            html.Div(
                [
                    html.Label("Scenario 1:", htmlFor=("scenario_1"), style={'margin-right': '15px', 'font-weight': 'bold'}),
                    dcc.Dropdown(
                        scenario_list, scenario_list[0], id="scenario_1", style={'flex-grow': '1'}
                    ),
                ], style={'display': 'flex', 'flex': '1', 'margin-right': '30px'}
            ),
            html.Div(
                [
                    html.Label("Scenario 2:", htmlFor=("scenario_2"), style={'margin-right': '15px', 'font-weight': 'bold'}),
                    dcc.Dropdown(
                        scenario_list, scenario_list[1], id="scenario_2",
                        style={'flex-grow': '1'}
                    ),
                ], style={'display': 'flex', 'flex': '1'},
            ),
        ], style={'display': 'none', 'gap': '10px'}, id='drop_container'),
        html.Div(
            children=[
                html.Label("Map Filter:", style={'font-weight': 'bold'}),
                dcc.Checklist(
                    id='my_filter',
                    options=[
                        {
                            "label": [
                                html.Span("Reservoirs"),
                                html.Img(src="/assets/green_circle.png", style={"height": "10px", "marginLeft": "5px"})
                            ],
                            "value": "Reservoirs"
                        },
                        {
                            "label": [
                                html.Span("Contractors")
                            ],
                            "value": "Contractors"
                        },
                        {
                            "label": [
                                html.Span("Exports"),
                                html.Img(src="/assets/yellow_circle.png", style={"height": "10px", "marginLeft": "5px"})
                            ],
                            "value": "Exports"
                        },
                        {
                            "label": [
                                html.Span("Flows"),
                                html.Img(src="/assets/blue_circle.png", style={"height": "10px", "marginLeft": "5px"})
                            ],
                            "value": "Flows"
                        },
                        {
                            "label": [
                                html.Span("Conveyance"),
                                html.Img(src="/assets/gray_circle.png", style={"height": "10px", "marginLeft": "5px"})
                            ],
                            "value": "Pools"
                        },
                    ],
                    value=['Reservoirs', 'Exports', 'Flows', 'Pools'],
                style={'display': 'flex', 'gap': '10px', 'justify-content' : 'space-between', 'flex-grow': '1'}
                ), 
            ], style={'display': 'flex', 'gap': '10px', 'padding-top': '20px', 'padding-bottom': '20px'},
        ),
        dcc.Graph(id="my_id", config={"scrollZoom": True}),
    ])

    return layout


@callback(
    Output("drop_container", "style"),
    Input("my_filter", "value"),
    prevent_initial_call=True
)
def filter_to_drop(selected_values):
    if 'Contractors' in selected_values:
        return {'display': 'flex', 'gap': '10px'}
    return {'display': 'none', 'gap': '10px'}


def update_graph(scen1: str, scen2: str, selected_values: list):
    # add variables for selected filter
    show_contractors = 'Contractors' in selected_values
    show_reservoirs = 'Reservoirs' in selected_values
    show_exports = 'Exports' in selected_values
    show_flows = 'Flows' in selected_values
    show_pool = 'Pools' in selected_values

    final_fig = go.Figure(
        layout=dict(
            mapbox=dict(
                style="carto-positron",
                center={"lon": -122.0, "lat": 38.0},
                zoom=6.3
            ),
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
            height=800,
        )
    )

    final_fig.add_trace(figca.data[0])

    # adding main rivers to california border map
    trace_river_sj = fig_river_sj.data[0]
    trace_river_amer = fig_river_amer.data[0]
    trace_river_feath = fig_river_feath.data[0]
    trace_river_sac = fig_river_sac.data[0]

    final_fig.add_trace(trace_river_sj)
    final_fig.add_trace(trace_river_amer)
    final_fig.add_trace(trace_river_feath)
    final_fig.add_trace(trace_river_sac)

    # add the aqueducts
    final_fig.add_trace(fig_aqueducts.data[0])

    # add contractors if selected
    if show_contractors:
        # Choropleth map to show % change of flow by agency
        fig = api.create_contractor_plot(scen1, scen2)

        # Scatter graph to show positive & negative percentages
        fig1 = api.create_contractor_centroid(scen1, scen2)

        trace1 = fig.data[0]
        trace3 = fig1.data[0]
        final_fig.add_trace(trace1)
        final_fig.add_trace(trace3)
    
    # add reservoirs if selected
    if show_reservoirs:
        trace4 = fig_r_centroid.data[0]
        final_fig.add_trace(trace4)
    
    # add exports if selected
    if show_exports:
        trace6 = fig_exp.data[0]
        trace7 = fig_exp_centroid.data[0]
        final_fig.add_trace(trace6)
        final_fig.add_trace(trace7)
    
    # add upstream flows if selected
    if show_flows:
        trace8 = fig_up_flows.data[0]
        trace9 = fig_up_flows_centroid.data[0]
        final_fig.add_trace(trace8)
        final_fig.add_trace(trace9)
        final_fig.add_trace(fig_del_outflows.data[0])
    
    # add pools
    if show_pool:
        trace10 = fig_p.data[0]
        trace11 = fig_p_centroid.data[0]
        final_fig.add_trace(trace10)
        final_fig.add_trace(trace11)
 
    final_fig.update_layout(
        map_style='outdoors',
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
        map_center={'lon': -122.0, 'lat': 38.0},
        map_zoom=6.3,
        height=800,
        coloraxis={
            "colorscale": [
                [0.0, "#b2182b"],   # dark red
                [0.35, "#ef8a62"],  # lighter red
                [0.48, "#fddbc7"],  # soft tan
                [0.50, "#f7f7f7"],  # near white
                [0.52, "#d1e5f0"],  # light blue
                [0.65, "#67a9cf"],  # medium blue
                [1.0, "#2166ac"]    # dark blue
            ],
            "cmin": -50,
            "cmax": 50,
            "cmid": 0,
            "cauto": False,
            "colorbar": {"title": {"text": "VAL DIFF %"}},
        }
    )

    return final_fig


def generate_graph(custom_data):
    result = []
    if custom_data and len(custom_data) > 1:
        data_type = custom_data[-1]
        bpart = custom_data[0]
        if data_type != "RESERVOIRS":
            result.append(html.H2("Annual Plot"))
            try:
                ex_fig = api.update_bar_annual(bpart, (1922, 2021))
                ex_dcc = dcc.Graph(figure=ex_fig)
                result.append(ex_dcc)
            except:
                ex_fig = go.Figure()
                ex_fig.update_layout(
                    margin={'r': 0, 't': 0, 'l': 0, 'b': 10},
                    xaxis = {"visible": False},
                    yaxis = {"visible": False},
                    annotations = [
                        {
                            "text": "No Data Available",
                            "xref": "paper",
                            "yref": "paper",
                            "showarrow": False,
                            "font": {"size": 28}
                        }
                    ]
                )
                ex_dcc = dcc.Graph(figure=ex_fig)
                result.append(ex_dcc)

        result.append(html.H2("Monthly Plot"))
        try:
            res_fig = api.update_monthly(bpart, (1922, 2021))
            res_dcc = dcc.Graph(figure=res_fig)
            result.append(res_dcc)
        except:
            res_fig = go.Figure()
            res_fig.update_layout(
                margin={'r': 0, 't': 0, 'l': 0, 'b': 10},
                xaxis = {"visible": False},
                yaxis = {"visible": False},
                annotations = [
                    {
                        "text": "No Data Available",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 28}
                    }
                ]
            )
            res_dcc = dcc.Graph(figure=res_fig)
            result.append(res_dcc)


        result.append(html.H2("Timeseries Plot"))
        try:
            contractor_fig = api.update_timeseries(bpart)
            contractor_dcc = dcc.Graph(figure=contractor_fig)
            result.append(contractor_dcc)
        except:
            contractor_fig = go.Figure()
            contractor_fig.update_layout(
                margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                xaxis = {"visible": False},
                yaxis = {"visible": False},
                annotations = [
                    {
                        "text": "No Data Available",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 28}
                    }
                ]
            )
            contractor_dcc = dcc.Graph(figure=contractor_fig)
            result.append(contractor_dcc)
        
        result.append(html.H2("Monthly Exceedance Plot"))
        try:
            ex_fig = api.update_monthly_exc(bpart, (1922, 2021))
            ex_dcc = dcc.Graph(figure=ex_fig)
            result.append(ex_dcc)
        except:
            ex_fig = go.Figure()
            ex_fig.update_layout(
                margin={'r': 0, 't': 0, 'l': 0, 'b': 10},
                xaxis = {"visible": False},
                yaxis = {"visible": False},
                annotations = [
                    {
                        "text": "No Data Available",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 28}
                    }
                ]
            )
            ex_dcc = dcc.Graph(figure=ex_fig)
            result.append(ex_dcc)

    return result


@callback(
    Output("my_id", "figure"),
    Input("my_id", "clickData"),
    Input("scenario_1", "value"),
    Input("scenario_2", "value"),
    Input("my_filter", "value"),
    prevent_initial_call=False
)
def handle_change(clickData, scen1: str, scen2: str, selected_values: list):
    input_changed = ctx.triggered_id
    fig = update_graph(scen1, scen2, selected_values)
    fig.update_layout(uirevision=True)
    return fig


@callback(
    Output("ndoi_graph_id", "children"),
    Input("del_out_bpart", "value"),
    prevent_initial_call=True
)
def handle_ndoi_selection(bpart):
    return generate_graph([bpart, "FLOW"])


@callback(
    Output("graph_modal", "is_open"),
    Output("my_id", "clickData"),
    Output("my_charts", "children"),
    Input("my_id", "clickData"),
    Input("close", "n_clicks"),
    State("graph_modal", "is_open"),
    prevent_initial_call=True
)
def handle_graph_click(clickData, n1, is_open):
    if is_open:
        return False, None, None
    else:
        if clickData:
            points = clickData["points"]
        else:
            return False, clickData, None

        if points and "customdata" in points[0]:
            custom_data = points[0]["customdata"]
            bpart = custom_data[0]
            if bpart == "NDOI":
                results = []
                results.append(dcc.Dropdown(ndoi_bparts, ndoi_bparts[0], id="del_out_bpart"))
                chart = generate_graph(custom_data)
                div = html.Div(children=chart, id="ndoi_graph_id")
                results.append(div)
                return True, None, results
            else:
                chart = generate_graph(custom_data)
                return True, None, chart
            

    return False, None, None
