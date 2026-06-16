"""Sprint 4-A: Ranked country table component."""
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc
import config

_POOL_COLOR = {"SAPP": "#0071BC", "EAPP": "#27AE60", "CAPP": "#E67E22"}
_MEDAL      = {1: "🥇", 2: "🥈", 3: "🥉"}
_RANK_COLOR = {1: "#F7A800", 2: "#6C757D", 3: "#8B5A2B"}
_BOTTOM_CLR = "#C0392B"


def _rank_badge(rank: int) -> html.Td:
    medal = _MEDAL.get(rank, "")
    color = _RANK_COLOR.get(rank, ("#C0392B" if rank > 10 else "#5A6A7A"))
    text  = f"{medal} #{rank}" if medal else f"#{rank}"
    return html.Td(text, style={"color": color, "fontWeight": "700",
                                "textAlign": "center", "whiteSpace": "nowrap"})


def make_rankings_table(df: pd.DataFrame, view: str) -> html.Div:
    """Render a rankings table card from a rankings DataFrame."""
    if df.empty:
        return html.Div()

    label = df["metric_label"].iloc[0]

    rows = []
    for _, r in df.iterrows():
        rank = int(r["rank"])
        sel  = bool(r["selected"])
        region_color = _POOL_COLOR.get(r["region"], "#8A9BAC")

        row_style = {"backgroundColor": "#EBF4FB"} if sel else {}
        if sel:
            row_style["fontWeight"] = "600"

        rows.append(html.Tr([
            _rank_badge(rank),
            html.Td([
                html.Span(r["country"]),
                (html.Span(" ★", style={"color": "#0071BC", "fontSize": "0.7rem"}) if sel else html.Span()),
            ]),
            html.Td(r["region"],
                    style={"color": region_color, "fontSize": "0.75rem", "fontWeight": "600"}),
            html.Td(str(r["value"]),
                    style={"textAlign": "right", "fontFamily": "monospace", "fontWeight": "600"}),
        ], style=row_style))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Rank",    style={"width": "64px", "textAlign": "center"}),
            html.Th("Country", style={"width": "120px"}),
            html.Th("Pool",    style={"width": "60px"}),
            html.Th(label,     style={"textAlign": "right"}),
        ]), className="ranking-thead"),
        html.Tbody(rows),
    ], className="ranking-table")

    return dbc.Card(
        dbc.CardBody([
            html.H6(f"Country Rankings — {label}", className="chart-title"),
            table,
            html.P("★ = currently selected  |  All 13 SSA countries",
                   className="table-note mt-2"),
        ]),
        className="rankings-card mt-3",
    )
