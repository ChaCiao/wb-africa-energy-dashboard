"""
Plotly figure builders for each dashboard dimension.

build_charts(view, scope, year_range) → {chart_id: go.Figure}
build_mini_charts(scope, year_range)  → {mini_id: go.Figure}

Sprint 3-B additions:
  - SSA average reference line on all trend (A) charts
  - Pool-aggregate mode when scope contains AGG_SAPP/EAPP/CAPP
"""
import plotly.graph_objects as go

import config
from data.loaders import load_access, load_tariffs, load_transition, load_institutions
from data.kpi_compute import resolve_countries

# ── Design constants ──────────────────────────────────────────────────────────

_POOL_COLOR  = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}
_ENERGY_COLOR = {
    "hydro_mw":      "#2980B9",
    "solar_mw":      "#F39C12",
    "wind_mw":       "#1ABC9C",
    "geothermal_mw": "#27AE60",
    "fossil_mw":     "#7F8C8D",
}
_ENERGY_LABEL = {
    "hydro_mw": "Hydro", "solar_mw": "Solar",
    "wind_mw": "Wind",   "geothermal_mw": "Geothermal", "fossil_mw": "Fossil",
}
_OWN_COLOR = {"public": "#0071BC", "mixed": "#F7A800", "private": "#27AE60"}
_SSA_REF_COLOR = "#E67E22"

# Axis style shared across figures
_AX = dict(gridcolor="#E8EDF2", linecolor="#D0D8E0", zeroline=False)


# ── Layout helpers ────────────────────────────────────────────────────────────

def _country_color(country: str) -> str:
    return _POOL_COLOR.get(config.COUNTRY_REGION.get(country, "SAPP"), "#0071BC")


def _filt(df, countries, yr_min, yr_max):
    return df[df["country"].isin(countries) & df["year"].between(yr_min, yr_max)]


def _base(**overrides) -> dict:
    """Common Plotly layout — no xaxis/yaxis to avoid keyword collisions."""
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F8FAFC",
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=11, color="#1A2332"),
        margin=dict(l=55, r=20, t=24, b=65),
        height=260,
        legend=dict(
            orientation="h", yanchor="top", y=-0.22,
            xanchor="center", x=0.5, font=dict(size=9),
        ),
    )
    layout.update(overrides)
    return layout


# ── Sprint 3-B helpers ────────────────────────────────────────────────────────

def _selected_pools(scope: dict) -> list[str]:
    """Return pool names explicitly selected as aggregates (e.g. ['SAPP', 'EAPP'])."""
    if not scope:
        return []
    return [s[4:] for s in scope.get("selected", []) if str(s).startswith("AGG_")]


def _pool_ctrys(pool: str) -> list[str]:
    return [c for c in config.ALL_COUNTRIES if config.COUNTRY_REGION[c] == pool]


def _pool_avg(df, col, pool, yr_min, yr_max, scale=1.0):
    """Per-year mean of col across a pool's countries."""
    filt = df[df["country"].isin(_pool_ctrys(pool)) & df["year"].between(yr_min, yr_max)]
    if filt.empty:
        return None
    agg = filt.groupby("year")[col].mean().reset_index()
    agg[col] = agg[col] * scale
    return agg


def _pool_latest_avg(df, col, pool, yr_min, yr_max, scale=1.0):
    """Average of col for a pool at the latest year in range."""
    filt = df[df["country"].isin(_pool_ctrys(pool)) & df["year"].between(yr_min, yr_max)]
    if filt.empty:
        return None
    latest = filt[filt["year"] == filt["year"].max()]
    return round(float(latest[col].mean()) * scale, 2)


def _pool_latest_sum(df, col, pool, yr_min, yr_max):
    """Sum of col for a pool at the latest year in range."""
    filt = df[df["country"].isin(_pool_ctrys(pool)) & df["year"].between(yr_min, yr_max)]
    if filt.empty:
        return None
    latest = filt[filt["year"] == filt["year"].max()]
    return int(latest[col].sum())


def _tag_country_traces(fig):
    """Post-process: add customdata=[country_name] to per-country traces for click navigation."""
    for trace in fig.data:
        if trace.name in config.ALL_COUNTRIES and trace.x is not None and len(trace.x) > 0:
            trace.update(customdata=[trace.name] * len(trace.x))


