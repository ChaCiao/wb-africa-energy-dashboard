# 03 – Data Schema

> Sections A–D define CSV columns in `data/`.  
> Section G defines design tokens applied in `assets/theme.css`.

---

## A – access.csv

| Column | Type | Description |
|---|---|---|
| country | str | Country name |
| year | int | 2015–2024 |
| region | str | SAPP / EAPP / CAPP |
| access_national_pct | float | National electrification rate (%) |
| access_urban_pct | float | Urban electrification rate (%) |
| access_rural_pct | float | Rural electrification rate (%) |
| pop_without_electricity_millions | float | Population without electricity (millions) |
| new_connections_thousands | float | New connections per year (thousands) |
| investment_usd_millions | float | Energy sector investment (USD millions) |
| is_mock | bool | Always True for mock data |
| source_url | str | Source URL (placeholder) |

## B – tariffs.csv

| Column | Type | Description |
|---|---|---|
| country | str | |
| year | int | 2015–2024 |
| region | str | SAPP / EAPP / CAPP |
| residential_usd_kwh | float | Residential tariff ($/kWh) |
| commercial_usd_kwh | float | Commercial tariff ($/kWh) |
| industrial_usd_kwh | float | Industrial tariff ($/kWh) |
| avg_usd_kwh | float | Average tariff ($/kWh) |
| cost_recovery_pct | float | Cost recovery ratio (%) |
| subsidy_usd_millions | float | Implicit subsidy (USD millions) |
| is_mock | bool | |
| source_url | str | |

## C – transition.csv

| Column | Type | Description |
|---|---|---|
| country | str | |
| year | int | 2015–2024 |
| region | str | SAPP / EAPP / CAPP |
| total_capacity_mw | float | Total installed capacity (MW) |
| renewable_mw | float | Total renewable capacity (MW) |
| solar_mw | float | Solar PV (MW) |
| wind_mw | float | Wind (MW) |
| hydro_mw | float | Hydropower (MW) |
| geothermal_mw | float | Geothermal (MW) |
| fossil_mw | float | Fossil fuel (MW) |
| renewable_share_pct | float | Renewable share of total capacity (%) |
| co2_intensity_gco2_kwh | float | CO₂ intensity (gCO₂/kWh) |
| is_mock | bool | |
| source_url | str | |

## D – institutions.csv

| Column | Type | Description |
|---|---|---|
| country | str | |
| region | str | SAPP / EAPP / CAPP |
| utility_name | str | Main electricity utility |
| utility_ownership | str | public / private / mixed |
| regulator_exists | bool | Dedicated energy regulator |
| tariff_mechanism | str | cost-reflective / political / hybrid |
| unbundled | bool | Generation/T&D unbundled |
| reform_year | int | Year of major sector reform |
| iea_member | bool | |
| comesa_member | bool | |
| sadc_member | bool | |
| year | int | Reference year (2024) |
| source_url | str | |
| is_mock | bool | |

---

## G – Design Tokens (`assets/theme.css`)

| Token | Value | Usage |
|---|---|---|
| --wb-blue | #0071BC | Primary brand / KPI card accent |
| --wb-blue-dark | #004F8B | Dark surfaces |
| --wb-blue-light | #009FDA | Links, accents, header subtitle |
| --bg-header | #003F72 | App header background |
| --bg-sidebar | #1B2A3B | Filter rail background |
| --bg-app | #F0F4F8 | Page background |
| --accent-success | #27AE60 | Positive trend indicators |
| --accent-warning | #E67E22 | Warnings; mock data banner |
| --accent-danger | #C0392B | Negative trend indicators |
| --border-radius | 6px | Card and input rounding |
| --card-shadow | 0 1px 4px rgba(0,63,114,.10) | Card depth |
