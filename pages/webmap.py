from dash import Dash, dcc, html, Input, Output, State, callback, register_page, ctx
import plotly.graph_objects as go
import dashboard_map.from_shp_to_dash as api
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# get the average annual sum of each delivery/agencyname
data_df = api.calc_mean()

# get a list of the scenarios for the dropdown
scenario_list = data_df["Scenario"].unique()

# get the geodata of the agencies
geodf = api.load_shp()

print(geodf['AREA'])
      
# reservoir geodf
reservoir_geodf = api.load_shp_reservoir()

# export geodf
export_geodf = api.load_shp_export()
print("EXPORT GEODF:")
print("columns = ", export_geodf.columns)
print("data = \n", export_geodf.head())
print("arc descrip column: /n", export_geodf["Comments"])

# choropleth map for exports
fig_exp = api.create_export_plot(export_geodf)

# centroid map for exports
fig_exp_centroid = api.create_export_centroid(export_geodf)

# upstream flows geodf
up_flows_geodf = api.load_shp_upstream_flows()

# choropleth map for upstream flows
fig_up_flows = api.create_up_flows_plot(up_flows_geodf)

# centroid map for upstream flows
fig_up_flows_centroid = api.create_up_flows_centroid(up_flows_geodf)

# Get the figure for the state border
figca = api.create_ca_plot()

# choropleth map for reservoirs
fig_r = api.create_reservoir_plot(reservoir_geodf)

# centroid map for reservoirs
fig_r_centroid = api.create_reservoir_centroid(reservoir_geodf)

# debug
fig_monthly = api.update_monthly("S_OROVL", (1922, 2021))

# Register the page webmap on the dashboard menu
register_page(
    __name__,
    name="Webmap",
    top_nav=True,
    path="/webmap",
)

# layout function
def layout():
    layout = dbc.Container(
        class_name="my-3",
        children=[
            dbc.Row(
                [
                    html.H1("State Water Project Contractor Deliveries"),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Label("Scenario 1:", htmlFor=("scenario_1")),
                                    dcc.Dropdown(
                                        scenario_list, scenario_list[0], id="scenario_1"
                                    ),
                                ],
                                # style={"width": "48%", "display": "inline-block"},
                            ),
                            html.Div(
                                [
                                    html.Label("Scenario 2:", htmlFor=("scenario_2")),
                                    dcc.Dropdown(
                                        scenario_list, scenario_list[1], id="scenario_2"
                                    ),
                                ],
                                # style={"width": "48%", "float": "right"},
                            ),
                            html.Div(
                                children=[
                                    html.Br(),
                                    html.Label("Map Filter"),
                                    dcc.Checklist(
                                        id='my_filter',
                                        options=['Reservoirs', 'Contractors', 'Exports', 'Upstream Flows'],
                                        value=['Reservoirs', 'Exports', 'Upstream Flows'],
                                    )
                                ]
                            ),
                            dcc.Graph(
                                id="my_id",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col([html.Div(id="my_charts")],
                        width=6,
                    )
                ]
            ),
        ],
    )

    return layout


