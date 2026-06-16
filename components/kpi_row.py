from dash import html
import dash_bootstrap_components as dbc
import config


def make_kpi_row(view: str, values: dict = None):
    """
    Build a row of 4 KPI cards for the given view.
    values: {component_id: display_string} from kpi_compute.compute_kpis()
    When values is None or a key is missing, the card shows "—".
    """
    kpis   = config.VIEW_KPIS.get(view, config.VIEW_KPIS["home"])
    values = values or {}

    cards = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.P(k["label"], className="kpi-label"),
                        html.H3(
                            values.get(k["id"], "—"),
                            id=k["id"],
                            className="kpi-value",
                        ),
                        html.Span(k["unit"], className="kpi-unit text-muted"),
                    ]
                ),
                className="kpi-card",
            ),
            md=3,
        )
        for k in kpis
    ]
    return dbc.Row(cards, className="kpi-row g-3")
