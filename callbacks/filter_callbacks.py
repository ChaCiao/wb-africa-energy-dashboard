import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

import config


def register_filter_callbacks(app):

    @app.callback(
        Output("country-dropdown", "options"),
        Output("country-dropdown", "value"),
        Output("selected-scope",   "data"),
        Input("tier-radio",  "value"),
        Input("map-click",   "data"),
        State("tier-radio",  "value"),  # keep current tier for map-click path
    )
    def update_scope(tier_input, map_click, tier_state):
        """
        Two triggers:
          • tier-radio  → apply tier logic (Tier1/2/3)
          • map-click   → select that single country in Tier-2 context
        """
        ctx = dash.callback_context
        trigger = ctx.triggered[0]["prop_id"] if ctx.triggered else ""

        # ── Map click path ────────────────────────────────────────────────
        if "map-click" in trigger and map_click and map_click.get("country"):
            country = map_click["country"]
            options = [{"label": c, "value": c} for c in config.ALL_COUNTRIES]
            store   = {
                "tier":                "tier2",
                "selected":            [country],
                "available_countries": config.ALL_COUNTRIES,
                "aggregates":          [],
            }
            return options, [country], store

        # ── Tier radio path (default) ─────────────────────────────────────
        tier       = tier_input
        aggregates = []

        if tier == "tier1":
            countries = config.TIER1_COUNTRIES
            options   = [{"label": c, "value": c} for c in countries]
            default   = countries[:]

        elif tier == "tier2":
            countries = config.ALL_COUNTRIES
            options   = [{"label": c, "value": c} for c in countries]
            default   = [countries[0]]

        else:  # tier3
            countries  = config.ALL_COUNTRIES
            aggregates = config.POWER_POOLS
            options    = (
                [{"label": f"{p} (Pool Aggregate)", "value": f"AGG_{p}"} for p in aggregates]
                + [{"label": c, "value": c} for c in countries]
            )
            default    = [f"AGG_{p}" for p in aggregates]

        store = {
            "tier":                tier,
            "selected":            default,
            "available_countries": countries,
            "aggregates":          aggregates,
        }
        return options, default, store
