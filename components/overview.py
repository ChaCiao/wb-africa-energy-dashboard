from dash import html
import dash_bootstrap_components as dbc

from components.kpi_row import make_kpi_row


def _mini_chart_card(title):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="chart-title"),
                html.Div("Chart — next sprint", className="chart-placeholder chart-placeholder-sm"),
            ]
        )
    )


def make_overview(values: dict = None):
    """Build the Home / Overview page, injecting computed KPI values."""
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
                [
                    dbc.Col(_mini_chart_card("Access — Electrification Rate Trend"),  md=6),
                    dbc.Col(_mini_chart_card("Economics — Residential Tariff Trend"), md=6),
                ],
                className="g-3 mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(_mini_chart_card("Transition — Renewable Share Trend"),   md=6),
                    dbc.Col(_mini_chart_card("Institutions — Reform & Regulation"),   md=6),
                ],
                className="g-3",
            ),
        ],
        className="overview-content",
    )


# Convenience alias used at module level (no data — shows "—")
layout = make_overview()
