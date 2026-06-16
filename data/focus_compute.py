"""
Compute per-country focus data for the Focus Country view.
Returns KPIs and chart-ready DataFrames for a single country.
"""
import pandas as pd
import plotly.graph_objects as go

import config
from data.loaders import load_access, load_tariffs, load_transition, load_institutions

_AX  = dict(gridcolor="#E8EDF2", linecolor="#D0D8E0", zeroline=False)
_SSA = "#E67E22"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ssa_series(df, col, yr_min, yr_max, scale=1.0):
    """Per-year SSA average across all 13 countries."""
    filt = df[df["country"].isin(config.ALL_COUNTRIES) & df["year"].between(yr_min, yr_max)]
    if filt.empty:
        return pd.DataFrame()
    agg = filt.groupby("year")[col].mean().reset_index()
    agg[col] = agg[col] * scale
    return agg


def _mini_layout(height=175, **extra):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F8FAFC",
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=10, color="#1A2332"),
        margin=dict(l=46, r=12, t=14, b=32),
        height=height,
        legend=dict(
            orientation="h", yanchor="top", y=-0.20,
            xanchor="center", x=0.5, font=dict(size=9),
        ),
    )
    base.update(extra)
    return base


# ── KPI computation ───────────────────────────────────────────────────────────

def compute_focus_kpis(country: str, yr_min: int, yr_max: int) -> dict:
    """
    Return focus KPIs for a single country (latest year in range).
    Keys: kpi-focus-access / kpi-focus-tariff / kpi-focus-renew / kpi-focus-ownership
    Each may have a companion -ssa key with the SSA average.
    """
    acc  = load_access()
    tar  = load_tariffs()
    tra  = load_transition()
    ins  = load_institutions()

    acc_c  = acc[(acc["country"] == country)  & acc["year"].between(yr_min, yr_max)]
    tar_c  = tar[(tar["country"] == country)  & tar["year"].between(yr_min, yr_max)]
    tra_c  = tra[(tra["country"] == country)  & tra["year"].between(yr_min, yr_max)]
    ins_c  = ins[ins["country"] == country]

    # Country latest values
    latest_acc = acc_c[acc_c["year"] == acc_c["year"].max()] if not acc_c.empty else acc_c
    latest_tar = tar_c[tar_c["year"] == tar_c["year"].max()] if not tar_c.empty else tar_c
    latest_tra = tra_c[tra_c["year"] == tra_c["year"].max()] if not tra_c.empty else tra_c

    def _v(df, col, scale=1, dec=1):
        if df.empty or col not in df.columns:
            return "—"
        return f"{float(df[col].iloc[0]) * scale:.{dec}f}"

    # SSA averages (same period)
    def _ssa(df, col, scale=1, dec=1):
        filt = df[df["country"].isin(config.ALL_COUNTRIES) & df["year"].between(yr_min, yr_max)]
        if filt.empty:
            return "—"
        latest = filt[filt["year"] == filt["year"].max()]
        return f"{float(latest[col].mean()) * scale:.{dec}f}"

    ownership = ins_c["utility_ownership"].iloc[0].capitalize() if not ins_c.empty else "—"

    return {
        "kpi-focus-access":    _v(latest_acc, "access_national_pct"),
        "kpi-focus-tariff":    _v(latest_tar, "residential_usd_kwh", scale=100, dec=2),
        "kpi-focus-renew":     _v(latest_tra, "renewable_share_pct"),
        "kpi-focus-ownership": ownership,
        # SSA benchmarks
        "ssa-access":  _ssa(acc, "access_national_pct"),
        "ssa-tariff":  _ssa(tar, "residential_usd_kwh", scale=100, dec=2),
        "ssa-renew":   _ssa(tra, "renewable_share_pct"),
    }


# ── Focus charts (all years) ──────────────────────────────────────────────────