def _add_ssa_ref(fig, df, col, yr_min, yr_max, scale=1.0, unit="", decimals=1):
    """Add SSA-13 average dotted reference line to a trend figure."""
    filt = df[df["country"].isin(config.ALL_COUNTRIES) & df["year"].between(yr_min, yr_max)]
    if filt.empty:
        return
    val = float(filt[col].mean()) * scale
    fig.add_hline(
        y=round(val, decimals),
        line_dash="dot",
        line_color=_SSA_REF_COLOR,
        line_width=1.5,
        annotation=dict(
            text=f"SSA avg: {val:.{decimals}f}{unit}",
            font=dict(size=9, color=_SSA_REF_COLOR),
            bgcolor="rgba(255,255,255,0.82)",
            xanchor="right",
            x=1.0,
            yanchor="bottom",
        ),
    )


# ── Access ────────────────────────────────────────────────────────────────────

def _access_charts(countries, yr_min, yr_max, scope=None):
    df    = load_access()
    pools = _selected_pools(scope)

    # ── A: National access rate trend ─────────────────────────────────────
    fig_a = go.Figure()

    if pools:
        for pool in pools:
            agg = _pool_avg(df, "access_national_pct", pool, yr_min, yr_max)
            if agg is None:
                continue
            agg_r = agg["access_national_pct"].round(1)
            fig_a.add_trace(go.Scatter(
                x=agg["year"], y=agg_r, mode="lines+markers",
                name=f"{pool} Pool",
                line=dict(color=_POOL_COLOR[pool], width=2.5),
                marker=dict(size=6, symbol="diamond"),
                hovertemplate=f"<b>{pool} Pool</b><br>Year: %{{x}}<br>Avg Access: %{{y:.1f}}%<extra></extra>",
            ))
    else:
        filt = _filt(df, countries, yr_min, yr_max)
        for country in countries:
            cdf = filt[filt["country"] == country].sort_values("year")
            if cdf.empty:
                continue
            fig_a.add_trace(go.Scatter(
                x=cdf["year"], y=cdf["access_national_pct"].round(1),
                mode="lines+markers", name=country,
                line=dict(color=_country_color(country), width=2),
                marker=dict(size=5),
                hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Access: %{y:.1f}%<extra></extra>",
            ))

    _add_ssa_ref(fig_a, df, "access_national_pct", yr_min, yr_max, unit="%")
    fig_a.update_layout(
        **_base(), xaxis=dict(**_AX, tickformat="d"),
        yaxis=dict(**_AX, range=[0, 105], title="Access Rate (%)"),
    )

    # ── B: Urban vs Rural (period average) ────────────────────────────────
    if pools:
        labels  = [f"{p} Pool" for p in pools]
        urban_v = [_pool_latest_avg(df, "access_urban_pct", p, yr_min, yr_max) or 0 for p in pools]
        rural_v = [_pool_latest_avg(df, "access_rural_pct", p, yr_min, yr_max) or 0 for p in pools]
        fig_b = go.Figure([
            go.Bar(name="Urban", x=labels, y=urban_v, marker_color="#0071BC",
                   hovertemplate="<b>%{x}</b><br>Urban avg: %{y:.1f}%<extra></extra>"),
            go.Bar(name="Rural", x=labels, y=rural_v, marker_color="#009FDA",
                   hovertemplate="<b>%{x}</b><br>Rural avg: %{y:.1f}%<extra></extra>"),
        ])
    else:
        avg = _filt(df, countries, yr_min, yr_max).groupby("country")[
            ["access_urban_pct", "access_rural_pct"]
        ].mean().reset_index()
        fig_b = go.Figure([
            go.Bar(name="Urban", x=avg["country"],
                   y=avg["access_urban_pct"].round(1), marker_color="#0071BC",
                   hovertemplate="<b>%{x}</b><br>Urban: %{y:.1f}%<extra></extra>"),
            go.Bar(name="Rural", x=avg["country"],
                   y=avg["access_rural_pct"].round(1), marker_color="#009FDA",
                   hovertemplate="<b>%{x}</b><br>Rural: %{y:.1f}%<extra></extra>"),
        ])

    fig_b.update_layout(
        **_base(), barmode="group",
        xaxis=dict(**_AX, tickangle=-35),
        yaxis=dict(**_AX, range=[0, 110], title="Access Rate (%)"),
    )

    _tag_country_traces(fig_a)
    return {"chart-access-a": fig_a, "chart-access-b": fig_b}


# ── Economics ─────────────────────────────────────────────────────────────────

