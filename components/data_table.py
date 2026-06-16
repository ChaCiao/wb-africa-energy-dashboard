from dash import html, dash_table
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Data Table", className="table-title"),
            html.P(
                "Select tier and country in the sidebar to populate this table.",
                className="table-placeholder text-muted",
            ),
            dash_table.DataTable(
                id="main-data-table",
                columns=[],
                data=[],
                page_size=10,
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#0071BC",
                    "color": "white",
                    "fontWeight": "bold",
                    "fontSize": "13px",
                },
                style_cell={
                    "textAlign": "left",
                    "fontSize": "12px",
                    "padding": "8px 12px",
                    "border": "1px solid #D0D8E0",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#F5F7FA",
                    }
                ],
            ),
        ]
    ),
    className="data-table-card mt-3",
)
