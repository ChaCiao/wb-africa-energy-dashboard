"""Map click → store the clicked country name."""
import time

from dash import Input, Output
from dash.exceptions import PreventUpdate

from components.africa_map import ISO3_TO_COUNTRY


def register_map_callbacks(app):

    @app.callback(
        Output("map-click", "data"),
        Input("africa-map", "clickData"),
        prevent_initial_call=True,
    )
    def handle_map_click(click_data):
        if not click_data:
            raise PreventUpdate
        iso3    = click_data["points"][0].get("location", "")
        country = ISO3_TO_COUNTRY.get(iso3)
        if not country:
            raise PreventUpdate
        return {"country": country, "ts": time.time()}
