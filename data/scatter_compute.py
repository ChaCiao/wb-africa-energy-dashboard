"""
Sprint 4-A: Scatter / correlation charts for each dimension.
Shows ALL 13 countries; highlights selected ones with larger markers.
"""
import plotly.graph_objects as go
import pandas as pd

import config
from data.loaders import load_access, load_tariffs, load_transition
from data.kpi_compute import resolve_countries

_POOL_COLOR = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}
_AX         = dict(gridcolor="#E8EDF2", linecolor="#D0D8E0", zeroline=False)


def _base(**kw):
    d = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F8FAFC",
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=11, color="#1A2332"),
        margin=dict(l=60, r=20, t=28, b=55),
        height=270,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.18,
                    xanchor="center", x=0.5, font=dict(size=9)),
    )
    d.update(kw)
    return d


def _scatter_data(loader, x_col, y_col, scope, year_range,
                  x_scale=1.0, y_scale=1.0):
    """
    Return a DataFrame with one row per country, aggregated to latest year.
    Columns: country, region, x, y, selected
    """
    df       = loader()
    selected = resolve_countries(scope) if scope else []

    if "year" in df.columns and year_range:
        yr_max = int(year_range[1])
        filt   = df[df["country"].isin(config.ALL_COUNTRIES) & (df["year"] == yr_max)]
    else:
        filt   = df[df["country"].isin(config.ALL_COUNTRIES)]

    if filt.empty:
        return pd.DataFrame()

    agg = filt.groupby("country")[[x_col, y_col]].mean().reset_index()
    agg["x"]        = agg[x_col] * x_scale
    agg["y"]        = agg[y_col] * y_scale
    agg["selected"] = agg["country"].isin(selected)
    agg["region"]   = agg["country"].map(config.COUNTRY_REGION)
    return agg


def _build_scatter_fig(df, x_label, y_label, title):
    if df.empty:
        return None

    fig = go.Figure()

    for region, color in _POOL_COLOR.items():
        sub = df[df["region"] == region]
        if sub.empty:
            continue

        # Unselected (background, smaller)
        bg = sub[~sub["selected"]]
        if not bg.empty:
            fig.add_trace(go.Scatter(
                x=bg["x"].round(2), y=bg["y"].round(1),
                mode="markers+text",
                name=f"{region} Pool",
                text=bg["country"],
                customdata=bg["country"].tolist(),
                textposition="top center",
                textfont=dict(size=8, color="#8A9BAC"),
                marker=dict(color=color, size=8, opacity=0.35,
                            line=dict(color="white", width=1)),
                showlegend=True,
                hovertemplate=(
                    "<b>%{customdata}</b><br>"
                    f"{x_label}: %{{x}}<br>"
                    f"{y_label}: %{{y}}<br>"
                    "<extra></extra>"
                ),
            ))

        # Selected (foreground, larger)
        sel = sub[sub["selected"]]
        if not sel.empty:
            fig.add_trace(go.Scatter(
                x=sel["x"].round(2), y=sel["y"].round(1),
                mode="markers+text",
                name=f"{region} (selected)",
                text=sel["country"],
                customdata=sel["country"].tolist(),
                textposition="top center",
                textfont=dict(size=9, color="#1A2332", family="Segoe UI"),
                marker=dict(color=color, size=13, opacity=1.0,
                            line=dict(color="white", width=1.5)),
                showlegend=False,
                hovertemplate=(
                    "<b>%{customdata}</b><br>"
                    f"{x_label}: %{{x}}<br>"
                    f"{y_label}: %{{y}}<br>"
                    "<extra></extra>"
                ),
            ))

    fig.update_layout(
        **_base(title=dict(text=title, font=dict(size=12), x=0.5, xanchor="center")),
        xaxis=dict(**_AX, title=x_label),
        yaxis=dict(**_AX, title=y_label),
    )
    return fig


# ── Per-view scatter definitions ─────────────────────────────────────────────

def build_scatter(view: str, scope: dict, year_range: list):
    """Return a go.Figure or None for the correlation scatter chart."""

    if view == "access":
        df = _scatter_data(load_access, "access_rural_pct", "access_national_pct",
                           scope, year_range)
        return _build_scatter_fig(
            df,
            x_label="Rural Access Rate (%)",
            y_label="National Access Rate (%)",
            title="Rural vs. National Access Rate",
        )

    if view == "economics":
        df = _scatter_data(load_tariffs, "residential_usd_kwh", "cost_recovery_pct",
                           scope, year_range, x_scale=100)
        return _build_scatter_fig(
            df,
            x_label="Residential Tariff (¢/kWh)",
            y_label="Cost Recovery Rate (%)",
            title="Tariff Level vs. Cost Recovery",
        )

    if view == "transition":
        df = _scatter_data(load_transition, "renewable_share_pct", "co2_intensity_gco2_kwh",
                           scope, year_range)
        return _build_scatter_fig(
            df,
            x_label="Renewable Share (%)",
            y_label="CO₂ Intensity (gCO₂/kWh)",
            title="Renewable Share vs. Carbon Intensity",
        )

    return None
