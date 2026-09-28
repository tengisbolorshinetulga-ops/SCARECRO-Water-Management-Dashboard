# SCARECRO Water Management Dashboard

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat-square&logo=pandas&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800?style=flat-square&logo=grafana&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-000000?style=flat-square)

A publicly available agricultural water management system integrating satellite ET data with IoT weather sensors — built during a research internship with the University of Idaho.

**In active use** by the University of Idaho College of Agricultural and Life Sciences research team at the Sandpoint Organic Agriculture Center.

**Presented at:**
- Western SARE I-CREWS (Jul 18, 2026)
- OpenET Conference, Salt Lake City (Nov 17, 2026)
- AGU26 Annual Meeting, San Francisco (Dec 2026)

---

## Key Metrics

| | |
|---|---|
| Running daily since | June 17, 2026 (100+ days) |
| Weather readings collected | ~10,000 (every 15 minutes) |
| Calculated metrics | 25+ ET and weather statistics, updated daily |
| Streak detection | Runs on 3 variables: ET, temperature, humidity |
| Recommendation engine | 6 weighted factors → 0–100 water stress score |
| Automated pipeline | 4 sequential GitHub Actions jobs, zero manual steps |
| Database | 7 MongoDB collections across 2 Atlas clusters |
| Research sites | 3 University of Idaho locations |

---

## My Role

**Research Intern — Western SARE I-CREWS, University of Idaho (Summer 2026)**

- Lead author and presenter at Western SARE I-CREWS, the OpenET Conference, and AGU26
- Built the analysis pipeline in Python/Pandas: ET analysis, weather analysis, and the irrigation recommendation engine
- Designed the MongoDB summary and trend collections powering the dashboard
- Automated the full pipeline with a 4-stage GitHub Actions CI/CD workflow
- Built the Grafana analysis and irrigation recommendation panels
- Translated raw satellite and sensor data into tools usable by researchers with no programming background

---

## Overview

SCARECRO automatically combines satellite evapotranspiration (ET) data with on-site weather data, analyzes it daily, and delivers a plain-English irrigation recommendation on a live dashboard. No programming knowledge is needed to use it.

---

## Problem

- **High stakes:** SOAC is one of only two USDA Certified Organic programs at the University of Idaho, growing 68 apple varieties, 8 pear varieties, and 8 other fruit types.
- **No room for error:** organic rules mean irrigation mistakes can't be corrected with synthetic inputs after the fact.
- **Scattered data:** ET and weather data lived on separate platforms and had to be pieced together manually.
- **Technical barrier:** building a custom dashboard from raw satellite and sensor data requires programming skills the research team didn't have.
- **Costly alternatives:** commercial agricultural data platforms charge ongoing subscription fees.

**SCARECRO replaces that manual process with one automated, no-code dashboard.**

---

## Dashboard

<img width="1600" height="860" alt="SCARECRO Grafana dashboard" src="https://github.com/user-attachments/assets/75feab7c-8dd5-44f6-83fb-110031f9a903" />

- **Current Conditions & Live Trends** — live temperature, humidity, pressure, wind, rainfall, leaf wetness, and air quality, plus 30-day temperature and ET trend charts
- **Irrigation Recommendation** — daily 0–100 water stress score with a plain-English recommendation
- **Weather Analysis (Past 30 Days)** — heat stress days, rainfall totals, humidity trends, and last rain date
- **ET Data (Since 06/17/2026)** — average, cumulative, highest/lowest ET, stress streaks, and week-over-week change

---

## Engineering Overview

### Data Collection
- Python REST clients pull daily ET from OpenET and 15-minute readings from the Ambient Weather station
- Raw data is stored directly in MongoDB for downstream analysis

### Data Storage Architecture
- MongoDB schema split across 2 Atlas clusters: raw data, summary, and trend collections kept separate
- Grafana reads pre-computed results instead of querying raw data, keeping the dashboard fast
- All writes use upserts, so reruns never create duplicates

### Analysis Pipeline

<img width="1680" height="577" alt="Analysis script" src="https://github.com/user-attachments/assets/f39bc6a0-b00a-4af4-a79f-b3676c03caaa" />
<img width="1673" height="372" alt="Analysis script" src="https://github.com/user-attachments/assets/77955b99-1778-4764-81c8-eb93ed79877a" />

Pandas turns raw time series data into decision-ready insights:
- **Aggregation** — 15-minute readings rolled into daily and weekly averages
- **Rolling averages** — 7-day ET average smooths daily noise
- **Streak detection** — custom algorithm finds the longest run of above-threshold days for ET, temperature, and humidity, with start and end dates
- **Week-over-week change** — shows whether stress is rising or falling
- **Seasonal baseline** — ET compared against a rolling 4-week average instead of a fixed threshold

### Irrigation Recommendation Engine

<img width="1655" height="488" alt="Irrigation recommendation script" src="https://github.com/user-attachments/assets/c638236f-50ba-414b-b3e1-904850986bda" />

- Combines 6 weighted factors from ET and weather analysis into one 0–100 water stress score
- Maps the score to 4 plain-English recommendations, from "no irrigation needed" to "irrigate within 48 hours"

