import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html, register_page
from utils.query_data import df_dv, scen_aliases, var_dict
from utils.tools import make_summary_df


#register_page(
#    __name__,
#    name="Summary Table",
#    top_nav=True,
#    path="/summary",
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
        #   '----'
        "DELTAINFLOWFORNDOI",
        #    '----'
        "NDOI",
        #
        "C_CAA003",
        "C_CAA003_SWP",
        "C_DMC000",
        "C_DMC000_CVP",
        #    '----',
        "SWP_TA_TOTAL",
        "SWP_IN_TOTAL",
        "SWP_CO_TOTAL",
        "CVPTOTALDEL",
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
            dcc.Markdown("# Summary Table"),
            html.A(summary_text),
            dbc.Row(
                [
                    dcc.Markdown("#### "),
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
                ]
            ),
        ],
    )
    return layout


layout()
