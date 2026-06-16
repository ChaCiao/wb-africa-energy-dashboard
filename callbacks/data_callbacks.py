"""Download-CSV callback for the DataTable."""
import pandas as pd
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from data.table_builder import build_table


def register_data_callbacks(app):

    @app.callback(
        Output("download-csv", "data"),
        Input("download-btn", "n_clicks"),
        State("current-view", "data"),
        State("selected-scope", "data"),
        State("year-slider", "value"),
        prevent_initial_call=True,
    )
    def download_csv(n_clicks, view, scope, year_range):
        if not n_clicks:
            raise PreventUpdate

        _, records = build_table(view or "access", scope, year_range)
        if not records:
            raise PreventUpdate

        df = pd.DataFrame(records)
        yr_min = int(year_range[0]) if year_range else 2015
        yr_max = int(year_range[1]) if year_range else 2024
        filename = f"wb_africa_{view or 'data'}_{yr_min}-{yr_max}.csv"

        return dict(content=df.to_csv(index=False), filename=filename, type="text/csv")
