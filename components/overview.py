from datetime import datetime
from dash import html, dcc
import dash_bootstrap_components as dbc

from components.kpi_row import make_kpi_row
from components.africa_map import build_africa_map

_TODAY = datetime.now().strftime("%B %d, %Y")


# ── Welcome box ───────────────────────────────────────────────────────────────

def _welcome_box():
    return html.Div(
        [
            html.Div(
                [
                    html.P("Welcome back, Wooseop", className="welcome-name"),
                    html.P(
                        "Private Research Workspace  ·  Sub-Saharan Africa Energy Sector",
                        className="welcome-sub",
                    ),
                ],
            ),
            html.Div(
                [
                    html.Span("🔒 PRIVATE", className="welcome-badge"),
                    html.Span(_TODAY, className="welcome-date"),
                ],
                className="welcome-right",
            ),
        ],
        className="welcome-box",
    )


# ── Mini chart helpers ────────────────────────────────────────────────────────

def _mini_chart_card(title, fig=None, chart_id=None):
    body = (
        dcc.Graph(
            id=chart_id,
            figure=fig,
            config={"displayModeBar": False},
            style={"height": "155px"},
        )
        if fig is not None
        else html.Div(
            "Select countries to load.",
            className="chart-placeholder chart-placeholder-sm",
        )
    )
    return dbc.Card(dbc.CardBody([
        html.H6(title, className="chart-title"),
        body,
    ]))


_MINI_CARDS = [
    ("mini-access",       "mini-chart-access",       "Access — Electrification Rate Trend"),
    ("mini-economics",    "mini-chart-economics",     "Economics — Residential Tariff Trend"),
    ("mini-transition",   "mini-chart-transition",    "Transition — Renewable Share Trend"),
    ("mini-institutions", "mini-chart-institutions",  "Institutions — Ownership Structure"),
]


# ── Public factory ────────────────────────────────────────────────────────────

def make_overview(values: dict = None, mini_figures: dict = None):
    """Build the Home / Overview page with welcome box, Africa map, KPIs, and mini-charts."""
    mini_figures = mini_figures or {}

    cards = [
        _mini_chart_card(title, mini_figures.get(fig_id), chart_id)
        for fig_id, chart_id, title in _MINI_CARDS
    ]

    return html.Div(
        [
            # ── Welcome box ────────────────────────────────────────────────
            _welcome_box(),

            # ── Interactive Africa map ─────────────────────────────────────
            html.Div(
                [
                    html.P("Sub-Saharan Africa — Coverage Map", className="section-label"),
                    dcc.Graph(
                        id="africa-map",
                        figure=build_africa_map(),
                        config={"displayModeBar": False, "scrollZoom": False},
                        className="africa-map-graph",
                    ),
                    html.P(
                        "Hover for key metrics · Click a country to open its focus view",
                        className="map-hint",
                    ),
                ],
                className="africa-map-container",
            ),

            html.Hr(className="section-divider"),

            # ── Cross-dimensional KPI row ──────────────────────────────────
            html.P("Cross-Dimensional KPIs", className="section-label"),
            make_kpi_row("home", values),

            html.Hr(className="section-divider"),

            # ── 2×2 mini chart snapshot ────────────────────────────────────
            html.P("Snapshot — All Dimensions", className="section-label"),
            dbc.Row(
                [dbc.Col(cards[0], md=6), dbc.Col(cards[1], md=6)],
                className="g-3 mb-3",
            ),
            dbc.Row(
                [dbc.Col(cards[2], md=6), dbc.Col(cards[3], md=6)],
                className="g-3",
            ),
        ],
        className="overview-content",
    )


# Convenience alias used at module level (static — no live data)
layout = make_overview()
