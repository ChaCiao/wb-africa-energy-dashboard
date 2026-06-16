from dash import html
import dash_bootstrap_components as dbc
import config


def _delta_badge(delta_info):
    """Render ▲/▼ delta badge from {"text": "+2.1", "dir": "up"|"down"|"flat"}."""
    if not delta_info or not isinstance(delta_info, dict):
        return None
    direction = delta_info.get("dir", "flat")
    text      = delta_info.get("text", "")
    if direction == "up":
        symbol, cls = "▲", "kpi-delta kpi-delta-up"
    elif direction == "down":
        symbol, cls = "▼", "kpi-delta kpi-delta-down"
    else:
        return None
    return html.Span(f"{symbol} {text}", className=cls)


def _alert_badge(direction):
    """Render a trend-alert pill for rapid 3-year change."""
    if direction == "up":
        return html.Span("⚠ Rapid ▲", className="kpi-alert kpi-alert-up")
    if direction == "down":
        return html.Span("⚠ Rapid ▼", className="kpi-alert kpi-alert-down")
    return None


def make_kpi_row(view: str, values: dict = None):
    """
    Build a row of 4 KPI cards for the given view.
    values: {id: str, id+"-delta": {"text","dir"}, id+"-alert": "up"|"down"}
    """
    kpis   = config.VIEW_KPIS.get(view, config.VIEW_KPIS["home"])
    values = values or {}

    cards = []
    for k in kpis:
        badge   = _delta_badge(values.get(k["id"] + "-delta"))
        alert   = _alert_badge(values.get(k["id"] + "-alert"))

        value_children = [
            html.Span(values.get(k["id"], "—"), className="kpi-value-text"),
        ]
        if badge:
            value_children.append(badge)

        body_children = [
            html.P(k["label"], className="kpi-label"),
            html.Div(value_children, id=k["id"], className="kpi-value"),
            html.Span(k["unit"], className="kpi-unit text-muted"),
        ]
        if alert:
            body_children.append(alert)

        cards.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(body_children),
                    className="kpi-card",
                ),
                md=3,
            )
        )

    return dbc.Row(cards, className="kpi-row g-3")
