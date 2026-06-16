"""
Plotly figure builders for each dashboard dimension.
build_charts(view, scope, year_range) → {chart_id: go.Figure}
"""
import plotly.graph_objects as go

import config
from data.loaders import load_access, load_tariffs, load_transition, load_institutions
from data.kpi_compute import resolve_countries

# ── Design constants ──────────────────────────────────────────────────────────

_POOL_COLOR = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}

_ENERGY_COLOR = {
    "hydro_mw":      "#2980B9",
    "solar_mw":      "#F39C12",
    "wind_mw":       "#1ABC9C",
    "geothermal_mw": "#27AE60",
    "fossil_mw":     "#7F8C8D",
}
_ENERGY_LABEL = {
    "hydro_mw":      "Hydro",
    "solar_mw":      "Solar",
    "wind_mw":       "Wind",
    "geothermal_mw": "Geothermal",
    "fossil_mw":     "Fossil",
}
_OWN_COLOR = {"public": "#0071BC", "mixed": "#F7A800", "private": "#27AE60"}

# Standard axis style (no zeroline, light grid)
_AX = dict(gridcolor="#E8EDF2", linecolor="#D0D8E0", zeroline=False)


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


# ── Access ────────────────────────────────────────────────────────────────────

def _access_charts(countries, yr_min, yr_max):
    df = _filt(load_access(), countries, yr_min, yr_max)
    if df.empty:
        return {}

    # A: National access rate trend — line per country
    fig_a = go.Figure()
    for country in countries:
        cdf = df[df["country"] == country].sort_values("year")
        fig_a.add_trace(go.Scatter(
            x=cdf["year"], y=cdf["access_national_pct"].round(1),
            mode="lines+markers", name=country,
            line=dict(color=_country_color(country), width=2),
            marker=dict(size=5),
            hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Access: %{y:.1f}%<extra></extra>",
        ))
    fig_a.update_layout(
        **_base(),
        xaxis=dict(**_AX, tickformat="d"),
        yaxis=dict(**_AX, range=[0, 105], title="Access Rate (%)"),
    )

    # B: Urban vs Rural — grouped bar (period average)
    avg = df.groupby("country")[["access_urban_pct", "access_rural_pct"]].mean().reset_index()
    fig_b = go.Figure([
        go.Bar(name="Urban", x=avg["country"],
               y=avg["access_urban_pct"].round(1), marker_color="#0071BC",
               hovertemplate="<b>%{x}</b><br>Urban: %{y:.1f}%<extra></extra>"),
        go.Bar(name="Rural", x=avg["country"],
               y=avg["access_rural_pct"].round(1), marker_color="#009FDA",
               hovertemplate="<b>%{x}</b><br>Rural: %{y:.1f}%<extra></extra>"),
    ])
    fig_b.update_layout(
        **_base(),
        barmode="group",
        xaxis=dict(**_AX, tickangle=-35),
        yaxis=dict(**_AX, range=[0, 110], title="Access Rate (%)"),
    )

    return {"chart-access-a": fig_a, "chart-access-b": fig_b}


# ── Economics ─────────────────────────────────────────────────────────────────

def _economics_charts(countries, yr_min, yr_max):
    df = _filt(load_tariffs(), countries, yr_min, yr_max)
    if df.empty:
        return {}

    # A: Residential tariff trend — line per country
    fig_a = go.Figure()
    for country in countries:
        cdf = df[df["country"] == country].sort_values("year")
        fig_a.add_trace(go.Scatter(
            x=cdf["year"], y=(cdf["residential_usd_kwh"] * 100).round(2),
            mode="lines+markers", name=country,
            line=dict(color=_country_color(country), width=2),
            marker=dict(size=5),
            hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Tariff: %{y:.2f} ¢/kWh<extra></extra>",
        ))
    fig_a.update_layout(
        **_base(),
        xaxis=dict(**_AX, tickformat="d"),
        yaxis=dict(**_AX, title="Tariff (¢/kWh)"),
    )

    # B: Cost recovery — horizontal bar, sorted ascending
    avg = (df.groupby("country")["cost_recovery_pct"]
             .mean().reset_index()
             .sort_values("cost_recovery_pct"))
    fig_b = go.Figure(go.Bar(
        x=avg["cost_recovery_pct"].round(1),
        y=avg["country"],
        orientation="h",
        marker_color=[_country_color(c) for c in avg["country"]],
        text=avg["cost_recovery_pct"].round(1).astype(str) + "%",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Cost Recovery: %{x:.1f}%<extra></extra>",
    ))
    fig_b.update_layout(
        **_base(margin=dict(l=90, r=65, t=24, b=30),
                showlegend=False,
                legend=dict(orientation="h", y=-0.10, x=0.5, xanchor="center")),
        xaxis=dict(**_AX, range=[0, 135], title="Cost Recovery Rate (%)"),
        yaxis=dict(**_AX),
    )

    return {"chart-economics-a": fig_a, "chart-economics-b": fig_b}


