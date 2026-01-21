from dash import html, register_page, dash_table, dcc, Input, Output, callback #, callback # If you need callbacks, import it here.
import utils.onepager_api as api
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


register_page(
    __name__,
    name='One Pager',
    top_nav=True,
    path='/onepager'
)

# Generate historical data 

dss_filenames = {
    "hist": "data/2023DCR_Hist_DV.dss"
}


# csv_filename = "data\\temp.csv"
csv_filename = "data\\dv_data.csv"

yaml_config = api.take_yaml("utils/op.yaml")

# scenario_list = ["AdjHist", "CC50", "CC75", "CC95"]
scenario_list = api.get_scenarios(csv_filename)

def layout():
    layout = html.Div(children=[
        html.Br(),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Select Delivery:", style={'margin-right': '15px', 'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='delivery_type',
                            options=[
                                {'label': 'Table A', 'value': 'Table A'},
                                {'label': 'Article 21', 'value': 'Article 21'},
                            ],
                            value='Article 21',
                            style={'flex-grow': '0.5', 'margin-right': '20px'}
                        )
                    ],
                    style={'display': 'flex', 'flex': '1', 'margin-right': '20px'}
                ),
                html.Div(
                    [
                        html.Label("Scenario 1:", htmlFor=("scenario_1"), style={'margin-right': '15px', 'font-weight': 'bold'}),
                        dcc.Dropdown(
                            scenario_list, scenario_list[0], id="scenario_1",
                            style={'flex-grow': '0.5'}
                        ),
                    ], style={'display': 'flex', 'flex': '1', 'margin-right': '20px'}
                ),
                html.Div(
                    [
                        html.Label("Scenario 2:", htmlFor=("scenario_2"), style={'margin-right': '15px', 'font-weight': 'bold'}),
                        dcc.Dropdown(
                            scenario_list, scenario_list[4], id="scenario_2",
                            style={'flex-grow': '0.5'}
                        ),
                    ], style={'display': 'flex', 'flex': '1', 'margin-right': '20px'},
                ),
            ], style={'display': 'flex', 'flex': '1', "padding": "15px"},
        ),
        html.H2("SWP Deliveries, TAF/year (Percent Allocation)"),
        html.Div(id="data_table"),
        html.Br(),
        html.Br(),
        html.Div(id='data_graph'),
        html.Div(id='likelihood_graph')
    ], style={'width': '80%'})

    return layout

