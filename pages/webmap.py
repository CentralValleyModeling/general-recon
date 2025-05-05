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

# map for main rivers
fig_river_sj = api.create_river_plot("dashboard_map/san_joaquin_river.shp", "San Joaquin River")

fig_river_amer = api.create_river_plot("dashboard_map/american_river.shp", "American River")

fig_river_feath = api.create_river_plot("dashboard_map/feather_river.shp", "Feather River")

fig_river_sac = api.create_river_plot("dashboard_map/sacramento_river.shp", "Sacramento River")


# debug
fig_monthly = api.update_monthly("S_OROVL", (1922, 2021))

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
                            ),
                            html.Div(
                                [
                                    html.Label("Scenario 2:", htmlFor=("scenario_2")),
                                    dcc.Dropdown(
                                        scenario_list, scenario_list[1], id="scenario_2"
                                    ),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Br(),
                                    html.Label("Map Filter"),
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
                                                    html.Span("Upstream Flows"),
                                                    html.Img(src="/assets/blue_circle.png", style={"height": "10px", "marginLeft": "5px"})
                                                ],
                                                "value": "Upstream Flows"
                                            },
                                        ],
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

def update_graph(scen1: str, scen2: str, selected_values: list):
    # add variables for selected filter
    show_contractors = 'Contractors' in selected_values
    show_reservoirs = 'Reservoirs' in selected_values
    show_exports = 'Exports' in selected_values
    show_upstream_flows = 'Upstream Flows' in selected_values

    # create an empty figure and add ca state border
    final_fig = go.Figure()
    final_fig.add_trace(figca.data[0])

    # add contractors if selected
    if show_contractors:
        # Geo DataFrame to hold all necessary data
        scen_geodf = api.create_df_for_scen(data_df, geodf, scen1, scen2)

        # Choropleth map to show % change of flow by agency
        fig = api.create_plot(scen_geodf)

        # Scatter graph to show positive & negative percentages
        fig1 = api.create_fig_1(scen_geodf)

        trace1 = fig.data[0]
        trace3 = fig1.data[0]
        final_fig.add_trace(trace1)
        final_fig.add_trace(trace3)
    
    # add reservoirs if selected
    if show_reservoirs:
        trace4 = fig_r_centroid.data[0]
        trace5 = fig_r.data[0]
        final_fig.add_trace(trace4)
        final_fig.add_trace(trace5)
    
    # add exports if selected
    if show_exports:
        trace6 = fig_exp.data[0]
        trace7 = fig_exp_centroid.data[0]
        final_fig.add_trace(trace6)
        final_fig.add_trace(trace7)
    
    # add upstream flows if selected
    if show_upstream_flows:
        trace8 = fig_up_flows.data[0]
        trace9 = fig_up_flows_centroid.data[0]
        final_fig.add_trace(trace8)
        final_fig.add_trace(trace9)
    
    # adding main rivers to california border map
    trace_river_sj = fig_river_sj.data[0]
    trace_river_amer = fig_river_amer.data[0]
    trace_river_feath = fig_river_feath.data[0]
    trace_river_sac = fig_river_sac.data[0]

    final_fig.add_trace(trace_river_sj)
    final_fig.add_trace(trace_river_amer)
    final_fig.add_trace(trace_river_feath)
    final_fig.add_trace(trace_river_sac)


    final_fig.update_layout(
        map_style='open-street-map',
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
        map_center={'lon': -122.0, 'lat': 38.0},
        map_zoom=6.3,
        height=800,
        colorscale={"diverging": mycolor_scale},
        coloraxis={
            "cmin": -50,
            "cmax": 50,
            "cauto": False,
            "autocolorscale": False,
            "colorbar": {"title": {"text": "VAL DIFF %"}},
        }
    )

    return final_fig


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
    return result


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
            if points and "customdata" in points[0]:
                custom_data = points[0]["customdata"]
                chart = handle_click(custom_data)
    return fig, chart