def _economics_charts(countries, yr_min, yr_max, scope=None):
    df    = load_tariffs()
    pools = _selected_pools(scope)

    # ── A: Residential tariff trend ────────────────────────────────────────
    fig_a = go.Figure()

    if pools:
        for pool in pools:
            agg = _pool_avg(df, "residential_usd_kwh", pool, yr_min, yr_max, scale=100)
            if agg is None:
                continue
            fig_a.add_trace(go.Scatter(
                x=agg["year"], y=agg["residential_usd_kwh"].round(2),
                mode="lines+markers", name=f"{pool} Pool",
                line=dict(color=_POOL_COLOR[pool], width=2.5),
                marker=dict(size=6, symbol="diamond"),
                hovertemplate=f"<b>{pool} Pool</b><br>Year: %{{x}}<br>Avg Tariff: %{{y:.2f}} ¢/kWh<extra></extra>",
            ))
    else:
        filt = _filt(df, countries, yr_min, yr_max)
        for country in countries:
            cdf = filt[filt["country"] == country].sort_values("year")
            if cdf.empty:
                continue
            fig_a.add_trace(go.Scatter(
                x=cdf["year"], y=(cdf["residential_usd_kwh"] * 100).round(2),
                mode="lines+markers", name=country,
                line=dict(color=_country_color(country), width=2),
                marker=dict(size=5),
                hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Tariff: %{y:.2f} ¢/kWh<extra></extra>",
            ))

    _add_ssa_ref(fig_a, df, "residential_usd_kwh", yr_min, yr_max, scale=100, unit=" ¢/kWh", decimals=2)
    fig_a.update_layout(
        **_base(), xaxis=dict(**_AX, tickformat="d"),
        yaxis=dict(**_AX, title="Tariff (¢/kWh)"),
    )

    # ── B: Cost recovery horizontal bar ────────────────────────────────────
    if pools:
        labels = [f"{p} Pool" for p in pools]
        vals   = [_pool_latest_avg(df, "cost_recovery_pct", p, yr_min, yr_max) or 0 for p in pools]
        colors = [_POOL_COLOR[p] for p in pools]
        fig_b = go.Figure(go.Bar(
            x=vals, y=labels, orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}%" for v in vals], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Cost Recovery: %{x:.1f}%<extra></extra>",
        ))
    else:
        avg = (_filt(df, countries, yr_min, yr_max)
               .groupby("country")["cost_recovery_pct"].mean().reset_index()
               .sort_values("cost_recovery_pct"))
        fig_b = go.Figure(go.Bar(
            x=avg["cost_recovery_pct"].round(1), y=avg["country"], orientation="h",
            marker_color=[_country_color(c) for c in avg["country"]],
            text=avg["cost_recovery_pct"].round(1).astype(str) + "%",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Cost Recovery: %{x:.1f}%<extra></extra>",
        ))

    fig_b.update_layout(
        **_base(margin=dict(l=90, r=65, t=24, b=30), showlegend=False,
                legend=dict(orientation="h", y=-0.10, x=0.5, xanchor="center")),
        xaxis=dict(**_AX, range=[0, 135], title="Cost Recovery Rate (%)"),
        yaxis=dict(**_AX),
    )

    _tag_country_traces(fig_a)
    return {"chart-economics-a": fig_a, "chart-economics-b": fig_b}


# ── Transition ────────────────────────────────────────────────────────────────

