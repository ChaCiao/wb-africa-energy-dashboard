from datetime import datetime
from dash import html
import dash_bootstrap_components as dbc

_LAST_UPDATED = datetime.now().strftime("%B %d, %Y")

layout = html.Div(
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.H1("Africa Energy Dashboard", className="header-title"),
                        html.P(
                            f"Last update: {_LAST_UPDATED}",
                            className="header-subtitle",
                        ),
                    ],
                    className="header-inner",
                ),
            ),
            dbc.Col(
                html.Div([
                    html.Button(
                        [html.Span("⌂ ", className="home-icon"), "Home"],
                        id="home-btn",
                        className="home-btn",
                        n_clicks=0,
                    ),
                    html.Button(
                        "↓ Export Report",
                        id="export-report-btn",
                        className="export-btn",
                        n_clicks=0,
                    ),
                    html.Button(
                        "☀ / ☾",
                        id="dark-mode-btn",
                        className="dark-mode-btn",
                        n_clicks=0,
                        title="Toggle dark mode",
                    ),
                ], className="header-btn-group"),
                width="auto",
                className="d-flex align-items-center",
            ),
        ],
        className="align-items-center w-100 m-0",
    ),
    className="app-header",
)