### Automation & Security
- 4 sequential GitHub Actions jobs run daily, each waiting on the previous one to succeed
- Credentials live in GitHub Secrets and `.env` files, never in code
- Error handling and guard clauses prevent crashes on missing data or failed connections

### Visualization
- MongoDB aggregation pipelines in JSON feed Grafana directly
- One source query powers multiple panels, cutting redundant database calls

---

## How It Works

```
OpenET Satellite API            Ambient Weather Station
        │                                │
        ▼                                ▼
  All_Locations2.py          Weather_station_data.py
  (Daily ET fetch)           (15-min weather fetch)
        │                                │
        ▼                                ▼
  ET_data (MongoDB)          WEATHER_STATION (MongoDB)
        │                                │
        ▼                                ▼
  et_analysis.py             weather_analysis.py
        │                                │
        ▼                                ▼
  ET_summary / ET_trends     WEATHER_ANALYSIS / WEATHER_TRENDS
        └──────────────┬─────────────────┘
                       ▼
         irrigation_recommendation.py
                       │
                       ▼
           IRRIGATION_RECOMMENDATION
                       │
                       ▼
               Grafana Dashboard
```

---

## Data Sources

| Source | What It Provides |
|--------|-----------------|
| [OpenET](https://etdata.org) | Daily satellite-derived ET estimates using an ensemble of satellite ET models built on Landsat data |
| [Ambient Weather WS-1965](https://ambientweather.com) | On-site temperature, humidity, rainfall, wind, barometric pressure, air quality, leaf wetness |
| MongoDB Atlas | Cloud storage for all raw and analyzed data |
| Grafana | Live visualization dashboard |

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | All data collection and analysis scripts |
| Pandas | Time series aggregation, statistical analysis, streak detection |
| PyMongo | MongoDB reads and writes from Python |
| MongoDB Atlas | Multi-collection cloud database across two clusters |
| Grafana | Live dashboard with MongoDB aggregation pipeline queries |
| GitHub Actions | Automated daily CI/CD pipeline with sequential job dependencies |
| OpenET API | Satellite ET data via REST |
| Ambient Weather API | IoT weather station data via REST |
| python-dotenv | Environment variable and secrets management |

---

## Research Locations

| Location | Coordinates | ET Satellite Model |
|----------|------------|---------|
| SOAC Sandpoint | 48.3222°N, 116.5541°W | Ensemble |
| Harbor Center CDA | 47.6834°N, 116.7969°W | SSEBop |
| Deary Forest | 46.8801°N, 116.5562°W | eeMETRIC |

---

## Setup

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (free tier works)
- OpenET API key — [register at etdata.org](https://etdata.org)
- Ambient Weather account and API keys
- Grafana instance with the [haohanyang MongoDB datasource plugin](https://github.com/haohanyang/mongodb-datasource)

### Installation

```bash
git clone https://github.com/tengisbolorshinetulga-ops/SCARECRO-Water-Management-Dashboard.git
cd SCARECRO-Water-Management-Dashboard
pip install requests pymongo pandas python-dotenv matplotlib
```

### Environment Variables

Create a `.env` file in the `SARE_repo/` directory:

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=YourApp
OPENET_API_KEY=your_openet_api_key
AMBIENT_API_KEY=your_ambient_api_key
AMBIENT_APPLICATION_KEY=your_ambient_application_key
WEATHER_MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=YourApp
```

### GitHub Actions Secrets

Add to your repository under Settings → Secrets → Actions:
- `MONGODB_URI`
- `OPENET_API_KEY`
- `WEATHER_MONGODB_URI`

### Running Manually

```bash
python3 SARE_repo/All_Locations2.py                        # Fetch ET data
python3 SARE_repo/analysis/et_analysis.py                  # Run ET analysis
python3 SARE_repo/analysis/weather_analysis.py             # Run weather analysis
python3 SARE_repo/analysis/irrigation_recommendation.py    # Generate recommendation
```

---

## Project Background

- This project was developed during the summer of 2026 through the **Western SARE I-CREWS project** at the University of Idaho, with support from the Department of Computer Science. The goal was to build an open, accessible water management tool for SOAC, a working certified organic research farm site of the University of Idaho's agricultural research program that needed a better way to monitor field conditions and plan irrigation without manual data collection and analysis.

- The project demonstrates how publicly available satellite data (OpenET) can be combined with low-cost on-site sensor data to create real, actionable insights for agricultural researchers and small-scale farming operations across the Western United States.

---

## Authors

- **Tengisbolor "Tebo" Shinetulga** — University of Idaho / North Idaho College
- **Joseph Harris** — University of Idaho / North Idaho College
- **Dr. Mary Everett** — University of Idaho, Department of Computer Science, CDA Associate Director
- **Dr. John Shovic** — University of Idaho, Department of Computer Science, CDA Director

---

## Acknowledgments

The project described was supported by NSF award number OIA-2242769 from the NSF Idaho EPSCoR Program and by the National Science Foundation.

---

## License

MIT License — free to use, modify, and distribute with attribution.
