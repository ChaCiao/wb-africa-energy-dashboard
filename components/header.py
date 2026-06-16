from dash import html
import dash_bootstrap_components as dbc

layout = html.Div(
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.H1("WB Africa Energy Access Dashboard", className="header-title"),
                        html.P(
                            "World Bank Sub-Saharan Africa Energy Sector Analysis · 2015–2024",
                            className="header-subtitle",
                        ),
                    ],
                    className="header-inner",
                ),
            ),
            dbc.Col(
                html.Button(
                    [html.Span("⌂ ", className="home-icon"), "Home"],
                    id="home-btn",
                    className="home-btn",
                    n_clicks=0,
                ),
                width="auto",
                className="d-flex align-items-center",
            ),
        ],
        className="align-items-center w-100 m-0",
    ),
    className="app-header",
)