def build_focus_charts(country: str, yr_min: int, yr_max: int) -> dict:
    """
    Build 4 mini trend charts for a single country vs SSA average (full period).
    """
    acc = load_access()
    tar = load_tariffs()
    tra = load_transition()
    results = {}

    # Access: national rate
    acc_c = acc[(acc["country"] == country) & acc["year"].between(yr_min, yr_max)].sort_values("year")
    ssa_a = _ssa_series(acc, "access_national_pct", yr_min, yr_max)
    if not acc_c.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=acc_c["year"], y=acc_c["access_national_pct"].round(1),
            mode="lines+markers", name=country,
            line=dict(color="#0071BC", width=2), marker=dict(size=4),
            hovertemplate=f"<b>{country}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
        if not ssa_a.empty:
            fig.add_trace(go.Scatter(
                x=ssa_a["year"], y=ssa_a["access_national_pct"].round(1),
                mode="lines", name="SSA avg",
                line=dict(color=_SSA, width=1.5, dash="dot"),
                hovertemplate="SSA avg<br>%{x}: %{y:.1f}%<extra></extra>",
            ))
        fig.update_layout(**_mini_layout(), xaxis=dict(**_AX, tickformat="d"),
                          yaxis=dict(**_AX, range=[0, 105], title="Access (%)"))
        results["focus-access"] = fig

    # Economics: residential tariff
    tar_c = tar[(tar["country"] == country) & tar["year"].between(yr_min, yr_max)].sort_values("year")
    ssa_t = _ssa_series(tar, "residential_usd_kwh", yr_min, yr_max, scale=100)
    if not tar_c.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tar_c["year"], y=(tar_c["residential_usd_kwh"] * 100).round(2),
            mode="lines+markers", name=country,
            line=dict(color="#27AE60", width=2), marker=dict(size=4),
            hovertemplate=f"<b>{country}</b><br>%{{x}}: %{{y:.2f}} ¢/kWh<extra></extra>",
        ))
        if not ssa_t.empty:
            fig.add_trace(go.Scatter(
                x=ssa_t["year"], y=ssa_t["residential_usd_kwh"].round(2),
                mode="lines", name="SSA avg",
                line=dict(color=_SSA, width=1.5, dash="dot"),
                hovertemplate="SSA avg<br>%{x}: %{y:.2f} ¢/kWh<extra></extra>",
            ))
        fig.update_layout(**_mini_layout(), xaxis=dict(**_AX, tickformat="d"),
                          yaxis=dict(**_AX, title="¢/kWh"))
        results["focus-tariff"] = fig

    # Transition: renewable share
    tra_c = tra[(tra["country"] == country) & tra["year"].between(yr_min, yr_max)].sort_values("year")
    ssa_r = _ssa_series(tra, "renewable_share_pct", yr_min, yr_max)
    if not tra_c.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tra_c["year"], y=tra_c["renewable_share_pct"].round(1),
            mode="lines+markers", name=country,
            line=dict(color="#1ABC9C", width=2), marker=dict(size=4),
            fill="tozeroy", opacity=0.8,
            hovertemplate=f"<b>{country}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
        if not ssa_r.empty:
            fig.add_trace(go.Scatter(
                x=ssa_r["year"], y=ssa_r["renewable_share_pct"].round(1),
                mode="lines", name="SSA avg",
                line=dict(color=_SSA, width=1.5, dash="dot"),
                hovertemplate="SSA avg<br>%{x}: %{y:.1f}%<extra></extra>",
            ))
        fig.update_layout(**_mini_layout(), xaxis=dict(**_AX, tickformat="d"),
                          yaxis=dict(**_AX, range=[0, 110], title="Renew. %"))
        results["focus-renew"] = fig

    # Capacity mix: latest year stacked bar (country vs SSA avg)
    tra_latest = tra[(tra["country"] == country) & tra["year"].between(yr_min, yr_max)]
    if not tra_latest.empty:
        latest_yr = int(tra_latest["year"].max())
        row = tra_latest[tra_latest["year"] == latest_yr].iloc[0]
        energy_cols  = ["hydro_mw", "solar_mw", "wind_mw", "fossil_mw"]
        energy_label = {"hydro_mw": "Hydro", "solar_mw": "Solar",
                        "wind_mw": "Wind", "fossil_mw": "Fossil"}
        energy_color = {"hydro_mw": "#2980B9", "solar_mw": "#F39C12",
                        "wind_mw": "#1ABC9C", "fossil_mw": "#7F8C8D"}
        # SSA avg
        ssa_all = tra[tra["country"].isin(config.ALL_COUNTRIES) & (tra["year"] == latest_yr)]
        fig = go.Figure()
        for col in energy_cols:
            fig.add_trace(go.Bar(
                name=energy_label[col], x=[country, "SSA avg"],
                y=[round(float(row[col])), round(float(ssa_all[col].mean())) if not ssa_all.empty else 0],
                marker_color=energy_color[col],
                hovertemplate=f"<b>%{{x}}</b><br>{energy_label[col]}: %{{y:,}} MW<extra></extra>",
            ))
        fig.update_layout(**_mini_layout(), barmode="stack",
                          xaxis=dict(**_AX),
                          yaxis=dict(**_AX, title="MW"))
        results["focus-capacity"] = fig

    return results