def _transition_charts(countries, yr_min, yr_max, scope=None):
    df    = load_transition()
    pools = _selected_pools(scope)

    # ── A: Renewable share trend ───────────────────────────────────────────
    many  = (not pools) and len(countries) > 4
    fig_a = go.Figure()

    if pools:
        for pool in pools:
            agg = _pool_avg(df, "renewable_share_pct", pool, yr_min, yr_max)
            if agg is None:
                continue
            fig_a.add_trace(go.Scatter(
                x=agg["year"], y=agg["renewable_share_pct"].round(1),
                mode="lines+markers", name=f"{pool} Pool",
                line=dict(color=_POOL_COLOR[pool], width=2.5),
                marker=dict(size=6, symbol="diamond"),
                hovertemplate=f"<b>{pool} Pool</b><br>Year: %{{x}}<br>Avg Renewable: %{{y:.1f}}%<extra></extra>",
            ))
    else:
        filt = _filt(df, countries, yr_min, yr_max)
        for country in countries:
            cdf = filt[filt["country"] == country].sort_values("year")
            if cdf.empty:
                continue
            color = _country_color(country)
            fig_a.add_trace(go.Scatter(
                x=cdf["year"], y=cdf["renewable_share_pct"].round(1),
                mode="lines+markers", name=country,
                line=dict(color=color, width=2),
                marker=dict(size=4),
                fill=None if many else "tozeroy",
                opacity=0.75,
                hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Renewable Share: %{y:.1f}%<extra></extra>",
            ))

    _add_ssa_ref(fig_a, df, "renewable_share_pct", yr_min, yr_max, unit="%")
    fig_a.update_layout(
        **_base(), xaxis=dict(**_AX, tickformat="d"),
        yaxis=dict(**_AX, range=[0, 110], title="Renewable Share (%)"),
    )

    # ── B: Capacity mix stacked bar ────────────────────────────────────────
    energy_cols = ["hydro_mw", "solar_mw", "wind_mw", "geothermal_mw", "fossil_mw"]

    if pools:
        labels_b = [f"{p} Pool" for p in pools]
        fig_b = go.Figure()
        for col in energy_cols:
            sums = [_pool_latest_sum(df, col, p, yr_min, yr_max) or 0 for p in pools]
            fig_b.add_trace(go.Bar(
                name=_ENERGY_LABEL[col], x=labels_b, y=sums,
                marker_color=_ENERGY_COLOR[col],
                hovertemplate=f"<b>%{{x}}</b><br>{_ENERGY_LABEL[col]}: %{{y:,}} MW<extra></extra>",
            ))
    else:
        latest_yr = int(_filt(df, countries, yr_min, yr_max)["year"].max())
        latest    = _filt(df, countries, yr_min, yr_max)
        latest    = latest[latest["year"] == latest_yr].set_index("country")
        fig_b = go.Figure()
        for col in energy_cols:
            vals = [float(latest.loc[c, col]) if c in latest.index else 0.0 for c in countries]
            fig_b.add_trace(go.Bar(
                name=_ENERGY_LABEL[col], x=countries, y=[round(v) for v in vals],
                marker_color=_ENERGY_COLOR[col],
                hovertemplate=f"<b>%{{x}}</b><br>{_ENERGY_LABEL[col]}: %{{y:,.0f}} MW ({latest_yr})<extra></extra>",
            ))

    fig_b.update_layout(
        **_base(), barmode="stack",
        xaxis=dict(**_AX, tickangle=-35),
        yaxis=dict(**_AX, title="Capacity (MW)"),
    )

    _tag_country_traces(fig_a)
    return {"chart-transition-a": fig_a, "chart-transition-b": fig_b}


# ── Institutions ──────────────────────────────────────────────────────────────

def _institutions_charts(countries, yr_min, yr_max):
    df  = load_institutions()
    sub = df[df["country"].isin(countries)].copy()
    if sub.empty:
        return {}

    # A: Utility ownership structure — donut
    counts = sub["utility_ownership"].value_counts().reset_index()
    counts.columns = ["ownership", "count"]
    fig_a = go.Figure(go.Pie(
        labels=counts["ownership"].str.capitalize(),
        values=counts["count"],
        hole=0.45,
        marker_colors=[_OWN_COLOR.get(o, "#8A9BAC") for o in counts["ownership"]],
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value} countries (%{percent})<extra></extra>",
    ))
    fig_a.update_layout(
        **_base(margin=dict(l=20, r=20, t=24, b=20), showlegend=True,
                legend=dict(orientation="h", y=-0.08, x=0.5,
                            xanchor="center", font=dict(size=10))),
    )

    # B: Regulatory environment — heatmap
    _tariff_score = {"cost-reflective": 1.0, "hybrid": 0.5, "political": 0.0}
    sub = sub.set_index("country")
    sub["tariff_score"] = sub["tariff_mechanism"].map(_tariff_score).fillna(0.5)

    col_defs = [
        ("regulator_exists", "Regulator"),
        ("unbundled",        "Unbundled"),
        ("tariff_score",     "Tariff Mechanism"),
    ]
    present = [c for c in countries if c in sub.index]
    z, text = [], []
    for country in present:
        row = sub.loc[country]
        z_row, t_row = [], []
        for col, _ in col_defs:
            val = row[col]
            if col in ("regulator_exists", "unbundled"):
                z_row.append(1.0 if val else 0.0)
                t_row.append("Yes" if val else "No")
            else:
                z_row.append(float(val))
                t_row.append(str(row["tariff_mechanism"]).capitalize())
        z.append(z_row)
        text.append(t_row)

    fig_b = go.Figure(go.Heatmap(
        z=z, x=[label for _, label in col_defs], y=present,
        text=text, texttemplate="%{text}",
        colorscale=[[0, "#C0392B"], [0.5, "#F7A800"], [1, "#27AE60"]],
        showscale=False, zmin=0, zmax=1,
        textfont=dict(size=10),
        hovertemplate="<b>%{y}</b> — %{x}: <b>%{text}</b><extra></extra>",
    ))
    fig_b.update_layout(
        **_base(margin=dict(l=90, r=20, t=24, b=30), showlegend=False),
        xaxis=dict(**_AX, side="top"),
        yaxis=dict(**_AX, autorange="reversed"),
    )

    return {"chart-institutions-a": fig_a, "chart-institutions-b": fig_b}


