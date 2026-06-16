from dash import html, dcc
import dash_bootstrap_components as dbc
import config


def make_chart_grid(view: str, figures: dict = None):
    """
    Build a 2-up chart row for the given view.
    figures: {chart_id: go.Figure} from chart_builders.build_charts()
    When a figure is missing, shows a placeholder div instead.
    """
    a_label, b_label = config.CHART_LABELS.get(view, ("Chart A", "Chart B"))
    figures = figures or {}

    def _card(label, chart_id):
        fig = figures.get(chart_id)
        body = (
            dcc.Graph(
                id=chart_id,
                figure=fig,
                config={"displayModeBar": False, "responsive": True},
                className="chart-graph",
            )
            if fig is not None
            else html.Div(
                "Select countries in the sidebar to load this chart.",
                id=chart_id,
                className="chart-placeholder",
            )
        )
        return dbc.Card(dbc.CardBody([html.H5(label, className="chart-title"), body]))

    return dbc.Row(
        [
            dbc.Col(_card(a_label, f"chart-{view}-a"), md=6),
            dbc.Col(_card(b_label, f"chart-{view}-b"), md=6),
        ],
        className="chart-grid g-3",
    )
