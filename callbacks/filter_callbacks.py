from dash import Input, Output
import config


def register_filter_callbacks(app):
    @app.callback(
        Output("country-dropdown", "options"),
        Output("country-dropdown", "value"),
        Output("selected-scope",   "data"),
        Input("tier-radio", "value"),
    )
    def update_scope_from_tier(tier):
        """
        Tier radio drives the country dropdown and the shared scope Store.

        Tier 1 → 2 focus countries, all pre-selected.
        Tier 2 → 13 countries, first one selected by default.
        Tier 3 → 3 pool aggregates + 13 countries; aggregates selected by default.
        """
        aggregates = []

        if tier == "tier1":
            countries = config.TIER1_COUNTRIES
            options   = [{"label": c, "value": c} for c in countries]
            default   = countries[:]  # select both

        elif tier == "tier2":
            countries = config.ALL_COUNTRIES
            options   = [{"label": c, "value": c} for c in countries]
            default   = [countries[0]]

        else:  # tier3
            countries  = config.ALL_COUNTRIES
            aggregates = config.POWER_POOLS
            options = (
                [
                    {"label": f"{p} (Pool Aggregate)", "value": f"AGG_{p}"}
                    for p in aggregates
                ]
                + [{"label": c, "value": c} for c in countries]
            )
            default = [f"AGG_{p}" for p in aggregates]

        store = {
            "tier":                tier,
            "selected":            default,
            "available_countries": countries,
            "aggregates":          aggregates,
        }
        return options, default, store
