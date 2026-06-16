"""
Sprint 5-B: Country comparison mode inside the Focus Country view.
Triggered by selecting a second country from the compare dropdown.
"""
import config
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from data.focus_compute import compute_focus_kpis

_POOL_COLOR = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}


def _cmp_row(label, val_a, val_b, unit, higher_is_better=True):
    """Side-by-side metric row with winner/loser highlighting."""
    def _classes(a, b):
        try:
            fa, fb = float(a), float(b)
            if higher_is_better:
                return ("compare-win", "compare-lose") if fa >= fb else ("compare-lose", "compare-win")
            else:
                return ("compare-win", "compare-lose") if fa <= fb else ("compare-lose", "compare-win")
        except (ValueError, TypeError):
            return ("", "")

    cls_a, cls_b = _classes(val_a, val_b)
    return html.Tr([
        html.Td(label,                    className="compare-row-label"),
        html.Td(f"{val_a} {unit}".strip(), className=f"compare-cell {cls_a}"),
        html.Td(f"{val_b} {unit}".strip(), className=f"compare-cell {cls_b}"),
    ])


def register_compare_callbacks(app):

    @app.callback(
        Output("compare-output", "children"),
        Input("compare-dropdown",  "value"),
        State("map-click",         "data"),
        State("year-slider",       "value"),
        prevent_initial_call=True,
    )
    def update_comparison(compare_country, map_click, year_range):
        if not compare_country or not map_click:
            raise PreventUpdate
        primary = map_click.get("country")
        if not primary or compare_country == primary:
            raise PreventUpdate

        yr_min = int(year_range[0]) if year_range else 2015
        yr_max = int(year_range[1]) if year_range else 2024

        kpis_a = compute_focus_kpis(primary,        yr_min, yr_max)
        kpis_b = compute_focus_kpis(compare_country, yr_min, yr_max)

        reg_a = config.COUNTRY_REGION.get(primary,         "SAPP")
        reg_b = config.COUNTRY_REGION.get(compare_country, "SAPP")

        def _badge(region, country):
            return [
                html.Span(region, className="compare-pool-badge",
                          style={"background": _POOL_COLOR.get(region, "#0071BC")}),
                f" {country}",
            ]

        table = html.Table([
            html.Thead(html.Tr([
                html.Th("Indicator"),
                html.Th(_badge(reg_a, primary)),
                html.Th(_badge(reg_b, compare_country)),
            ]), className="compare-thead"),
            html.Tbody([
                _cmp_row("Electrification Rate",
                         kpis_a.get("kpi-focus-access", "—"),
                         kpis_b.get("kpi-focus-access", "—"), "%"),
                _cmp_row("Residential Tariff",
                         kpis_a.get("kpi-focus-tariff", "—"),
                         kpis_b.get("kpi-focus-tariff", "—"), "¢/kWh",
                         higher_is_better=False),
                _cmp_row("Renewable Share",
                         kpis_a.get("kpi-focus-renew", "—"),
                         kpis_b.get("kpi-focus-renew", "—"), "%"),
                _cmp_row("Access Rank",
                         kpis_a.get("rank-access", "—"),
                         kpis_b.get("rank-access", "—"), "",
                         higher_is_better=False),
            ]),
        ], className="compare-table")

        return dbc.Card(
            dbc.CardBody([
                html.H6(f"Comparison: {primary} vs {compare_country}",
                        className="chart-title"),
                table,
                html.P("Green = better on each metric  ·  Rank: lower number = better",
                       className="table-note mt-2"),
            ]),
            className="compare-card mt-3",
        )
