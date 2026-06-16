"""
Sprint 4-B: Country navigation history.
Tracks last 3 visited Focus Countries; renders clickable chips in sidebar.
"""
import json
import time

import dash
from dash import html, Input, Output, State, ALL
from dash.exceptions import PreventUpdate


def register_history_callbacks(app):

    # ── Track last 3 Focus Countries in session store ────────────────────
    @app.callback(
        Output("country-history", "data"),
        Input("map-click", "data"),
        State("country-history", "data"),
        prevent_initial_call=True,
    )
    def update_history(map_click, history):
        if not map_click or not map_click.get("country"):
            raise PreventUpdate
        country = map_click["country"]
        history = [c for c in (history or []) if c != country]
        history.insert(0, country)
        return history[:3]

    # ── Render history chips in sidebar ──────────────────────────────────
    @app.callback(
        Output("country-history-rail", "children"),
        Input("country-history", "data"),
    )
    def render_history_rail(history):
        if not history:
            return html.P("No recent countries.", className="history-empty")
        return [
            html.Button(
                country,
                id={"type": "history-btn", "index": i},
                className="history-btn",
                n_clicks=0,
                title=f"Open Focus View: {country}",
            )
            for i, country in enumerate(history[:3])
        ]

    # ── Navigate to Focus Country when a history chip is clicked ─────────
    @app.callback(
        Output("map-click", "data"),
        Input({"type": "history-btn", "index": ALL}, "n_clicks"),
        State("country-history", "data"),
        prevent_initial_call=True,
    )
    def navigate_from_history(n_clicks_list, history):
        if not any(n_clicks_list or []) or not history:
            raise PreventUpdate
        ctx = dash.callback_context
        triggered = ctx.triggered[0]["prop_id"]
        idx = json.loads(triggered.split(".")[0])["index"]
        if idx >= len(history):
            raise PreventUpdate
        return {"country": history[idx], "ts": time.time()}
