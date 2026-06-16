"""Sprint 6-C: ▶ Play animation — advances year-slider.value[1] on each interval tick."""
import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

import config


def register_play_callbacks(app):

    # ── Toggle interval on button click (clientside — instant) ───────────
    app.clientside_callback(
        """
        function(n_clicks, is_disabled) {
            if (!n_clicks) {
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            var d = (is_disabled === null || is_disabled === undefined || is_disabled === true);
            return [!d, d ? '■ Stop' : '▶ Play'];
        }
        """,
        Output("play-interval", "disabled"),
        Output("play-btn",      "children"),
        Input("play-btn",       "n_clicks"),
        State("play-interval",  "disabled"),
        prevent_initial_call=True,
    )

    # ── Advance year on each tick; auto-stop at YEAR_MAX ─────────────────
    @app.callback(
        Output("year-slider",   "value"),
        Output("play-interval", "disabled",  allow_duplicate=True),
        Output("play-btn",      "children",  allow_duplicate=True),
        Input("play-interval",  "n_intervals"),
        State("year-slider",    "value"),
        prevent_initial_call=True,
    )
    def step_year(n_intervals, year_range):
        if not year_range:
            raise PreventUpdate
        yr_min  = int(year_range[0])
        yr_max  = int(year_range[1])
        new_max = yr_max + 1
        if new_max >= config.YEAR_MAX:
            return [yr_min, config.YEAR_MAX], True, "▶ Play"
        return [yr_min, new_max], dash.no_update, dash.no_update
