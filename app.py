import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from components import header, filter_rail, dimension_tabs
from callbacks.filter_callbacks import register_filter_callbacks
from callbacks.layout_callbacks import register_layout_callbacks
import data.loaders  # noqa: F401 – triggers CSV auto-generation on first run

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="WB Africa Energy Dashboard",
    suppress_callback_exceptions=True,
)
server = app.server

register_filter_callbacks(app)
register_layout_callbacks(app)

app.layout = dbc.Container(
    [
        # ── Mock data notice ──────────────────────────────────────────
        html.Div(
            dbc.Badge(
                "⚠ MOCK DATA — not for citation",
                color="warning",
                className="mock-badge",
            ),
            className="mock-banner",
        ),

        # ── App header (title + Home button) ─────────────────────────
        header.layout,

        # ── Body: sidebar container + main panel ─────────────────────
        html.Div(
            [
                # Sidebar: animated wrapper + arrow toggle side by side
                html.Div(
                    [
                        html.Div(
                            filter_rail.layout,
                            id="sidebar-wrapper",
                            className="sidebar-wrapper",
                        ),
                        html.Button(
                            "◀",
                            id="sidebar-toggle-btn",
                            className="sidebar-arrow-btn",
                            n_clicks=0,
                        ),
                    ],
                    className="sidebar-container",
                ),

                # Main: dimension tabs + page content
                html.Div(
                    [
                        dimension_tabs.layout,
                        html.Div(id="page-content"),
                    ],
                    id="main-wrapper",
                    className="main-wrapper",
                ),
            ],
            className="body-row",
        ),

        # ── Client-side state stores ──────────────────────────────────
        dcc.Store(id="sidebar-open",   data=True,   storage_type="session"),
        dcc.Store(id="current-view",   data="home", storage_type="session"),
        dcc.Store(id="selected-scope",              storage_type="session"),
    ],
    fluid=True,
    className="app-container",
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
