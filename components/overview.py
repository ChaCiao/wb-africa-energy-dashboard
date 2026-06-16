from dash import html, dcc
import dash_bootstrap_components as dbc

from components.kpi_row import make_kpi_row


def _mini_chart_card(title, fig=None, chart_id=None):
    body = (
        dcc.Graph(
            id=chart_id,
            figure=fig,
            config={"displayModeBar": False},
            style={"height": "155px"},
        )
        if fig is not None
        else html.Div("Select countries to load.", className="chart-placeholder chart-placeholder-sm")
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


def make_overview(values: dict = None, mini_figures: dict = None):
    """Build the Home / Overview page with KPIs and 2×2 mini-chart snapshot."""
    mini_figures = mini_figures or {}

    cards = [
        _mini_chart_card(title, mini_figures.get(fig_id), chart_id)
        for fig_id, chart_id, title in _MINI_CARDS
    ]

    return html.Div(
        [
            # ── Intro ─────────────────────────────────────────────────────
            html.Div(
                [
                    html.H4("Sub-Saharan Africa Energy Overview", className="overview-title"),
                    html.P(
                        "This dashboard covers energy access, economics, transition, and "
                        "institutional quality across 13 Sub-Saharan African countries (2015–2024). "
                        "Select a dimension tab above to explore detailed data.",
                        className="overview-intro",
                    ),
                ],
                className="overview-intro-block",
            ),

            # ── Cross-dimensional KPI row ──────────────────────────────────
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


# Convenience alias used at module level (no data — shows placeholders)
layout = make_overview()
