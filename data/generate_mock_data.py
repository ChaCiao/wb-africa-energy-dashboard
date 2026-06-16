"""
Generate mock CSV files for the WB Africa Energy Dashboard.
All rows carry is_mock=True and a placeholder source_url.
Run standalone:  python data/generate_mock_data.py
Or auto-invoked by data/loaders.py on first import.
"""
import os
import sys
import random
import pandas as pd

# Allow running as a standalone script from the project root
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import config  # noqa: E402 – after sys.path fix

OUTDIR = os.path.dirname(os.path.abspath(__file__))
SEED   = 42

# ── Country baselines (2015) ──────────────────────────────────────────────────

_ACCESS_BASE = {
    "Lesotho": 30, "Namibia": 55, "Botswana": 66, "Zambia": 27,
    "Zimbabwe": 38, "Mozambique": 20, "Malawi": 11, "Ethiopia": 22,
    "Kenya": 45, "Tanzania": 24, "Uganda": 19, "DRC": 9, "Cameroon": 52,
}

_RENEW_BASE = {  # renewable share of installed capacity (%)
    "Lesotho": 95, "Namibia": 45, "Botswana": 20, "Zambia": 88,
    "Zimbabwe": 65, "Mozambique": 82, "Malawi": 91, "Ethiopia": 94,
    "Kenya": 85, "Tanzania": 58, "Uganda": 90, "DRC": 96, "Cameroon": 72,
}

_TARIFF_BASE = {  # residential $/kWh
    "Lesotho": 0.10, "Namibia": 0.14, "Botswana": 0.08, "Zambia": 0.06,
    "Zimbabwe": 0.09, "Mozambique": 0.05, "Malawi": 0.04, "Ethiopia": 0.03,
    "Kenya": 0.16, "Tanzania": 0.07, "Uganda": 0.17, "DRC": 0.04,
    "Cameroon": 0.08,
}

