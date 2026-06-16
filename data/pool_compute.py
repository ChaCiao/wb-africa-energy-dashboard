"""
Sprint 5-B: Pool-level aggregate KPIs for SAPP / EAPP / CAPP.
Used by pool summary cards on the Overview page.
"""
import config
from data.loaders import load_access, load_tariffs, load_transition

_POOL_COUNTRIES = {
    pool: [c for c, p in config.COUNTRY_REGION.items() if p == pool]
    for pool in config.POWER_POOLS
}

_POOL_COLORS = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}

_POOL_FULL = {
    "SAPP": "Southern Africa Power Pool",
    "EAPP": "East Africa Power Pool",
    "CAPP": "Central Africa Power Pool",
}


def compute_pool_summaries(year_range: list) -> dict:
    """
    Return {pool: {access, tariff, renew, count, color, full_name}} for latest year.
    """
    yr_max = int(year_range[1]) if year_range else config.YEAR_MAX
    acc = load_access()
    tar = load_tariffs()
    tra = load_transition()

    result = {}
    for pool, ctrs in _POOL_COUNTRIES.items():
        acc_p = acc[acc["country"].isin(ctrs) & (acc["year"] == yr_max)]
        tar_p = tar[tar["country"].isin(ctrs) & (tar["year"] == yr_max)]
        tra_p = tra[tra["country"].isin(ctrs) & (tra["year"] == yr_max)]

        def _mean(df, col, scale=1.0, dec=1):
            if df.empty or col not in df.columns:
                return "—"
            return f"{float(df[col].mean()) * scale:.{dec}f}"

        result[pool] = {
            "access":    _mean(acc_p, "access_national_pct"),
            "tariff":    _mean(tar_p, "residential_usd_kwh", scale=100, dec=2),
            "renew":     _mean(tra_p, "renewable_share_pct"),
            "count":     len(ctrs),
            "color":     _POOL_COLORS[pool],
            "full_name": _POOL_FULL[pool],
        }
    return result
