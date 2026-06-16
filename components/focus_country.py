"""
Focus Country page — single-country deep-dive panel.
Reached by clicking a country on the Africa map.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc

import config

_COMPARE_OPTIONS = [{"label": c, "value": c} for c in config.ALL_COUNTRIES]


_POOL_COLOR = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}


def _kpi_card(label, value, unit, ssa_value=None, color="#0071BC", rank=None):
    """Compact KPI card with optional SSA benchmark row and rank badge."""
    ssa_el = (
        html.P(
            [html.Span("SSA avg: ", style={"color": "#8A9BAC"}),
             html.Span(f"{ssa_value} {unit}", style={"color": "#E67E22", "fontWeight": "600"})],
            className="focus-ssa-bench",
        ) if ssa_value and ssa_value != "—" else html.Span()
    )
    rank_el = (
        html.Span(f"Rank {rank}", className="focus-rank-badge")
        if rank and rank != "—" else html.Span()
    )
    return dbc.Card(
        dbc.CardBody([
            html.P(label, className="kpi-label"),
            html.Div([
                html.Span(value, className="kpi-value-text"),
                html.Span(f" {unit}", className="kpi-unit"),
                rank_el,
            ], className="kpi-value"),
            ssa_el,
        ]),
        className="kpi-card",
        style={"borderLeftColor": color},
    )


def _chart_panel(title, fig, chart_id):
    body = (
        dcc.Graph(id=chart_id, figure=fig,
                  config={"displayModeBar": False},
                  style={"height": "175px"})
        if fig is not None
        else html.Div("No data.", className="chart-placeholder chart-placeholder-sm")
    )
    return dbc.Card(dbc.CardBody([
        html.H6(title, className="chart-title"),
        body,
    ]))


def make_focus_page(country: str, kpis: dict, charts: dict, year_range: list):
    """
    Build the Focus Country page for a single country.

    Args:
        country   : e.g. "Kenya"
        kpis      : dict from focus_compute.compute_focus_kpis()
        charts    : dict from focus_compute.build_focus_charts()
        year_range: [yr_min, yr_max]
    """
    region     = config.COUNTRY_REGION.get(country, "SAPP")
    pool_color = _POOL_COLOR.get(region, "#0071BC")
    yr_label   = f"{year_range[0]}–{year_range[1]}" if year_range else "—"

    # KPI row
    kpi_cards = dbc.Row([
        dbc.Col(_kpi_card("Electrification Rate", kpis.get("kpi-focus-access", "—"), "%",
                           kpis.get("ssa-access"), color="#0071BC",
                           rank=kpis.get("rank-access")), md=3),
        dbc.Col(_kpi_card("Residential Tariff", kpis.get("kpi-focus-tariff", "—"), "¢/kWh",
                           kpis.get("ssa-tariff"), color="#27AE60",
                           rank=kpis.get("rank-tariff")), md=3),
        dbc.Col(_kpi_card("Renewable Share", kpis.get("kpi-focus-renew", "—"), "%",
                           kpis.get("ssa-renew"), color="#1ABC9C",
                           rank=kpis.get("rank-renew")), md=3),
        dbc.Col(_kpi_card("Utility Ownership", kpis.get("kpi-focus-ownership", "—"), "",
                           None, color=pool_color), md=3),
    ], className="kpi-row g-3")

    # Chart grid
    chart_grid = dbc.Row([
        dbc.Col(_chart_panel("Electrification Rate Trend", charts.get("focus-access"),
                              "focus-chart-access"), md=6),
        dbc.Col(_chart_panel("Residential Tariff Trend",  charts.get("focus-tariff"),
                              "focus-chart-tariff"),  md=6),
        dbc.Col(_chart_panel("Renewable Share Trend",     charts.get("focus-renew"),
                              "focus-chart-renew"),   md=6),
        dbc.Col(_chart_panel("Capacity Mix vs SSA avg",   charts.get("focus-capacity"),
                              "focus-chart-capacity"), md=6),
    ], className="g-3")

    return html.Div([
        # ── Country header ─────────────────────────────────────────────
        html.Div(
            [
                html.Div(
                    [
                        html.Span(region, className="focus-pool-badge",
                                  style={"background": pool_color}),
                        html.H4(country, className="focus-country-title"),
                    ],
                    className="focus-title-row",
                ),
                html.P(f"Focus Country View  ·  {yr_label}  ·  vs SSA Average (dotted)",
                       className="focus-subtitle"),
            ],
            className="focus-header",
        ),

        html.Hr(className="section-divider"),

        # ── KPI row ────────────────────────────────────────────────────
        html.P("Key Indicators — Latest Year", className="section-label"),
        kpi_cards,

        html.Hr(className="section-divider"),

        # ── 2×2 chart grid ─────────────────────────────────────────────
        html.P("Trend Analysis (Country vs SSA Average)", className="section-label"),
        chart_grid,

        html.Hr(className="section-divider"),

        # ── Country comparison output (placeholder populated by callback) ──
        html.P("Compare with Another Country", className="section-label"),
        html.Div(id="compare-output"),
    ], className="focus-content")