@callback(
    Output("data_table", "children"),
    Output("data_graph", "children"),
    Output("likelihood_graph", "children"),
    Input("delivery_type", "value"),
    Input("scenario_1", "value"),
    Input("scenario_2", "value"),
    prevent_initial_call=False
)
def handle_selection(delivery_type, scen1, scen2):
    add_perc = (delivery_type == 'Table A')
    df = api.read_all_runs_to_structure_csv(csv_filename, delivery_type, scen1, scen2)
    tab_rows = []
    graph_data = []
    for year_type in yaml_config.get_period_types():
        df_1 = df[df["YEAR_TYPE"] == year_type]
        row_count = len(df_1)
        i = 0
        for _, row in df_1.iterrows():
            graph_data.append([year_type, scen1, row["ITEM"], row["VAL_1"]])
            graph_data.append([year_type, scen2, row["ITEM"], row["VAL_2"]])

            if i == 0:
                tab_rows.append(html.Tr(style={'border-bottom': '1px solid black'}))
                tab_rows.append(
                    html.Tr(
                        [
                            html.Td(f"{year_type}", rowSpan=row_count, style={'font-weight': 'bold'}),
                            html.Td(row["ITEM"]),
                            html.Td(
                                f"{row['VAL_1']:,d} ({row['PERC_1']:0.1f}%)" if add_perc else f"{row['VAL_1']:,d}",
                                style={'textAlign': 'right', 'paddingRight': '10%'}
                            ),
                            html.Td(
                                f"{row['VAL_2']:,d} ({row['PERC_2']:0.1f}%)" if add_perc else f"{row['VAL_2']:,d}",
                                style={'textAlign': 'right', 'paddingRight': '10%'}
                            ),
                            html.Td(
                                f"{row['CHANGE']:+d}",
                                style={'textAlign': 'right', 'paddingRight': '10%'}
                            )
                        ]
                    )
                )
            else:
                tab_rows.append(
                    html.Tr(
                        [
                            # skip first column
                            html.Td(row['ITEM']),
                            html.Td(
                                f"{row['VAL_1']:,d} ({row['PERC_1']:0.1f}%)" if add_perc else f"{row['VAL_1']:,d}",
                                style={'textAlign': 'right', 'paddingRight': '10%'}
                            ),
                            html.Td(
                                f"{row['VAL_2']:,d} ({row['PERC_2']:0.1f}%)" if add_perc else f"{row['VAL_2']:,d}",
                                style={'textAlign': 'right', 'paddingRight': '10%'}
                            ),
                            html.Td(
                                f"{row['CHANGE']:+d}",
                                style={'textAlign': 'right', 'paddingRight': '10%'}
                            )
                        ]
                    )
                )
            i += 1

    tab = html.Table(
        [
            html.Thead(html.Tr([
                html.Th(""),
                html.Th(""),
                html.Th(f"Final DCR 2023 Conditions ({scen1})"),
                html.Th(f"Draft DCR 2025 Conditions ({scen2})"),
                html.Th("Change")
            ])),
            html.Tbody(tab_rows)
        ],
        style={'width': '80%', 'margin': '20px auto'}
    )

    bar_figs = []
    for year_type in yaml_config.get_period_types():
        graph_df = pd.DataFrame(graph_data, columns=['YEAR_TYPE', 'SCENARIO', 'SWP Delivery Type', 'SWP Deliveries (TAF/year)'])
        graph_df_wet = graph_df[graph_df["YEAR_TYPE"] == year_type]
        bar = px.bar(graph_df_wet, x="SWP Delivery Type", y="SWP Deliveries (TAF/year)", color="SCENARIO", barmode="group", color_discrete_sequence=["#336DFF", "#000000"])
        bar.update_yaxes(tickformat=",")
        bar.update_traces(texttemplate='%{y:,.0f}', textposition='outside', textfont=dict(color='black'), cliponaxis=False)
        # set background light gray, gridlines black, and add black border
        bar.update_layout(
            plot_bgcolor='lightgray',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='black'),
            shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, x1=1, y0=0, y1=1, line=dict(color='black', width=1), fillcolor='rgba(0,0,0,0)')],
            margin=dict(t=50, b=50, l=50, r=50)
        )
        heading = html.H2(f"Estimated {year_type} SWP {delivery_type}, for Climate Scenarios {scen1} and {scen2}")
        bar_figs.append(heading)
        bar_figs.append(dcc.Graph(figure=bar))
    
    likelihood_figs = []
    likelihood_df = api.build_likelihood_by_taf(csv_filename, "Article 21", "DCR23_Baseline", "DCR25_Baseline")
    # print("likelihood_df:\n", likelihood_df)
    bar = px.bar(likelihood_df, x="RANGE", y="LIKELIHOOD", color="SCENARIO", barmode="group", color_discrete_sequence=["#336DFF", "#000000"])
    bar.update_traces(texttemplate='%{y:,.0f}', textposition='outside', textfont=dict(color='black'), cliponaxis=False)
    bar.update_layout(
        plot_bgcolor='lightgray',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='black'),
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, x1=1, y0=0, y1=1, line=dict(color='black', width=1), fillcolor='rgba(0,0,0,0)')],
        margin=dict(t=50, b=50, l=50, r=50)
    )
    heading = html.H2(f"Estimated Likelihood of Annual Deliveries of SWP Article 21 Water (Existing Conditions)")
    likelihood_figs.append(heading)
    likelihood_figs.append(dcc.Graph(figure=bar))
    return [tab], bar_figs, likelihood_figs
