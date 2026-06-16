"""
Sprint 4-A: Country rankings per dashboard dimension.
Always ranks ALL 13 countries for full context; highlights selected ones.
"""
import pandas as pd
import config
from data.loaders import load_access, load_tariffs, load_transition, load_institutions
from data.kpi_compute import resolve_countries

_CFG = {
    "access": dict(
        loader=load_access, col="access_national_pct",
        label="National Access Rate (%)", ascending=False, ts=True,
    ),
    "economics": dict(
        loader=load_tariffs, col="cost_recovery_pct",
        label="Cost Recovery Rate (%)", ascending=False, ts=True,
    ),
    "transition": dict(
        loader=load_transition, col="renewable_share_pct",
        label="Renewable Share (%)", ascending=False, ts=True,
    ),
    "institutions": dict(
        loader=load_institutions, col="reform_year",
        label="Reform Year (earlier = longer reform track)", ascending=True, ts=False,
    ),
}


def build_rankings(view: str, scope: dict, year_range: list) -> pd.DataFrame:
    """
    Return ranked DataFrame for 13 SSA countries on the primary metric.
    Columns: rank, country, region, value, selected, metric_label
    """
    cfg = _CFG.get(view)
    if cfg is None:
        return pd.DataFrame()

    df       = cfg["loader"]()
    selected = resolve_countries(scope) if scope else []

    if cfg["ts"] and year_range:
        yr_max = int(year_range[1])
        filt = df[df["country"].isin(config.ALL_COUNTRIES) & (df["year"] == yr_max)]
    else:
        filt = df[df["country"].isin(config.ALL_COUNTRIES)]

    if filt.empty:
        return pd.DataFrame()

    avg = (filt.groupby("country")[cfg["col"]]
               .mean().reset_index()
               .rename(columns={cfg["col"]: "value"}))
    avg["value"]        = avg["value"].round(1)
    avg                 = avg.sort_values("value", ascending=cfg["ascending"]).reset_index(drop=True)
    avg["rank"]         = range(1, len(avg) + 1)
    avg["selected"]     = avg["country"].isin(selected)
    avg["region"]       = avg["country"].map(config.COUNTRY_REGION)
    avg["metric_label"] = cfg["label"]

    return avg[["rank", "country", "region", "value", "selected", "metric_label"]]


def country_rank(view: str, country: str, year_range: list) -> tuple[int, int]:
    """Return (rank, total) for a single country in the full 13-country ranking."""
    df = build_rankings(view, None, year_range)
    if df.empty or country not in df["country"].values:
        return None, len(config.ALL_COUNTRIES)
    rank = int(df[df["country"] == country]["rank"].iloc[0])
    return rank, len(df)
