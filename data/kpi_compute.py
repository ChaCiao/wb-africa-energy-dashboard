"""
KPI aggregation logic for each dashboard view.

All public functions return a dict keyed by the component IDs
defined in config.VIEW_KPIS. Values are pre-formatted strings
(or "—" when data is unavailable).
"""
import config
from data.loaders import load_access, load_tariffs, load_transition, load_institutions


# ── Helpers ───────────────────────────────────────────────────────────────────

def resolve_countries(scope: dict) -> list[str]:
    """Expand AGG_<POOL> entries in scope['selected'] into real country names."""
    if not scope:
        return []
    countries = []
    for s in scope.get("selected", []):
        if str(s).startswith("AGG_"):
            pool = s[4:]
            countries.extend(
                c for c in config.ALL_COUNTRIES if config.COUNTRY_REGION[c] == pool
            )
        else:
            countries.append(s)
    return list(dict.fromkeys(countries))  # deduplicate, preserve order


def _filt(df, countries, yr_min, yr_max):
    return df[df["country"].isin(countries) & df["year"].between(yr_min, yr_max)]


def _fmt(val, decimals: int = 1) -> str:
    if val is None:
        return "—"
    try:
        return f"{float(val):.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


# ── Per-view computers ────────────────────────────────────────────────────────

def _home(countries, yr_min, yr_max) -> dict:
    acc = _filt(load_access(),     countries, yr_min, yr_max)
    eco = _filt(load_tariffs(),    countries, yr_min, yr_max)
    tra = _filt(load_transition(), countries, yr_min, yr_max)
    latest_yr  = int(acc["year"].max()) if not acc.empty else yr_max
    latest_acc = acc[acc["year"] == latest_yr]
    return {
        "kpi-home-access": _fmt(acc["access_national_pct"].mean()),
        "kpi-home-tariff": _fmt(eco["residential_usd_kwh"].mean() * 100),
        "kpi-home-renew":  _fmt(tra["renewable_share_pct"].mean()),
        "kpi-home-unelec": _fmt(latest_acc["pop_without_electricity_millions"].sum()),
    }


def _access(countries, yr_min, yr_max) -> dict:
    df = _filt(load_access(), countries, yr_min, yr_max)
    if df.empty:
        return {}
    latest = df[df["year"] == df["year"].max()]
    return {
        "kpi-acc-national": _fmt(df["access_national_pct"].mean()),
        "kpi-acc-urban":    _fmt(df["access_urban_pct"].mean()),
        "kpi-acc-rural":    _fmt(df["access_rural_pct"].mean()),
        "kpi-acc-unelec":   _fmt(latest["pop_without_electricity_millions"].sum()),
    }


def _economics(countries, yr_min, yr_max) -> dict:
    df = _filt(load_tariffs(), countries, yr_min, yr_max)
    if df.empty:
        return {}
    latest = df[df["year"] == df["year"].max()]
    return {
        "kpi-eco-res":  _fmt(df["residential_usd_kwh"].mean() * 100),
        "kpi-eco-cost": _fmt(df["cost_recovery_pct"].mean()),
        "kpi-eco-comm": _fmt(df["commercial_usd_kwh"].mean() * 100),
        "kpi-eco-sub":  _fmt(latest["subsidy_usd_millions"].sum()),
    }


def _transition(countries, yr_min, yr_max) -> dict:
    df = _filt(load_transition(), countries, yr_min, yr_max)
    if df.empty:
        return {}
    latest = df[df["year"] == df["year"].max()]
    return {
        "kpi-tra-renew": _fmt(df["renewable_share_pct"].mean()),
        "kpi-tra-solar": _fmt(latest["solar_mw"].sum(), 0),
        "kpi-tra-hydro": _fmt(latest["hydro_mw"].sum(), 0),
        "kpi-tra-co2":   _fmt(df["co2_intensity_gco2_kwh"].mean()),
    }


def _institutions(countries) -> dict:
    df  = load_institutions()
    sub = df[df["country"].isin(countries)]
    if sub.empty:
        return {}
    n = len(sub)
    return {
        "kpi-ins-reg":  f"{int(sub['regulator_exists'].sum())} / {n}",
        "kpi-ins-cost": str(int((sub["tariff_mechanism"] == "cost-reflective").sum())),
        "kpi-ins-unb":  str(int(sub["unbundled"].sum())),
        "kpi-ins-ref":  _fmt(sub["reform_year"].mean(), 0),
    }


# ── Public entry point ────────────────────────────────────────────────────────

def compute_kpis(view: str, scope: dict, year_range: list) -> dict:
    """
    Return a {component_id: display_string} dict for the given view.
    Returns {} when scope or year_range is missing/empty.
    """
    countries = resolve_countries(scope)
    if not countries or not year_range:
        return {}

    yr_min, yr_max = int(year_range[0]), int(year_range[1])

    dispatch = {
        "home":         lambda: _home(countries, yr_min, yr_max),
        "access":       lambda: _access(countries, yr_min, yr_max),
        "economics":    lambda: _economics(countries, yr_min, yr_max),
        "transition":   lambda: _transition(countries, yr_min, yr_max),
        "institutions": lambda: _institutions(countries),
    }
    return dispatch.get(view, lambda: {})()
