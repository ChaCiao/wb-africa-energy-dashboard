"""
Build DataTable columns + data for each dashboard view.
Returns (columns_list, records_list) ready to pass to dash_table.DataTable.
"""
import pandas as pd

from data.loaders import load_access, load_tariffs, load_transition, load_institutions
from data.kpi_compute import resolve_countries

# ── Column definitions per view ───────────────────────────────────────────────
# (csv_key, [(field, display_name, type), ...])

_COLS = {
    "home": ("access", [
        ("country",                       "Country",            "text"),
        ("year",                          "Year",               "numeric"),
        ("region",                        "Region",             "text"),
        ("access_national_pct",           "National Access (%)", "numeric"),
        ("access_urban_pct",              "Urban (%)",           "numeric"),
        ("access_rural_pct",              "Rural (%)",           "numeric"),
        ("pop_without_electricity_millions", "Pop. w/o Elec. (M)", "numeric"),
    ]),
    "access": ("access", [
        ("country",                          "Country",             "text"),
        ("year",                             "Year",                "numeric"),
        ("region",                           "Region",              "text"),
        ("access_national_pct",              "National Access (%)", "numeric"),
        ("access_urban_pct",                 "Urban (%)",           "numeric"),
        ("access_rural_pct",                 "Rural (%)",           "numeric"),
        ("pop_without_electricity_millions", "Pop. w/o Elec. (M)", "numeric"),
        ("new_connections_thousands",        "New Connections (K)", "numeric"),
        ("investment_usd_millions",          "Investment (M USD)",  "numeric"),
    ]),
    "economics": ("tariffs", [
        ("country",               "Country",             "text"),
        ("year",                  "Year",                "numeric"),
        ("region",                "Region",              "text"),
        ("residential_usd_kwh",   "Residential ($/kWh)", "numeric"),
        ("commercial_usd_kwh",    "Commercial ($/kWh)",  "numeric"),
        ("industrial_usd_kwh",    "Industrial ($/kWh)",  "numeric"),
        ("avg_usd_kwh",           "Avg. ($/kWh)",        "numeric"),
        ("cost_recovery_pct",     "Cost Recovery (%)",   "numeric"),
        ("subsidy_usd_millions",  "Subsidy (M USD)",     "numeric"),
    ]),
    "transition": ("transition", [
        ("country",               "Country",              "text"),
        ("year",                  "Year",                 "numeric"),
        ("region",                "Region",               "text"),
        ("total_capacity_mw",     "Total Cap. (MW)",      "numeric"),
        ("renewable_mw",          "Renewable (MW)",       "numeric"),
        ("renewable_share_pct",   "Renewable Share (%)",  "numeric"),
        ("solar_mw",              "Solar (MW)",           "numeric"),
        ("wind_mw",               "Wind (MW)",            "numeric"),
        ("hydro_mw",              "Hydro (MW)",           "numeric"),
        ("co2_intensity_gco2_kwh","CO₂ (gCO₂/kWh)",      "numeric"),
    ]),
    "institutions": ("institutions", [
        ("country",          "Country",          "text"),
        ("region",           "Region",           "text"),
        ("utility_name",     "Utility",          "text"),
        ("utility_ownership","Ownership",        "text"),
        ("regulator_exists", "Regulator",        "text"),
        ("tariff_mechanism", "Tariff Mechanism", "text"),
        ("unbundled",        "Unbundled",        "text"),
        ("reform_year",      "Reform Year",      "numeric"),
    ]),
}

_LOADERS = {
    "access":       load_access,
    "tariffs":      load_tariffs,
    "transition":   load_transition,
    "institutions": load_institutions,
}

# Rounding rules for numeric columns
_ROUND = {
    "access_national_pct": 1, "access_urban_pct": 1, "access_rural_pct": 1,
    "pop_without_electricity_millions": 1, "new_connections_thousands": 0,
    "investment_usd_millions": 1,
    "residential_usd_kwh": 4, "commercial_usd_kwh": 4,
    "industrial_usd_kwh": 4, "avg_usd_kwh": 4,
    "cost_recovery_pct": 1, "subsidy_usd_millions": 1,
    "total_capacity_mw": 0, "renewable_mw": 0, "solar_mw": 0,
    "wind_mw": 0, "hydro_mw": 0, "geothermal_mw": 0, "fossil_mw": 0,
    "renewable_share_pct": 1, "co2_intensity_gco2_kwh": 1,
}

_BOOL_COLS = {"regulator_exists", "unbundled"}

# CSVs that are snapshots (no meaningful time series) — skip year range filter
_SKIP_YEAR_FILTER = {"institutions"}


def build_table(view: str, scope: dict, year_range: list):
    """
    Return (columns, records) for the given view + filter state.
    columns: list of dash DataTable column dicts
    records: list of row dicts
    """
    countries = resolve_countries(scope)
    if not countries:
        return [], []

    csv_key, col_defs = _COLS.get(view, _COLS["home"])
    df: pd.DataFrame = _LOADERS[csv_key]().copy()

    # ── Filter rows ───────────────────────────────────────────────────────
    df = df[df["country"].isin(countries)]
    if "year" in df.columns and year_range and csv_key not in _SKIP_YEAR_FILTER:
        yr_min, yr_max = int(year_range[0]), int(year_range[1])
        df = df[df["year"].between(yr_min, yr_max)]

    if df.empty:
        return [], []

    # ── Select & order columns ────────────────────────────────────────────
    fields  = [f for f, _, _ in col_defs if f in df.columns]
    sliced  = df[fields]
    sort_by = [c for c in ["country", "year"] if c in sliced.columns]
    df      = sliced.sort_values(sort_by) if sort_by else sliced

    # ── Format ────────────────────────────────────────────────────────────
    for col in fields:
        if col in _BOOL_COLS and col in df.columns:
            df[col] = df[col].map({True: "Yes", False: "No"})
        elif col in _ROUND and col in df.columns:
            df[col] = df[col].round(_ROUND[col])

    # ── Build column defs ─────────────────────────────────────────────────
    columns = [
        {"name": label, "id": field, "type": dtype}
        for field, label, dtype in col_defs
        if field in df.columns
    ]
    return columns, df.to_dict("records")