# ── Transition ────────────────────────────────────────────────────────────────

def _transition_charts(countries, yr_min, yr_max):
    df = _filt(load_transition(), countries, yr_min, yr_max)
    if df.empty:
        return {}

    # A: Renewable share trend — area fill when few countries, line when many
    many = len(countries) > 4
    fig_a = go.Figure()
    for country in countries:
        cdf = df[df["country"] == country].sort_values("year")
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
    fig_a.update_layout(
        **_base(),
        xaxis=dict(**_AX, tickformat="d"),
        yaxis=dict(**_AX, range=[0, 110], title="Renewable Share (%)"),
    )

    # B: Capacity mix — stacked bar, latest year
    latest_yr = int(df["year"].max())
    latest = df[df["year"] == latest_yr].set_index("country")
    energy_cols = ["hydro_mw", "solar_mw", "wind_mw", "geothermal_mw", "fossil_mw"]
    fig_b = go.Figure()
    for col in energy_cols:
        vals = [float(latest.loc[c, col]) if c in latest.index else 0.0 for c in countries]
        fig_b.add_trace(go.Bar(
            name=_ENERGY_LABEL[col], x=countries,
            y=[round(v) for v in vals],
            marker_color=_ENERGY_COLOR[col],
            hovertemplate=f"<b>%{{x}}</b><br>{_ENERGY_LABEL[col]}: %{{y:,.0f}} MW ({latest_yr})<extra></extra>",
        ))
    fig_b.update_layout(
        **_base(),
        barmode="stack",
        xaxis=dict(**_AX, tickangle=-35),
        yaxis=dict(**_AX, title=f"Capacity (MW) — {latest_yr}"),
    )

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
    ))
    fig_a.update_layout(
        **_base(margin=dict(l=20, r=20, t=24, b=20),
                showlegend=True,
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
    display = countries[:6]  # cap to 6 for legibility
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
            ))
        fig.update_layout(**_mini_base(), xaxis=dict(**_AX), yaxis=dict(**_AX, range=[0, 105]))
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
            ))
        fig.update_layout(**_mini_base(), xaxis=dict(**_AX), yaxis=dict(**_AX))
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
            ))
        fig.update_layout(**_mini_base(), xaxis=dict(**_AX), yaxis=dict(**_AX, range=[0, 110]))
        results["mini-transition"] = fig

    # institutions: ownership donut (no year filter — one row per country)
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


# ── Public entry point ────────────────────────────────────────────────────────

def build_charts(view: str, scope: dict, year_range: list) -> dict:
    """Return {chart_id: go.Figure} for the given view and filter state."""
    countries = resolve_countries(scope)
    if not countries or not year_range:
        return {}

    yr_min, yr_max = int(year_range[0]), int(year_range[1])

    dispatch = {
        "access":       lambda: _access_charts(countries, yr_min, yr_max),
        "economics":    lambda: _economics_charts(countries, yr_min, yr_max),
        "transition":   lambda: _transition_charts(countries, yr_min, yr_max),
        "institutions": lambda: _institutions_charts(countries, yr_min, yr_max),
    }
    return dispatch.get(view, lambda: {})()