# ── Mini chart helpers (Overview 2×2 grid) ────────────────────────────────────

def _mini_base(**overrides) -> dict:
    """Compact Plotly layout for Overview page mini charts (height=155)."""
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F8FAFC",
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=10, color="#1A2332"),
        margin=dict(l=40, r=10, t=10, b=30),
        height=155,
        showlegend=False,
    )
    layout.update(overrides)
    return layout


def build_mini_charts(scope: dict, year_range: list) -> dict:
    """Return {mini_id: go.Figure} for the 2×2 Overview snapshot grid."""
    countries = resolve_countries(scope)
    if not countries or not year_range:
        return {}

    yr_min, yr_max = int(year_range[0]), int(year_range[1])
    display = countries[:6]
    results = {}

    # access: national rate trend
    df = _filt(load_access(), display, yr_min, yr_max)
    if not df.empty:
        fig = go.Figure()
        for c in display:
            cdf = df[df["country"] == c].sort_values("year")
            fig.add_trace(go.Scatter(
                x=cdf["year"], y=cdf["access_national_pct"].round(1),
                mode="lines", name=c, line=dict(color=_country_color(c), width=1.5),
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.1f}%<extra></extra>",
            ))
        fig.update_layout(**_mini_base(), xaxis=dict(**_AX, tickformat="d"),
                          yaxis=dict(**_AX, range=[0, 105]))
        results["mini-access"] = fig

    # economics: residential tariff ¢/kWh
    df = _filt(load_tariffs(), display, yr_min, yr_max)
    if not df.empty:
        fig = go.Figure()
        for c in display:
            cdf = df[df["country"] == c].sort_values("year")
            fig.add_trace(go.Scatter(
                x=cdf["year"], y=(cdf["residential_usd_kwh"] * 100).round(2),
                mode="lines", name=c, line=dict(color=_country_color(c), width=1.5),
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.2f} ¢/kWh<extra></extra>",
            ))
        fig.update_layout(**_mini_base(), xaxis=dict(**_AX, tickformat="d"),
                          yaxis=dict(**_AX))
        results["mini-economics"] = fig

    # transition: renewable share %
    df = _filt(load_transition(), display, yr_min, yr_max)
    if not df.empty:
        fig = go.Figure()
        for c in display:
            cdf = df[df["country"] == c].sort_values("year")
            fig.add_trace(go.Scatter(
                x=cdf["year"], y=cdf["renewable_share_pct"].round(1),
                mode="lines", name=c, line=dict(color=_country_color(c), width=1.5),
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.1f}%<extra></extra>",
            ))
        fig.update_layout(**_mini_base(), xaxis=dict(**_AX, tickformat="d"),
                          yaxis=dict(**_AX, range=[0, 110]))
        results["mini-transition"] = fig

    # institutions: ownership donut
    sub = load_institutions()[lambda d: d["country"].isin(countries)]
    if not sub.empty:
        counts = sub["utility_ownership"].value_counts().reset_index()
        counts.columns = ["ownership", "count"]
        fig = go.Figure(go.Pie(
            labels=counts["ownership"].str.capitalize(),
            values=counts["count"],
            hole=0.42,
            marker_colors=[_OWN_COLOR.get(o, "#8A9BAC") for o in counts["ownership"]],
            textinfo="label",
            textfont=dict(size=9),
        ))
        fig.update_layout(**_mini_base(margin=dict(l=10, r=10, t=10, b=10)))
        results["mini-institutions"] = fig

    return results


# ── Public entry points ───────────────────────────────────────────────────────

def build_charts(view: str, scope: dict, year_range: list) -> dict:
    """Return {chart_id: go.Figure} for the given view and filter state."""
    countries = resolve_countries(scope)
    if not countries or not year_range:
        return {}

    yr_min, yr_max = int(year_range[0]), int(year_range[1])

    dispatch = {
        "access":       lambda: _access_charts(countries,      yr_min, yr_max, scope),
        "economics":    lambda: _economics_charts(countries,   yr_min, yr_max, scope),
        "transition":   lambda: _transition_charts(countries,  yr_min, yr_max, scope),
        "institutions": lambda: _institutions_charts(countries, yr_min, yr_max),
    }
    return dispatch.get(view, lambda: {})()
