"""Sprint 6-C: Clicking a chart data point navigates to that country's Focus view."""
import time
import json
import dash
from dash import Input, Output, ALL
from dash.exceptions import PreventUpdate

import config


def register_chart_click_callbacks(app):

    @app.callback(
        Output("map-click", "data", allow_duplicate=True),
        Input({"type": "dim-chart", "index": ALL}, "clickData"),
        prevent_initial_call=True,
    )
    def chart_point_to_focus(click_data_list):
        if not any(click_data_list):
            raise PreventUpdate

        ctx = dash.callback_context
        if not ctx.triggered or not ctx.triggered[0]["value"]:
            raise PreventUpdate

        click_data = ctx.triggered[0]["value"]
        points     = click_data.get("points", [])
        if not points:
            raise PreventUpdate

        pt = points[0]

        # 1st: customdata (trend charts, scatter, gap chart)
        country = pt.get("customdata")
        if isinstance(country, list):
            country = country[0] if country else None

        # 2nd: axis labels / text (bar charts, heatmap)
        if not country or country not in config.ALL_COUNTRIES:
            for key in ("y", "x", "text"):
                val = pt.get(key)
                if isinstance(val, str) and val in config.ALL_COUNTRIES:
                    country = val
                    break

        if not country or country not in config.ALL_COUNTRIES:
            raise PreventUpdate

        return {"country": str(country), "ts": time.time()}
