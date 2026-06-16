"""
Interactive Africa choropleth map for the Overview page.
Shows all 13 SSA countries colored by electrification rate.
Hover → 4-axis summary. Click → country focus navigation.
"""
import pandas as pd
import plotly.graph_objects as go

from data.loaders import load_access, load_tariffs, load_transition, load_institutions

# ── ISO-3 mapping for our 13 countries ───────────────────────────────────────
COUNTRY_ISO3: dict[str, str] = {
    "Lesotho":    "LSO",
    "Namibia":    "NAM",
    "Botswana":   "BWA",
    "Zambia":     "ZMB",
    "Zimbabwe":   "ZWE",
    "Mozambique": "MOZ",
    "Malawi":     "MWI",
    "Ethiopia":   "ETH",
    "Kenya":      "KEN",
    "Tanzania":   "TZA",
    "Uganda":     "UGA",
    "DRC":        "COD",
    "Cameroon":   "CMR",
}
ISO3_TO_COUNTRY: dict[str, str] = {v: k for k, v in COUNTRY_ISO3.items()}


def _map_data() -> pd.DataFrame:
    """Compute latest-year per-country metrics for hover tooltips."""
    acc_df  = load_access()
    tar_df  = load_tariffs()
    ren_df  = load_transition()
    ins_df  = load_institutions()

    latest_yr = int(acc_df["year"].max())

    rows = []
    for country, iso3 in COUNTRY_ISO3.items():
        # Access rate
        a = acc_df[(acc_df["country"] == country) & (acc_df["year"] == latest_yr)]
        access = round(float(a["access_national_pct"].iloc[0]), 1) if not a.empty else 0.0

        # Residential tariff (¢/kWh)
        t = tar_df[(tar_df["country"] == country) & (tar_df["year"] == latest_yr)]
        tariff = round(float(t["residential_usd_kwh"].iloc[0]) * 100, 2) if not t.empty else 0.0

        # Renewable share
        r = ren_df[(ren_df["country"] == country) & (ren_df["year"] == latest_yr)]
        renew = round(float(r["renewable_share_pct"].iloc[0]), 1) if not r.empty else 0.0

        # Ownership
        i = ins_df[ins_df["country"] == country]
        ownership = i["utility_ownership"].iloc[0].capitalize() if not i.empty else "—"

        rows.append(dict(
            country=country, iso3=iso3,
            access=access, tariff=tariff, renew=renew, ownership=ownership,
        ))

    return pd.DataFrame(rows)


def build_africa_map() -> go.Figure:
    """
    Build a Plotly Choropleth map of Sub-Saharan Africa.
    All 13 dashboard countries are colored by national electrification rate.
    Other African countries appear in light grey.
    """
    df = _map_data()

    # customdata columns: [country, tariff, renew, ownership]
    custom = df[["country", "tariff", "renew", "ownership"]].values

    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        locations=df["iso3"],
        z=df["access"],
        locationmode="ISO-3",
        customdata=custom,
        colorscale=[
            [0.00, "#C6E0F5"],
            [0.40, "#5BA3D0"],
            [0.70, "#1A6FA8"],
            [1.00, "#003F72"],
        ],
        zmin=0,
        zmax=100,
        showscale=True,
        colorbar=dict(
            title=dict(text="Access (%)", font=dict(size=11, color="#1A2332")),
            thickness=12,
            len=0.55,
            x=1.01,
            tickfont=dict(size=10, color="#1A2332"),
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "⚡  Electrification rate: <b>%{z:.1f}%</b><br>"
            "💲  Residential tariff: <b>%{customdata[1]:.2f} ¢/kWh</b><br>"
            "🌿  Renewable share: <b>%{customdata[2]:.1f}%</b><br>"
            "🏛  Utility ownership: <b>%{customdata[3]}</b><br>"
            "<span style='color:#8A9BAC;font-size:11px'>Click to open country focus</span>"
            "<extra></extra>"
        ),
        marker_line_color="white",
        marker_line_width=0.8,
    ))

    fig.update_layout(
        geo=dict(
            scope="africa",
            showframe=False,
            showcoastlines=False,
            showlakes=False,
            showocean=True,
            oceancolor="#EBF4FA",
            landcolor="#D8E3EC",   # grey for non-data Africa countries
            bgcolor="rgba(0,0,0,0)",
            projection_type="mercator",
            lataxis_range=[-36, 24],
            lonaxis_range=[-20, 52],
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=60, t=0, b=0),
        height=400,
        font=dict(family="Segoe UI, Inter, Arial, sans-serif", size=11, color="#1A2332"),
    )

    return fig
