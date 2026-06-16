from dash import html, dcc
import config

layout = html.Div(
    [
        html.H5("Filters", className="filter-heading"),
        html.Hr(),

        # ── Tier radio ────────────────────────────────────────────────
        html.Label("Analysis Tier", className="filter-label"),
        dcc.RadioItems(
            id="tier-radio",
            options=[
                {"label": "Tier 1 – Focus Countries",     "value": "tier1"},
                {"label": "Tier 2 – Regional Comparison", "value": "tier2"},
                {"label": "Tier 3 – Continental Overview","value": "tier3"},
            ],
            value="tier2",
            inputClassName="tier-radio-input",
            labelClassName="tier-radio-label",
            className="tier-radio",
        ),
        html.Hr(),

        # ── Country dropdown ──────────────────────────────────────────
        html.Label("Countries", className="filter-label"),
        dcc.Dropdown(
            id="country-dropdown",
            options=[{"label": c, "value": c} for c in config.ALL_COUNTRIES],
            value=[config.ALL_COUNTRIES[0]],
            multi=True,
            placeholder="Select countries…",
            className="country-dropdown",
        ),
        html.Hr(),

        # ── Year range slider ─────────────────────────────────────────
        html.Label("Year Range", className="filter-label"),
        dcc.RangeSlider(
            id="year-slider",
            min=config.YEAR_MIN,
            max=config.YEAR_MAX,
            step=1,
            value=[config.YEAR_MIN, config.YEAR_MAX],
            marks={y: str(y) for y in config.YEARS if y % 3 == 0},
            tooltip={"placement": "bottom", "always_visible": True},
            className="year-slider",
        ),
        html.Hr(),

        # ── Recent Countries ──────────────────────────────────────────
        html.Label("Recent Countries", className="filter-label"),
        html.Div(id="country-history-rail", className="history-rail"),
    ],
    className="filter-rail-inner",
)
