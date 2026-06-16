"""Sprint 6-B: Urban–Rural electricity access gap chart."""
import plotly.graph_objects as go
import config
from data.loaders import load_access
from data.kpi_compute import resolve_countries

_POOL_COLOR = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}
_AX = dict(gridcolor="#E8EDF2", linecolor="#D0D8E0", zeroline=True,
           zerolinecolor="#C0392B", zerolinewidth=1)


def build_gap_chart(scope, year_range):
    """
    Horizontal bar: urban−rural access gap per country, sorted by gap.
    Selected countries shown in pool color; others greyed out.
    """
    acc      = load_access()
    yr_max   = int(year_range[1]) if year_range else config.YEAR_MAX
    selected = resolve_countries(scope) if scope else []

    filt = acc[acc["country"].isin(config.ALL_COUNTRIES) & (acc["year"] == yr_max)].copy()
    if filt.empty:
        return None

    filt["gap"] = (filt["access_urban_pct"] - filt["access_rural_pct"]).round(1)
    filt = filt.sort_values("gap", ascending=True)   # ascending so largest gap is at top

    def _color(c):
        base = _POOL_COLOR.get(config.COUNTRY_REGION.get(c, "SAPP"), "#0071BC")
        return base if (not selected or c in selected) else "#D0D8E0"

    colors = [_color(c) for c in filt["country"]]

    fig = go.Figure(go.Bar(
        x=filt["gap"],
        y=filt["country"],
        orientation="h",
        marker_color=colors,
        customdata=filt["country"].tolist(),
        hovertemplate="<b>%{customdata}</b><br>Urban–Rural Gap: %{x:.1f} pp<extra></extra>",
    ))

    fig.add_vline(
        x=10, line_dash="dot", line_color="#E67E22", line_width=1.5,
        annotation=dict(text="10 pp", font=dict(size=8, color="#E67E22"),
                        bgcolor="rgba(255,255,255,0.8)", yanchor="bottom"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F8FAFC",
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=10, color="#1A2332"),
        margin=dict(l=90, r=30, t=10, b=36),
        height=320,
        showlegend=False,
        xaxis=dict(**_AX, title="Gap (pp, Urban − Rural)"),
        yaxis=dict(gridcolor="#E8EDF2", linecolor="#D0D8E0"),
    )
    return fig
