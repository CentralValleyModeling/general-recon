from dash import html, register_page, dash_table, dcc, Input, Output, callback #, callback # If you need callbacks, import it here.
import utils.onepager_api as api
import plotly.express as px
import pandas as pd


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

csv_filename = "data\\temp.csv"


# scenario_list = ["DCR23_Baseline", "DCR23_CC50", "DCR23_CC75", "DCR23_CC95", "DCR25_Baseline", "DCR25_CC50", "DCR25_CC95"]
scenario_list = ["AdjHist", "CC50", "CC75", "CC95"]

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
                            value='Table A',
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
                            scenario_list, scenario_list[1], id="scenario_2",
                            style={'flex-grow': '0.5'}
                        ),
                    ], style={'display': 'flex', 'flex': '1', 'margin': '20px'},
                ),
            ], style={'display': 'flex', 'flex': '1'},
        ),
        html.H2("SWP Deliveries under Existing Conditions, TAF/year (Percent Allocation)"),
        html.Div(id="data_table"),
        html.Br(),
        html.Br(),
        html.H2("SWP Deliveries under Existing Conditions, for Climate Scenarios"),
        dcc.Graph(id='data_graph'),
    ], style={'width': '80%'})

    return layout

@callback(
    Output("data_table", "children"),
    Output("data_graph", "figure"),
    Input("delivery_type", "value"),
    Input("scenario_1", "value"),
    Input("scenario_2", "value"),
    prevent_initial_call=False
)
def handle_selection(delivery_type, scen1, scen2):
    df = api.read_all_runs_to_structure_csv(csv_filename, delivery_type, scen1, scen2)
    tab_rows = []
    graph_data = []
    for year_type in ["Wet", "Dry"]:
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
                            html.Td(f"{year_type} Periods", rowSpan=row_count, style={'font-weight': 'bold'}),
                            html.Td(row["ITEM"]),
                            html.Td(f"{row['VAL_1']:d} ({row['PERC_1']:0.2f}%)"),
                            html.Td(f"{row['VAL_2']:d} ({row['PERC_2']:0.2f}%)"),
                            html.Td(f"{row['CHANGE']:+d}")
                        ]
                    )
                )
            else:
                tab_rows.append(
                    html.Tr(
                        [
                            # skip first column
                            html.Td(row["ITEM"]),
                            html.Td(f"{row['VAL_1']:d} ({row['PERC_1']:0.2f}%)"),
                            html.Td(f"{row['VAL_2']:d} ({row['PERC_2']:0.2f}%)"),
                            html.Td(f"{row['CHANGE']:+d}")
                        ]
                    )
                )
            i += 1

    tab = html.Table(
        [
            html.Thead(html.Tr([
                html.Th(""),
                html.Th(""),
                html.Th("Final DCR 2023 Existing Conditions"),
                html.Th("Draft DCR 2025 Existing Conditions"),
                html.Th("Change")
            ])),
            html.Tbody(tab_rows)
        ],
        style={'width': '80%', 'margin': '20px auto'}
    )

    graph_df = pd.DataFrame(graph_data, columns=['YEAR_TYPE', 'SCENARIO', 'SWP Delivery Type', 'SWP Deliveries (TAF/year)'])
    graph_df_wet = graph_df[graph_df["YEAR_TYPE"] == "Wet"]
    fig = px.bar(graph_df_wet, x="SWP Delivery Type", y="SWP Deliveries (TAF/year)", color="SCENARIO", barmode="group", color_discrete_sequence=["#336DFF", "#000000"])

    return [tab], fig




# def handle_selection_old(delivery_type, scen1, scen2):
#     year_type = "Wet"
#     combined_struct = api.read_all_runs_to_structure_csv(csv_filename, delivery_type, year_type, scen1, scen2)
#     data_list = []
#     graph_data = []
#     dry_wet_label_1 = ""
#     dry_wet_label_2 = ""
#     dry_wet_label_3 = ""
#     for study_name, table in combined_struct.items():
#         # print(f"{study_name} = {table}")
#         dry_wet_label_1 = table["dry_wet_label_1"]
#         dry_wet_label_2 = table["dry_wet_label_2"]
#         dry_wet_label_3 = table["dry_wet_label_3"]

