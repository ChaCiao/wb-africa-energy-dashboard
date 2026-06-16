"""
Sprint 5-B: Trend alerts — flags KPIs with rapid 3-year change exceeding thresholds.
Alert keys injected into the values dict as kpi_id + "-alert": "up" | "down".
"""
import pandas as pd
import config
from data.loaders import load_access, load_tariffs, load_transition
from data.kpi_compute import resolve_countries

_THRESHOLDS = {
    "access_national_pct":    5.0,    # percentage points
    "access_rural_pct":       5.0,
    "residential_usd_kwh":    0.003,  # ~15 % of typical 0.02 $/kWh
    "cost_recovery_pct":      10.0,
    "renewable_share_pct":    5.0,
    "co2_intensity_gco2_kwh": 20.0,
}

_VIEW_CHECKS = {
    "access": [
        (load_access,     "access_national_pct",    "kpi-acc-national"),
        (load_access,     "access_rural_pct",        "kpi-acc-rural"),
    ],
    "economics": [
        (load_tariffs,    "residential_usd_kwh",     "kpi-eco-res"),
        (load_tariffs,    "cost_recovery_pct",        "kpi-eco-cost"),
    ],
    "transition": [
        (load_transition, "renewable_share_pct",     "kpi-tra-renew"),
        (load_transition, "co2_intensity_gco2_kwh",  "kpi-tra-co2"),
    ],
}


def compute_alerts(view: str, scope: dict, year_range: list) -> dict:
    """Return {kpi_id+"-alert": "up"|"down"} for KPIs showing rapid 3-year trend."""
    checks = _VIEW_CHECKS.get(view, [])
    if not checks or not year_range:
        return {}

    countries = resolve_countries(scope) if scope else config.ALL_COUNTRIES
    yr_max = int(year_range[1])
    yr_ref = max(int(year_range[0]), yr_max - 3)
    if yr_ref == yr_max:
        return {}

    alerts = {}
    for loader_fn, col, kpi_id in checks:
        df    = loader_fn()
        df_c  = df[df["country"].isin(countries)]
        latest = df_c[df_c["year"] == yr_max][col].mean() if "year" in df_c.columns else float("nan")
        ref    = df_c[df_c["year"] == yr_ref][col].mean() if "year" in df_c.columns else float("nan")
        if pd.isna(latest) or pd.isna(ref):
            continue
        delta  = float(latest - ref)
        thresh = _THRESHOLDS.get(col, 9999)
        if abs(delta) >= thresh:
            alerts[kpi_id + "-alert"] = "up" if delta > 0 else "down"

    return alerts
