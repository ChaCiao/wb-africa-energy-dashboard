from dash import html

_TABS = [
    ("access",       "Access"),
    ("economics",    "Economics"),
    ("transition",   "Transition"),
    ("institutions", "Institutions"),
]

layout = html.Div(
    [
        html.Button(
            label,
            id=f"tab-{view}",
            className="dim-tab",
            n_clicks=0,
        )
        for view, label in _TABS
    ],
    className="dim-tabs-bar",
)
