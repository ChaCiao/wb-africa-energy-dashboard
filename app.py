import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import config
from components import header, filter_rail, dimension_tabs
from callbacks.filter_callbacks import register_filter_callbacks
from callbacks.layout_callbacks import register_layout_callbacks
from callbacks.data_callbacks import register_data_callbacks
from callbacks.map_callbacks import register_map_callbacks
from callbacks.history_callbacks import register_history_callbacks
from callbacks.report_callbacks import register_report_callbacks
from callbacks.compare_callbacks import register_compare_callbacks
from callbacks.play_callbacks import register_play_callbacks
from callbacks.chart_click_callbacks import register_chart_click_callbacks
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
register_data_callbacks(app)
register_map_callbacks(app)
register_history_callbacks(app)
register_report_callbacks(app)
register_compare_callbacks(app)
register_play_callbacks(app)
register_chart_click_callbacks(app)

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
                # Sidebar: animated wrapper + arrow toggle
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
                                        # Back button lives here permanently (shown only in focus view)
                        html.Button(
                            "← Back to Overview",
                            id="focus-back-btn",
                            className="back-btn",
                            n_clicks=0,
                            style={"display": "none"},
                        ),
                        # Compare dropdown lives here permanently (shown only in focus view)
                        html.Div([
                            dcc.Dropdown(
                                id="compare-dropdown",
                                options=[{"label": c, "value": c}
                                         for c in config.ALL_COUNTRIES],
                                placeholder="Compare with another country…",
                                clearable=True,
                                className="compare-dropdown",
                            ),
                        ], id="compare-controls-wrapper", style={"display": "none"}),
                        dcc.Loading(
                            children=html.Div(id="page-content"),
                            type="dot",
                            color="#0071BC",
                            delay_show=150,
                        ),
                    ],
                    id="main-wrapper",
                    className="main-wrapper",
                ),
            ],
            className="body-row",
        ),

        # ── Client-side state stores ──────────────────────────────────
        dcc.Store(id="sidebar-open",      data=True,   storage_type="session"),
        dcc.Store(id="current-view",      data="home", storage_type="session"),
        dcc.Store(id="selected-scope",               storage_type="session"),
        dcc.Store(id="map-click",                    storage_type="memory"),
        dcc.Store(id="country-history",   data=[],    storage_type="session"),
        dcc.Store(id="dark-mode",         data=False, storage_type="local"),

        # ── URL sync ─────────────────────────────────────────────────
        dcc.Location(id="url", refresh=False),

        # ── Animation interval ────────────────────────────────────────
        dcc.Interval(id="play-interval", interval=1000, n_intervals=0, disabled=True),

        # ── Download targets ──────────────────────────────────────────
        dcc.Download(id="download-csv"),
        dcc.Download(id="download-report"),
    ],
    fluid=True,
    className="app-container",
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
