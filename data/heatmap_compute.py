"""Sprint 6-B: Country × Year heatmap for primary dimension metric."""
import plotly.graph_objects as go
import config
from data.loaders import load_access, load_tariffs, load_transition

_CFG = {
    "access":     (load_access,     "access_national_pct",  "Access Rate (%)",    "YlGn"),
    "economics":  (load_tariffs,    "cost_recovery_pct",    "Cost Recovery (%)",  "RdYlGn"),
    "transition": (load_transition, "renewable_share_pct",  "Renewable Share (%)", "Teal"),
}


def build_heatmap(view: str, year_range: list):
    """
    Country × Year heatmap for the primary metric of a dimension.
    Countries sorted by descending average. Returns go.Figure or None.
    """
    cfg = _CFG.get(view)
    if cfg is None:
        return None

    loader, col, col_label, colorscale = cfg
    df = loader()

    yr_min = int(year_range[0]) if year_range else config.YEAR_MIN
    yr_max = int(year_range[1]) if year_range else config.YEAR_MAX
    years  = list(range(yr_min, yr_max + 1))

    filt = df[df["country"].isin(config.ALL_COUNTRIES) & df["year"].between(yr_min, yr_max)]
    if filt.empty:
        return None

    pivot = (filt.pivot(index="country", columns="year", values=col)
                 .reindex(columns=years))
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    fig = go.Figure(go.Heatmap(
        x=years,
        y=list(pivot.index),
        z=pivot.values.round(1).tolist(),
        colorscale=colorscale,
        colorbar=dict(title=dict(text=col_label, side="right"),
                      thickness=13, len=0.85),
        hovertemplate="<b>%{y}</b><br>Year %{x}: %{z:.1f}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F8FAFC",
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=10, color="#1A2332"),
        margin=dict(l=90, r=20, t=10, b=36),
        height=320,
        xaxis=dict(tickformat="d", tickvals=years, gridcolor="#E8EDF2", tickangle=-35),
        yaxis=dict(gridcolor="#E8EDF2"),
    )
    return fig