_UTILITY_NAME = {
    "Lesotho":    "Lesotho Electricity Company",
    "Namibia":    "NamPower",
    "Botswana":   "BPC (Botswana Power Corporation)",
    "Zambia":     "ZESCO",
    "Zimbabwe":   "ZESA Holdings",
    "Mozambique": "EDM",
    "Malawi":     "ESCOM Malawi",
    "Ethiopia":   "EEP (Ethiopian Electric Power)",
    "Kenya":      "Kenya Power & Lighting",
    "Tanzania":   "TANESCO",
    "Uganda":     "UMEME Ltd.",
    "DRC":        "SNEL",
    "Cameroon":   "AES SONEL (Eneo Cameroon)",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _r(lo, hi, decimals=2):
    return round(random.uniform(lo, hi), decimals)


def _trend(base, year, annual_delta, noise=1.0):
    val = base + (year - 2015) * annual_delta + random.uniform(-noise, noise)
    return round(max(0.0, min(100.0, val)), 2)


# ── Builders ──────────────────────────────────────────────────────────────────

def _build_access():
    rows = []
    for country in config.ALL_COUNTRIES:
        base_nat = _ACCESS_BASE[country]
        for year in config.YEARS:
            nat   = _trend(base_nat, year, 2.0, 1.5)
            urban = round(min(nat * 1.6, 99.0), 2)
            rural = round(max(nat * 0.4,  1.0), 2)
            rows.append({
                "country":                        country,
                "year":                           year,
                "region":                         config.COUNTRY_REGION[country],
                "access_national_pct":            nat,
                "access_urban_pct":               urban,
                "access_rural_pct":               rural,
                "pop_without_electricity_millions": _r(0.5, 30.0),
                "new_connections_thousands":       _r(10, 500),
                "investment_usd_millions":         _r(5, 200),
                "is_mock":                        True,
                "source_url":                     config.MOCK_SOURCE_URL,
            })
    return pd.DataFrame(rows)


def _build_tariffs():
    rows = []
    for country in config.ALL_COUNTRIES:
        base_res = _TARIFF_BASE[country]
        for year in config.YEARS:
            res  = round(max(base_res + (year - 2015) * 0.003 + random.uniform(-0.005, 0.005), 0.01), 4)
            comm = round(res * 1.20, 4)
            ind  = round(res * 0.90, 4)
            avg  = round((res + comm + ind) / 3, 4)
            rows.append({
                "country":             country,
                "year":                year,
                "region":              config.COUNTRY_REGION[country],
                "residential_usd_kwh": res,
                "commercial_usd_kwh":  comm,
                "industrial_usd_kwh":  ind,
                "avg_usd_kwh":         avg,
                "cost_recovery_pct":   _r(40, 110),
                "subsidy_usd_millions": _r(0, 100),
                "is_mock":             True,
                "source_url":          config.MOCK_SOURCE_URL,
            })
    return pd.DataFrame(rows)


def _build_transition():
    rows = []
    for country in config.ALL_COUNTRIES:
        base_renew = _RENEW_BASE[country]
        base_cap   = _r(50, 3000, 1)
        for year in config.YEARS:
            total_cap  = round(base_cap * (1 + (year - 2015) * 0.04), 1)
            renew_share = _trend(base_renew, year, 0.5, 2.0)
            renew_mw   = round(total_cap * renew_share / 100, 1)
            hydro_mw   = round(renew_mw * _r(0.40, 0.90), 1)
            solar_mw   = round(renew_mw * _r(0.05, 0.30), 1)
            wind_mw    = round(max(renew_mw - hydro_mw - solar_mw, 0), 1)
            geo_mw     = round(_r(0, 50) if country in {"Kenya", "Ethiopia", "Uganda"} else 0, 1)
            fossil_mw  = round(max(total_cap - renew_mw, 0), 1)
            rows.append({
                "country":               country,
                "year":                  year,
                "region":                config.COUNTRY_REGION[country],
                "total_capacity_mw":     total_cap,
                "renewable_mw":          renew_mw,
                "solar_mw":              solar_mw,
                "wind_mw":               wind_mw,
                "hydro_mw":              hydro_mw,
                "geothermal_mw":         geo_mw,
                "fossil_mw":             fossil_mw,
                "renewable_share_pct":   renew_share,
                "co2_intensity_gco2_kwh": _r(50, 600),
                "is_mock":               True,
                "source_url":            config.MOCK_SOURCE_URL,
            })
    return pd.DataFrame(rows)


_COMESA = {"Kenya", "Tanzania", "Uganda", "Ethiopia", "DRC", "Zambia", "Zimbabwe", "Malawi", "Mozambique", "Cameroon"}
_SADC   = {"Lesotho", "Namibia", "Botswana", "Zambia", "Zimbabwe", "Mozambique", "Malawi", "DRC", "Tanzania"}


def _build_institutions():
    rows = []
    for country in config.ALL_COUNTRIES:
        rows.append({
            "country":          country,
            "region":           config.COUNTRY_REGION[country],
            "utility_name":     _UTILITY_NAME[country],
            "utility_ownership": random.choice(["public", "mixed", "private"]),
            "regulator_exists": random.choice([True, False]),
            "tariff_mechanism": random.choice(["cost-reflective", "political", "hybrid"]),
            "unbundled":        random.choice([True, False]),
            "reform_year":      random.randint(1998, 2020),
            "iea_member":       False,
            "comesa_member":    country in _COMESA,
            "sadc_member":      country in _SADC,
            "year":             2024,
            "source_url":       config.MOCK_SOURCE_URL,
            "is_mock":          True,
        })
    return pd.DataFrame(rows)


# ── Public entry point ────────────────────────────────────────────────────────

def generate_all():
    random.seed(SEED)
    _build_access().to_csv(      os.path.join(OUTDIR, "access.csv"),       index=False)
    _build_tariffs().to_csv(     os.path.join(OUTDIR, "tariffs.csv"),      index=False)
    _build_transition().to_csv(  os.path.join(OUTDIR, "transition.csv"),   index=False)
    _build_institutions().to_csv(os.path.join(OUTDIR, "institutions.csv"), index=False)
    print(f"[generate_mock_data] 4 CSVs written to {OUTDIR}")


if __name__ == "__main__":
    generate_all()
