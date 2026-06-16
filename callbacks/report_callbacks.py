"""
Sprint 4-C: Export Report (HTML) + URL state sync.
"""
from datetime import datetime
import pandas as pd
from dash import Input, Output, State, clientside_callback
from dash.exceptions import PreventUpdate

import config
from data.kpi_compute import compute_kpis, resolve_countries
from data.table_builder import build_table


# ── HTML report template ──────────────────────────────────────────────────────

_HTML_STYLE = """
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1A2332;
       max-width: 960px; margin: 40px auto; padding: 0 24px; }
h1   { color: #003F72; border-bottom: 3px solid #0071BC; padding-bottom: 8px; }
h2   { color: #004F8B; margin-top: 32px; font-size: 1.1rem; }
.meta { color: #5A6A7A; font-size: 0.85rem; margin-bottom: 24px; }
.badge { background:#E67E22; color:#fff; border-radius:4px;
         padding: 2px 8px; font-size: 0.75rem; font-weight: 700; }
table { width: 100%; border-collapse: collapse; margin-top: 12px;
        font-size: 0.88rem; }
th { background: #0071BC; color: #fff; padding: 9px 12px; text-align: left; }
td { padding: 8px 12px; border-bottom: 1px solid #D0D8E0; }
tr:nth-child(even) td { background: #F5F7FA; }
.footer { color: #8A9BAC; font-size: 0.78rem; margin-top: 40px;
          border-top: 1px solid #D0D8E0; padding-top: 12px; }
"""


def _kpi_table_html(view: str, scope: dict, year_range: list) -> str:
    values    = compute_kpis(view, scope, year_range)
    kpi_defs  = config.VIEW_KPIS.get(view, config.VIEW_KPIS["home"])
    rows_html = ""
    for k in kpi_defs:
        val = values.get(k["id"], "—")
        rows_html += f"<tr><td>{k['label']}</td><td><strong>{val}</strong></td><td>{k['unit']}</td></tr>"
    return f"<table><thead><tr><th>Indicator</th><th>Value</th><th>Unit</th></tr></thead><tbody>{rows_html}</tbody></table>"


def _data_table_html(view: str, scope: dict, year_range: list) -> str:
    cols, rows = build_table(view, scope, year_range)
    if not cols or not rows:
        return "<p>No data available for selected filters.</p>"
    df = pd.DataFrame(rows)[[c["id"] for c in cols]]
    return df.to_html(index=False, classes="", border=0)


def _build_report(view: str, scope: dict, year_range: list) -> str:
    countries  = resolve_countries(scope) if scope else []
    yr_str     = f"{int(year_range[0])}–{int(year_range[1])}" if year_range else "—"
    now        = datetime.now().strftime("%B %d, %Y %H:%M")
    view_label = view.capitalize() if view else "Overview"

    kpi_html  = _kpi_table_html(view, scope, year_range)
    data_html = _data_table_html(view, scope, year_range) if view != "home" else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Africa Energy Dashboard — {view_label} Report</title>
<style>{_HTML_STYLE}</style>
</head>
<body>
<h1>Africa Energy Dashboard</h1>
<p class="meta">
  <span class="badge">MOCK DATA</span>&nbsp;&nbsp;
  <strong>View:</strong> {view_label}&nbsp;|&nbsp;
  <strong>Countries:</strong> {', '.join(countries) if countries else '—'}&nbsp;|&nbsp;
  <strong>Years:</strong> {yr_str}&nbsp;|&nbsp;
  <strong>Generated:</strong> {now}
</p>

<h2>Key Performance Indicators</h2>
{kpi_html}

{"<h2>Data Table</h2>" + data_html if data_html else ""}

<div class="footer">
  Africa Energy Dashboard &nbsp;·&nbsp; Mock data only — not for citation &nbsp;·&nbsp;
  Powered by World Bank Open Data (mock)
</div>
</body>
</html>"""


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_report_callbacks(app):

    # ── Export Report (HTML download) ─────────────────────────────────────
    @app.callback(
        Output("download-report", "data"),
        Input("export-report-btn", "n_clicks"),
        State("current-view",   "data"),
        State("selected-scope", "data"),
        State("year-slider",    "value"),
        prevent_initial_call=True,
    )
    def export_report(n_clicks, view, scope, year_range):
        if not n_clicks:
            raise PreventUpdate
        html_str  = _build_report(view or "home", scope, year_range)
        yr_str    = f"{int(year_range[0])}-{int(year_range[1])}" if year_range else "2015-2024"
        filename  = f"africa_energy_{view or 'overview'}_{yr_str}.html"
        return dict(content=html_str, filename=filename, type="text/html")

    # ── Write current view + tier to URL (one-directional, no restore) ───
    clientside_callback(
        """
        function(view, scope) {
            if (!view) return window.location.search;
            var params = new URLSearchParams();
            params.set('view', view);
            if (scope && scope.tier) params.set('tier', scope.tier);
            var search = '?' + params.toString();
            if (window.history && window.history.replaceState) {
                window.history.replaceState(null, '', search);
            }
            return search;
        }
        """,
        Output("url", "search"),
        Input("current-view",   "data"),
        Input("selected-scope", "data"),
    )
