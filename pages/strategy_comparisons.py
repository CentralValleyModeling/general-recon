import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html, register_page
from utils.query_data import df_dv, scen_aliases, var_dict
from utils.tools import make_summary_df


#register_page(
#    __name__,
#    name="Strategy Comparisons",
#    top_nav=True,
#    path="/strategy_comparisons",
#    order=4,
#)

summary_text = (
    """This page provides annual averages (water year) for key system variables. """,
    """Types include upstream river flows, Delta inflow """,
    """and outflows, exports, and deliveries.""",
    html.Br(),
    html.Br(),
)

exp_tbl = make_summary_df(
    scen_aliases,
    df_dv,
    var_dict,
    bparts=[
        "EXPORTACTUALTDIF",
    ],
)

ta_tbl = make_summary_df(
    scen_aliases,
    df_dv,
    var_dict,
    bparts=[
        "SWP_TA_TOTAL",
    ],
)
a21_tbl = make_summary_df(
    scen_aliases,
    df_dv,
    var_dict,
    bparts=[
        "SWP_IN_TOTAL",
    ],
)


# Determine the table order
# Descriptive stuff goes first
table_order = [
    {"name": "Type", "id": "type"},
    {"name": "Description", "id": "description"},
    {"name": "B-Part", "id": "bpart"},
    {"name": "Units", "id": "convert"},

]

# Scenarios go next
table_order.extend(
    [
        {"name": s, "id": s, "type": "numeric", "format": {"specifier": ",.0f"}}
        for s in scen_aliases
        if s not in ["description", "index", "type"]
    ]
)


def layout():
    layout = dbc.Container(
        class_name="my-3",
        children=[
 #           dcc.Markdown("# Summary Table"),
 #           html.A(summary_text),
            dbc.Row(
                [
                    dcc.Markdown("### Strategy Comparisons - 2043 CC50"),
                    dcc.Markdown("#### <<INSERT YEAR TYPE DROPDOWN HERE>>"),
                    dcc.Markdown("#### Total Delta Exports"),
                    dash_table.DataTable(
                        id="exp_tbl",
                        columns=table_order,
                        data=exp_tbl.to_dict(orient="records"),
                        style_header={
                            "backgroundColor": "rgb(200, 200, 200)",
                            "fontWeight": "bold",
                        },
                        style_cell={
                            "width": "{}%".format(len(exp_tbl.columns)),
                            # 'width': '1000px',
                            "textOverflow": "ellipsis",
                            "overflow": "hidden",
                            "textAlign": "left",
                        },
                    ),
                    dcc.Markdown("## _"),
                    dcc.Markdown("#### Table A Deliveries"),
                    dash_table.DataTable(
                        id="ta_tbl",
                        columns=table_order,
                        data=ta_tbl.to_dict(orient="records"),
                        style_header={
                            "backgroundColor": "rgb(200, 200, 200)",
                            "fontWeight": "bold",
                        },
                        style_cell={
                            "width": "{}%".format(len(exp_tbl.columns)),
                            # 'width': '1000px',
                            "textOverflow": "ellipsis",
                            "overflow": "hidden",
                            "textAlign": "left",
                        },
                    ),
                    dcc.Markdown("## _"),
                    dcc.Markdown("#### Article 21 Deliveries"),
                    dash_table.DataTable(
                        id="ta_tbl",
                        columns=table_order,
                        data=a21_tbl.to_dict(orient="records"),
                        style_header={
                            "backgroundColor": "rgb(200, 200, 200)",
                            "fontWeight": "bold",
                        },
                        style_cell={
                            "width": "{}%".format(len(exp_tbl.columns)),
                            # 'width': '1000px',
                            "textOverflow": "ellipsis",
                            "overflow": "hidden",
                            "textAlign": "left",
                        },
                    ),
                ]
            ),
        ],
    )
    return layout


layout()
