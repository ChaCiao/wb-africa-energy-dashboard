# WB Africa Energy Dashboard

Interactive energy analytics dashboard for 13 Sub-Saharan African countries (2015–2024).  
Built with Python Dash + Plotly. Currently runs on **mock data only** — not for citation.

## Live Demo

> Deploy to Render or Railway using the configuration files in this repo.

## Features

| Module | Description |
|---|---|
| **Access** | Electrification rates, urban/rural gap, country heatmap, access gap ranking |
| **Economics** | Residential & commercial tariffs, cost-recovery, implicit subsidy |
| **Transition** | Renewable share trend, solar/hydro capacity, CO₂ intensity |
| **Institutions** | Sector reform scores, regulator presence, utility structure |
| **Focus Country** | Per-country deep-dive with KPI rankings and multi-year charts |
| **Analytics** | Correlation scatter, country rankings table, trend alerts |
| **Animation** | ▶ Play button auto-advances the year slider |

## Countries Covered

13 SSA countries across three power pools:

- **SAPP** (Southern): Lesotho, Namibia, Botswana, Zambia, Zimbabwe, Mozambique, Malawi
- **EAPP** (Eastern): Ethiopia, Kenya, Tanzania, Uganda
- **CAPP** (Central): DRC, Cameroon

## Tech Stack

- Python 3.11
- [Dash](https://dash.plotly.com/) 4.x + [dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/) 2.x
- [Plotly](https://plotly.com/python/) 6.x
- pandas 3.x
- gunicorn (production server)

## Local Setup

```bash
git clone https://github.com/ChaCiao/wb-africa-energy-dashboard.git
cd wb-africa-energy-dashboard

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
python app.py
```

Open [http://localhost:8050](http://localhost:8050)

## Deploy to Render

1. Fork or push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service** → connect the repo.
3. Render auto-detects `render.yaml` — no manual config needed.
4. First deploy takes ~2 min; mock CSVs are generated on startup.

## Deploy to Railway

1. Install the [Railway CLI](https://docs.railway.app/develop/cli) or use the web UI.
2. Connect the repo; Railway detects the `Procfile` automatically.
3. Set env var `DASH_DEBUG=false` for production.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8050` | Server port (set automatically by Render/Railway) |
| `DASH_DEBUG` | `true` | Set to `false` in production |
| `IS_MOCK` | `true` | Mock data flag (always true in current release) |

## Data

All data is **synthetically generated** in `data/loaders.py` on first startup.  
CSVs are written to `data/*.csv` and excluded from version control (`.gitignore`).  
No real World Bank API calls are made.

## License

MIT