# @callback(
#     Output("my_id", "figure"),
#     Output("my_charts", "children"),
#     Input("scenario_1", "value"),
#     Input("scenario_2", "value"),
#     Input("my_filter", "value")
# )
def update_graph(scen1: str, scen2: str, selected_values: list):
    # add variables for selected filter
    show_contractors = 'Contractors' in selected_values
    show_reservoirs = 'Reservoirs' in selected_values
    show_exports = 'Exports' in selected_values
    show_upstream_flows = 'Upstream Flows' in selected_values

    # Geo DataFrame to hold all necessary data
    scen_geodf = api.create_df_for_scen(data_df, geodf, scen1, scen2)

    # List to hold the all trace data
    trace2 = figca.data[0]
    graph_data = [trace2]

    if show_contractors:
        # Choropleth map to show % change of flow by agency
        fig = api.create_plot(scen_geodf)

        # Scatter graph to show positive & negative percentages
        fig1 = api.create_fig_1(scen_geodf)

        trace1 = fig.data[0]
        trace3 = fig1.data[0]
        graph_data.append(trace1)
        graph_data.append(trace3)
    
    if show_reservoirs:
        trace4 = fig_r.data[0]
        trace5 = fig_r_centroid.data[0]
        graph_data.append(trace4)
        graph_data.append(trace5)
    
    if show_exports:
        trace6 = fig_exp.data[0]
        trace7 = fig_exp_centroid.data[0]
        graph_data.append(trace6)
        graph_data.append(trace7)
    
    if show_upstream_flows:
        trace8 = fig_up_flows.data[0]
        trace9 = fig_up_flows_centroid.data[0]
        graph_data.append(trace8)
        graph_data.append(trace9)

    mycolor_scale = [
        [0, "#0000ff"],
        [0.1, "#3333ff"],
        [0.2, "#6666ff"],
        [0.3, "#9999ff"],
        [0.4, "#ccccff"],
        [0.5, "#ffffff"],
        [0.6, "#ffcccc"],
        [0.7, "#ff9999"],
        [0.8, "#ff6666"],
        [0.9, "#ff3333"],
        [1.0, "#ff0000"],
    ]

    layout = go.Layout(
        geo={"visible": False, "fitbounds": "locations"},
        autosize=False,
        height=1000,
        colorscale={"diverging": mycolor_scale},
        coloraxis={
            "cmin": -50,
            "cmax": 50,
            "cauto": False,
            "autocolorscale": False,
            "colorbar": {"title": {"text": "VAL DIFF %"}},
        },
    )
    # final_fig = go.Figure(data=[trace1, trace2, trace3, trace4], layout=layout)
    final_fig = go.Figure(graph_data, layout=layout)

    lat_min = 34.3
    lat_max = 40.2
    lat_center = (lat_min + lat_max) / 2

    final_fig.update_geos(
        center_lon=-119.3,
        center_lat=lat_center,
        lataxis_range=[lat_min, lat_max],
        lonaxis_range=[-124.7, -113.9],
        projection_scale=1,
        fitbounds=False,
    )

    final_fig.update_layout(
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=0, autoexpand=True),
        height=600,
        coloraxis_colorbar=dict(xref="paper", xanchor="right", x=1.2),
        uniformtext_minsize=8, 
        uniformtext_mode='hide'
    )

    return final_fig

# @callback(
#     Output("my_charts", "children"),
#     Input("my_id", "clickData"),
# )
def handle_click(custom_data):
    result = []
    if custom_data and len(custom_data) > 1:
        data_type = custom_data[-1]
        bpart = custom_data[0]

        result.append(html.H2("Annual Plot"))
        ex_fig = api.update_bar_annual(bpart, [1922, 2021])
        ex_dcc = dcc.Graph(figure=ex_fig)
        result.append(ex_dcc)

        result.append(html.H2("Monthly Plot"))
        res_fig = api.update_monthly(bpart, [1922, 2021])
        res_dcc = dcc.Graph(figure=res_fig)
        result.append(res_dcc)

        result.append(html.H2("Timeseries Plot"))
        contractor_fig = api.update_timeseries(bpart)
        contractor_dcc = dcc.Graph(figure=contractor_fig)
        result.append(contractor_dcc)

        # if data_type in ["CONTRACTORS", "RESERVOIRS", "EXPORTS"]:
        #     result.append(html.H2("Timeseries Plot"))
        #     contractor_fig = api.update_timeseries(bpart)
        #     contractor_dcc = dcc.Graph(figure=contractor_fig)
        #     result.append(contractor_dcc)
        # if data_type in ["RESERVOIRS", "EXPORTS"]:
        #     result.append(html.H2("Monthly Plot"))
        #     res_fig = api.update_monthly(bpart, [1922, 2021])
        #     res_dcc = dcc.Graph(figure=res_fig)
        #     result.append(res_dcc)
        # if data_type == "EXPORTS":
        #     result.append(html.H2("Annual Plot"))
        #     ex_fig = api.update_bar_annual(bpart, [1922, 2021])
        #     ex_dcc = dcc.Graph(figure=ex_fig)
        #     result.append(ex_dcc)
    return result

    # If the code reaches at this point, then there is no figure to update.
    # print("handle_click: No ClickData")
    # raise PreventUpdate

@callback(
    Output("my_id", "figure"),
    Output("my_charts", "children"),
    Input("my_id", "clickData"),
    Input("scenario_1", "value"),
    Input("scenario_2", "value"),
    Input("my_filter", "value")
)
def handle_change(clickData, scen1: str, scen2: str, selected_values: list):
    input_changed = ctx.triggered_id
    fig = update_graph(scen1, scen2, selected_values)
    fig.update_layout(uirevision=True)
    chart = [
        html.P("Please Click An Object On The Map To See Charts.",
                style={
                    "width": "80%", 
                    "display": "inline-block",
                    "height": "100vh",
                    "line-height": "100vh",
                    "text-align": "center"
                }
        )
    ]
    if input_changed == "my_id":
        if clickData:
            points = clickData["points"]
            if points:
                custom_data = points[0]["customdata"]
                chart = handle_click(custom_data)
    return fig, chart
