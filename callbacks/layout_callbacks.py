import dash
from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc

from components.kpi_row import make_kpi_row
from components.chart_grid import make_chart_grid
from components.overview import make_overview
from components.data_table import make_data_table
from components.focus_country import make_focus_page
from components.rankings_table import make_rankings_table
from data.kpi_compute import compute_kpis
from data.chart_builders import build_charts, build_mini_charts
from data.table_builder import build_table
from data.focus_compute import compute_focus_kpis, build_focus_charts
from data.rankings import build_rankings
from data.scatter_compute import build_scatter
from data.alert_compute import compute_alerts
from data.pool_compute import compute_pool_summaries


def _dim_page(view: str, values: dict = None, figures: dict = None,
              table_columns=None, table_data=None,
              rankings_df=None, scatter_fig=None):
    analytics_row = None
    if scatter_fig is not None or (rankings_df is not None and not rankings_df.empty):
        cols = []
        if scatter_fig is not None:
            cols.append(dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("Correlation Analysis", className="chart-title"),
                    dcc.Graph(
                        id=f"scatter-{view}",
                        figure=scatter_fig,
                        config={"displayModeBar": False},
                        style={"height": "270px"},
                    ),
                ])),
                md=8,
            ))
        if rankings_df is not None and not rankings_df.empty:
            cols.append(dbc.Col(
                make_rankings_table(rankings_df, view),
                md=4 if scatter_fig is not None else 12,
            ))
        analytics_row = dbc.Row(cols, className="g-3 mt-1")

    return html.Div([
        make_kpi_row(view, values),
        html.Hr(className="section-divider"),
        make_chart_grid(view, figures),
        make_data_table(table_columns, table_data),
        (analytics_row if analytics_row else html.Span()),
    ])


_VIEW_MAP = {
    "home-btn":         "home",
    "focus-back-btn":   "home",
    "tab-access":       "access",
    "tab-economics":    "economics",
    "tab-transition":   "transition",
    "tab-institutions": "institutions",
}


def register_layout_callbacks(app):

    # ── Show / hide focus-view chrome (back btn + compare dropdown) ──────
    @app.callback(
        Output("focus-back-btn",        "style"),
        Output("compare-controls-wrapper", "style"),
        Input("current-view", "data"),
    )
    def toggle_focus_chrome(view):
        if view == "focus":
            return ({"display": "block", "marginBottom": "8px"},
                    {"display": "block", "maxWidth": "360px", "marginBottom": "12px"})
        return {"display": "none"}, {"display": "none"}

    # ── Dark mode toggle — clientside, persisted in localStorage ────────
    app.clientside_callback(
        """
        function(n_clicks, is_dark) {
            var dark = (n_clicks && n_clicks > 0) ? !is_dark : (is_dark || false);
            if (dark) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
            return dark;
        }
        """,
        Output("dark-mode", "data"),
        Input("dark-mode-btn", "n_clicks"),
        State("dark-mode",     "data"),
    )

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
        Input("focus-back-btn",      "n_clicks"),
        Input("tab-access",          "n_clicks"),
        Input("tab-economics",       "n_clicks"),
        Input("tab-transition",      "n_clicks"),
        Input("tab-institutions",    "n_clicks"),
        Input("selected-scope",      "data"),
        Input("year-slider",         "value"),
        Input("map-click",           "data"),
        State("current-view",        "data"),
    )
    def update_view(home_n, back_n, acc_n, eco_n, tra_n, ins_n,
                    scope, year_range, map_click, current_view):
        ctx = dash.callback_context

        if not ctx.triggered or ctx.triggered[0]["value"] is None:
            view = current_view or "home"
        else:
            trigger = ctx.triggered[0]["prop_id"].split(".")[0]

            if trigger == "map-click" and map_click and map_click.get("country"):
                view = "focus"
            else:
                view = _VIEW_MAP.get(trigger, current_view or "home")

        def tab_cls(tab_view):
            return "dim-tab dim-tab-active" if view == tab_view else "dim-tab"

        # ── Focus Country view (map click) ───────────────────────────
        if view == "focus" and map_click and map_click.get("country"):
            country = map_click["country"]
            yr_min  = int(year_range[0]) if year_range else 2015
            yr_max  = int(year_range[1]) if year_range else 2024
            kpis    = compute_focus_kpis(country, yr_min, yr_max)
            charts  = build_focus_charts(country, yr_min, yr_max)
            content = make_focus_page(country, kpis, charts, year_range)
            return (content, view,
                    tab_cls("access"), tab_cls("economics"),
                    tab_cls("transition"), tab_cls("institutions"))

        values = compute_kpis(view, scope, year_range)

        if view == "home":
            mini_figures = build_mini_charts(scope, year_range)
            pool_data    = compute_pool_summaries(year_range)
            content = make_overview(values, mini_figures, pool_data=pool_data)
        else:
            alerts  = compute_alerts(view, scope, year_range)
            values.update(alerts)
            figures         = build_charts(view, scope, year_range)
            table_columns, table_data = build_table(view, scope, year_range)
            rankings_df     = build_rankings(view, scope, year_range)
            scatter_fig     = build_scatter(view, scope, year_range)
            content = _dim_page(view, values, figures, table_columns, table_data,
                                rankings_df=rankings_df, scatter_fig=scatter_fig)

        return (
            content,
            view,
            tab_cls("access"),
            tab_cls("economics"),
            tab_cls("transition"),
            tab_cls("institutions"),
        )
