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

        # customdata is set to [country_name, ...] on each country trace
        country = points[0].get("customdata")
        if isinstance(country, list):
            country = country[0] if country else None

        if not country or country not in config.ALL_COUNTRIES:
            raise PreventUpdate

        return {"country": str(country), "ts": time.time()}
