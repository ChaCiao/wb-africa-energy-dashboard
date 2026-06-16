import dash
from dash import Input, Output, State, html

from components.kpi_row import make_kpi_row
from components.chart_grid import make_chart_grid
from components.overview import make_overview
from components.data_table import make_data_table
from data.kpi_compute import compute_kpis
from data.chart_builders import build_charts, build_mini_charts
from data.table_builder import build_table


def _dim_page(view: str, values: dict = None, figures: dict = None,
              table_columns=None, table_data=None):
    return html.Div([
        make_kpi_row(view, values),
        html.Hr(className="section-divider"),
        make_chart_grid(view, figures),
        make_data_table(table_columns, table_data),
    ])


_VIEW_MAP = {
    "home-btn":         "home",
    "tab-access":       "access",
    "tab-economics":    "economics",
    "tab-transition":   "transition",
    "tab-institutions": "institutions",
}


def register_layout_callbacks(app):

    # ── Sidebar toggle — clientside, no server round-trip ────────────────
    app.clientside_callback(
        """
        function(n_clicks, is_open) {
            var open = (is_open !== false && is_open !== null);
            if (n_clicks && n_clicks > 0) { open = !open; }
            return [
                open ? "sidebar-wrapper" : "sidebar-wrapper closed",
                open ? "◀" : "▶",
                open
            ];
        }
        """,
        Output("sidebar-wrapper",    "className"),
        Output("sidebar-toggle-btn", "children"),
        Output("sidebar-open",       "data"),
        Input("sidebar-toggle-btn",  "n_clicks"),
        State("sidebar-open",        "data"),
    )

    # ── View switching + KPI + charts + table ────────────────────────────
    @app.callback(
        Output("page-content",       "children"),
        Output("current-view",       "data"),
        Output("tab-access",         "className"),
        Output("tab-economics",      "className"),
        Output("tab-transition",     "className"),
        Output("tab-institutions",   "className"),
        Input("home-btn",            "n_clicks"),
        Input("tab-access",          "n_clicks"),
        Input("tab-economics",       "n_clicks"),
        Input("tab-transition",      "n_clicks"),
        Input("tab-institutions",    "n_clicks"),
        Input("selected-scope",      "data"),
        Input("year-slider",         "value"),
        State("current-view",        "data"),
    )
    def update_view(home_n, acc_n, eco_n, tra_n, ins_n, scope, year_range, current_view):
        ctx = dash.callback_context

        if not ctx.triggered or ctx.triggered[0]["value"] is None:
            view = current_view or "home"
        else:
            trigger = ctx.triggered[0]["prop_id"].split(".")[0]
            view = _VIEW_MAP.get(trigger, current_view or "home")

        def tab_cls(tab_view):
            return "dim-tab dim-tab-active" if view == tab_view else "dim-tab"

        values = compute_kpis(view, scope, year_range)

        if view == "home":
            mini_figures = build_mini_charts(scope, year_range)
            content = make_overview(values, mini_figures)
        else:
            figures = build_charts(view, scope, year_range)
            table_columns, table_data = build_table(view, scope, year_range)
            content = _dim_page(view, values, figures, table_columns, table_data)

        return (
            content,
            view,
            tab_cls("access"),
            tab_cls("economics"),
            tab_cls("transition"),
            tab_cls("institutions"),
        )
