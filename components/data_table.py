from dash import html, dash_table
import dash_bootstrap_components as dbc


def make_data_table(columns=None, data=None):
    """Build the DataTable card with a Download CSV button."""
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.H5("Data Table", className="table-title mb-0"),
                    className="d-flex align-items-center",
                ),
                dbc.Col(
                    html.Button(
                        "↓ Download CSV",
                        id="download-btn",
                        className="download-btn",
                        n_clicks=0,
                    ),
                    className="d-flex justify-content-end align-items-center",
                ),
            ], className="mb-2 g-0"),

            dash_table.DataTable(
                id="main-data-table",
                columns=columns or [],
                data=data or [],
                page_size=10,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#0071BC",
                    "color": "white",
                    "fontWeight": "bold",
                    "fontSize": "12px",
                    "padding": "10px 12px",
                },
                style_cell={
                    "textAlign": "left",
                    "fontSize": "12px",
                    "padding": "8px 12px",
                    "border": "1px solid #D0D8E0",
                    "whiteSpace": "normal",
                    "height": "auto",
                    "minWidth": "80px",
                    "maxWidth": "200px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#F5F7FA"},
                ],
                style_filter={"fontSize": "11px"},
            ),
        ]),
        className="data-table-card mt-3",
    )


# Backward-compatible alias (shows empty table — used before data is wired)
layout = make_data_table()
