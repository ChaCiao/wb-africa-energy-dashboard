# WB Africa Energy Dashboard — CLAUDE.md

> **TODO:** Fill in project-specific context below.

## Project Overview

World Bank Sub-Saharan Africa Energy Access Dashboard.  
Python Dash application for multi-tier analysis of energy access, tariffs, and energy transition metrics across 13 SSA countries, 2015–2024.

## Stack

- Python 3.10+
- Dash + dash-bootstrap-components
- Plotly
- Pandas

## Rules

- Code and comments: **English**
- Conversation: **Korean**
- Confirm scope before large changes

## Country Tiers

| Tier | Scope | Selection |
|------|-------|-----------|
| Tier 1 | Focus countries | Lesotho, Namibia |
| Tier 2 | Regional comparison | All 13 countries |
| Tier 3 | Continental overview | All 13 + SAPP/EAPP/CAPP pool aggregates |

## Data

All CSVs are mock (is_mock=True). Real data pipeline is a future phase.  
CSVs are auto-generated on first `python app.py` via `data/loaders.py`.

## Completed Sprints

- [ ] Sprint 0: Skeleton scaffold (folder structure, mock data, layout, filter tier callback)

## Pending

- [ ] Sprint 1: KPI row callbacks + dimension charts (access / tariff / transition / institutions)
