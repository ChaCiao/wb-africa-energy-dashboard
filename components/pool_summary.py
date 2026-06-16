"""Sprint 5-B: Pool summary cards (SAPP / EAPP / CAPP) for the Overview page."""
from dash import html
import dash_bootstrap_components as dbc


def _pool_card(pool: str, data: dict) -> dbc.Col:
    color = data.get("color", "#0071BC")
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.Span(pool, className="pool-badge",
                              style={"background": color}),
                    html.Span(f"{data['count']} countries",
                              className="pool-count"),
                ], className="pool-header-row"),
                html.P(data.get("full_name", pool), className="pool-full-name"),
                html.Div([
                    html.Div([
                        html.Span("Access",     className="pool-metric-label"),
                        html.Span(f"{data['access']} %",     className="pool-metric-val"),
                    ], className="pool-metric"),
                    html.Div([
                        html.Span("Tariff",     className="pool-metric-label"),
                        html.Span(f"{data['tariff']} ¢",     className="pool-metric-val"),
                    ], className="pool-metric"),
                    html.Div([
                        html.Span("Renewables", className="pool-metric-label"),
                        html.Span(f"{data['renew']} %",      className="pool-metric-val"),
                    ], className="pool-metric"),
                ], className="pool-metrics-grid"),
            ]),
            className="pool-card",
            style={"borderTopColor": color},
        ),
        md=4,
    )


def make_pool_summary(pool_data: dict) -> dbc.Row:
    """Render 3-column SAPP/EAPP/CAPP card row. pool_data from compute_pool_summaries()."""
    if not pool_data:
        return html.Span()
    return dbc.Row(
        [_pool_card(pool, pool_data[pool])
         for pool in ["SAPP", "EAPP", "CAPP"] if pool in pool_data],
        className="g-3",
    )
