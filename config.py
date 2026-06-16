TIER1_COUNTRIES = ["Lesotho", "Namibia"]

ALL_COUNTRIES = [
    "Lesotho", "Namibia", "Botswana", "Zambia", "Zimbabwe",
    "Mozambique", "Malawi", "Ethiopia", "Kenya", "Tanzania",
    "Uganda", "DRC", "Cameroon",
]

COUNTRY_REGION = {
    "Lesotho":    "SAPP",
    "Namibia":    "SAPP",
    "Botswana":   "SAPP",
    "Zambia":     "SAPP",
    "Zimbabwe":   "SAPP",
    "Mozambique": "SAPP",
    "Malawi":     "SAPP",
    "Ethiopia":   "EAPP",
    "Kenya":      "EAPP",
    "Tanzania":   "EAPP",
    "Uganda":     "EAPP",
    "DRC":        "CAPP",
    "Cameroon":   "CAPP",
}

POWER_POOLS = ["SAPP", "EAPP", "CAPP"]

YEARS     = list(range(2015, 2025))
YEAR_MIN  = 2015
YEAR_MAX  = 2024

TIERS = {
    "tier1": "Tier 1 – Focus Countries",
    "tier2": "Tier 2 – Regional Comparison",
    "tier3": "Tier 3 – Continental Overview",
}

MOCK_SOURCE_URL = "https://placeholder.worldbank.org/mock-data"

# ── Per-view KPI definitions ──────────────────────────────────────────────────
# Each entry: {"id": str, "label": str, "unit": str}
VIEW_KPIS = {
    "home": [
        {"id": "kpi-home-access",  "label": "Avg. Electrification Rate", "unit": "%"},
        {"id": "kpi-home-tariff",  "label": "Avg. Residential Tariff",   "unit": "¢/kWh"},
        {"id": "kpi-home-renew",   "label": "Avg. Renewable Share",       "unit": "%"},
        {"id": "kpi-home-unelec",  "label": "Pop. Without Electricity",   "unit": "M"},
    ],
    "access": [
        {"id": "kpi-acc-national", "label": "National Access Rate",  "unit": "%"},
        {"id": "kpi-acc-urban",    "label": "Urban Access Rate",     "unit": "%"},
        {"id": "kpi-acc-rural",    "label": "Rural Access Rate",     "unit": "%"},
        {"id": "kpi-acc-unelec",   "label": "Pop. Without Elec.",    "unit": "M"},
    ],
    "economics": [
        {"id": "kpi-eco-res",  "label": "Avg. Residential Tariff", "unit": "¢/kWh"},
        {"id": "kpi-eco-cost", "label": "Cost Recovery Rate",      "unit": "%"},
        {"id": "kpi-eco-comm", "label": "Avg. Commercial Tariff",  "unit": "¢/kWh"},
        {"id": "kpi-eco-sub",  "label": "Total Implicit Subsidy",  "unit": "M USD"},
    ],
    "transition": [
        {"id": "kpi-tra-renew", "label": "Avg. Renewable Share", "unit": "%"},
        {"id": "kpi-tra-solar", "label": "Solar Capacity",        "unit": "MW"},
        {"id": "kpi-tra-hydro", "label": "Hydro Capacity",        "unit": "MW"},
        {"id": "kpi-tra-co2",   "label": "CO₂ Intensity",         "unit": "gCO₂/kWh"},
    ],
    "institutions": [
        {"id": "kpi-ins-reg",  "label": "Countries w/ Regulator",   "unit": "/ 13"},
        {"id": "kpi-ins-cost", "label": "Cost-Reflective Tariff",   "unit": "ctrs"},
        {"id": "kpi-ins-unb",  "label": "Unbundled Utilities",      "unit": "ctrs"},
        {"id": "kpi-ins-ref",  "label": "Avg. Sector Reform Year",  "unit": ""},
    ],
}

# ── Per-view chart placeholder labels ────────────────────────────────────────
CHART_LABELS = {
    "home": (
        "Access & Economics — Overview",
        "Transition & Institutions — Overview",
    ),
    "access": (
        "Electrification Rate Trend (% national)",
        "Urban vs. Rural Access Gap (%)",
    ),
    "economics": (
        "Residential Tariff Trend ($/kWh)",
        "Cost Recovery Rate by Country (%)",
    ),
    "transition": (
        "Renewable Share Trend (%)",
        "Installed Capacity Mix (MW)",
    ),
    "institutions": (
        "Utility Ownership Structure",
        "Regulatory Environment by Country",
    ),
}