#         data = {}
#         data["v0"] = study_name
#         data["v1"], data["p1"] = table["Long-term Average"]
#         data["v2"], data["p2"] = table["dry_wet_data_1"]
#         data["v3"], data["p3"] = table["dry_wet_data_2"]
#         data["v4"], data["p4"] = table["2-Year (1982-1983)"]
#         data["v5"], data["p5"] = table["4-Year (1980-1983)"]
#         data["v6"], data["p6"] = table["6-Year (1978-1983)"]
#         data["v7"], data["p7"] = table["10-Year (1978-1987)"]
#         data["v8"], data["p8"] = table["dry_wet_data_3"]
#         data_list.append(data)

#         # populate data for graph
#         graph_row = [study_name, "Long-term Average", data["v1"]]
#         graph_data.append(graph_row)

#         graph_row = [study_name, dry_wet_label_1, data["v2"]]
#         graph_data.append(graph_row)

#         graph_row = [study_name, dry_wet_label_2, data["v3"]]
#         graph_data.append(graph_row)

#         graph_row = [study_name, "2-Year (1982-1983)", data["v4"]]
#         graph_data.append(graph_row)

#         graph_row = [study_name, "4-Year (1980-1983)", data["v5"]]
#         graph_data.append(graph_row)

#         graph_row = [study_name, "6-Year (1978-1983)", data["v6"]]
#         graph_data.append(graph_row)

#         graph_row = [study_name, "10-Year (1978-1987)", data["v7"]]
#         graph_data.append(graph_row)

#         graph_row = [study_name, dry_wet_label_3, data["v8"]]
#         graph_data.append(graph_row)

#     header1 = (f"Table 5-4. Estimated Average and {year_type}-Period Deliveries of SWP {delivery_type} Water (Existing Conditions, in taf/year) and Percent of Maximum SWP {delivery_type} Amount, 4,133 TAF/year")

#     tab = dash_table.DataTable(
#         columns=[
#             {"name": [header1, "Scenario", ""], "id": "v0"},
#             {"name": [header1, "Long-term Average", "val"], "id": "v1"},
#             {"name": [header1, "Long-term Average", "%"], "id": "p1"},
#             {"name": [header1, f"{dry_wet_label_1}", "val"], "id": "v2"},
#             {"name": [header1, f"{dry_wet_label_1}", "%"], "id": "p2"},
#             {"name": [header1, f"{dry_wet_label_2}", "val"], "id": "v3"},
#             {"name": [header1, f"{dry_wet_label_2}", "%"], "id": "p3"},
#             {"name": [header1, "2-Year (1982-1983)", "val"], "id": "v4"},
#             {"name": [header1, "2-Year (1982-1983)", "%"], "id": "p4"},
#             {"name": [header1, "4-Year (1980-1983)", "val"], "id": "v5"},
#             {"name": [header1, "4-Year (1980-1983)", "%"], "id": "p5"},
#             {"name": [header1, "6-Year (1978-1983)", "val"], "id": "v6"},
#             {"name": [header1, "6-Year (1978-1983)", "%"], "id": "p6"},
#             {"name": [header1, "10-Year (1978-1987)", "val"], "id": "v7"},
#             {"name": [header1, "10-Year (1978-1987)", "%"], "id": "p7"},
#             {"name": [header1, f"{dry_wet_label_3}", "val"], "id": "v8"},
#             {"name": [header1, f"{dry_wet_label_3}", "%"], "id": "p8"}, 
#         ], 
#         data=data_list,
#         merge_duplicate_headers=True,
#     )

#     graph_df = pd.DataFrame(graph_data, columns=['Scenario', 'Measure', 'Value'])
#     fig = px.bar(graph_df, x="Measure", y="Value", color="Scenario", barmode="group")

#     return tab, fig


    
