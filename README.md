# SCARECRO Water Management Dashboard


![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat-square&logo=pandas&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800?style=flat-square&logo=grafana&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-000000?style=flat-square)

An publicly available agricultural water management system
- Presented at Western SARE I-CREWS 
- OpenET Conference (Nov 17, 2026) 
- AGU26 Annual Meeting, San Francisco (Dec 2026)

---

# Overview


SCARECRO is a fully automated water/irrigation management system built developed through the Western SARE I-CREWS project at the University of Idaho, with support from the Department of Computer Science. It was built specifically to serve The Sandpoint Organic Agriculture Center of University of Idaho's  Agricultural and Life Sciences farm research site and similar agricultural research sites across the Western United States bringing together satellite derived Evapotranspiration ("ET") data and on site weather sensor data into a single, continuously updated dashboard that anyone on the research team can use without any technical background in programming.


# Problem 


The Sandpoint Organic Agriculture Center (SOAC) is one of only two USDA Certified Organic programs in the University of Idaho's College of Agricultural and Life Sciences. Nestled at the base of Schweitzer Mountain in Bonner County, Idaho, the center manages a certified organic heirloom fruit orchard producing 68 varieties of apples, eight varieties of pears, and eight additional fruit types — all under organic certification standards that leave no room for error in irrigation and soil health management.

Organic certification means SOAC cannot rely on synthetic interventions to correct over or under-watering after the fact. Getting irrigation right requires understanding exactly how much water the orchard is losing to evaporation and transpiration on any given day, a measurement called evapotranspiration (ET) and how local weather conditions are contributing to that loss. Without a centralized system to collect, analyze, and surface this information to make better irrigation decisions, researchers and farm managers often times have to manually piece together data from satellite platforms and on site weather and soil sensors or pay huge price for other expensive paid only agricultural data programs, a time-consuming process prone to delays and missed patterns as well as extra expenses.

Project SCARECRO was built to solve that problem.

# Dashboard 


<img width="1600" height="860" alt="Screenshot 2026-09-23 at 2 50 48 PM" src="https://github.com/user-attachments/assets/75feab7c-8dd5-44f6-83fb-110031f9a903" />



- Current Conditions & Live Trends — The top section shows real time weather data from the on-site station: current temperature, feels like, humidity, barometric pressure, wind speed, rainfall totals, last rain date, leaf wetness, and air quality readings. Alongside this, two live time series charts show the temperature trend over the past 30 days and the ET data trend, giving researchers an immediate sense of what the conditions are now and where where it is heading.

- Irrigation Recommendation — A water stress score gauge (0–100) and a plain-English recommendation generated daily from the combined ET and weather analysis file on python. This is the primary decision-making tool for irrigation planning. 

- Weather Analysis (Past 30 Days) — Statistical breakdown of recent weather conditions: temperature trends, days exceeding heat stress threshold, total and weekly rainfall, humidity change, and date of last rainfall giving researcher full data from the past 4 weeks to help analyze the weather and seasonal shift and it's affect on the field site. 

- ET Data (Since 06/17/2026) — Statistics calculated from satellite ET data since the project began: average daily ET, cumulative seasonal ET, highest and lowest recorded ET, above-average stress days, longest consecutive stress streak with dates, week-over-week percentage change, and past 4-week average to give the researchers how much of the water used for irrigation is being lost due to ET that could potentially cause dehydration or over irrigation.


# Engineering / Programming Overview

- Data Collection

  Two separate Python scripts handle data collection — one for satellite ET data via the OpenET REST API, and one for the Ambient Weather station API. Both         authenticate via API keys, construct structured requests with the appropriate parameters (coordinates, date ranges, units, models), and store the raw responses
  directly into MongoDB. The weather station script runs every 15 minutes on a Linux server, while the ET pipeline runs once daily via GitHub Actions

- Data Storage Architecture

  The project uses a deliberately structured MongoDB schema split across two separate Atlas clusters. Raw sensor and satellite data live in their own               collections, while analysis outputs are stored separately in summary and trend collections. This separation means Grafana can read pre-computed results           directly without running heavy queries on raw data, keeping the dashboard fast and the data organized. All writes use upsert operations to prevent duplicates     regardless of how many times the pipeline runs.


Analysis Pipeline
---

<img width="1680" height="577" alt="Screenshot 2026-09-23 at 3 45 39 PM" src="https://github.com/user-attachments/assets/f39bc6a0-b00a-4af4-a79f-b3676c03caaa" />
<img width="1673" height="372" alt="Screenshot 2026-09-23 at 3 38 03 PM" src="https://github.com/user-attachments/assets/77955b99-1778-4764-81c8-eb93ed79877a" />


---





The analysis file scripts are where the core engineering work lives. Rather than just storing raw numbers, each script uses and relies heavily on Python's        Pandas library to transform raw time series data into meaningful structured data analysis insights:






- Aggregation — Raw 15-minute weather readings are aggregated into daily and weekly averages, giving researchers clean trend data split into different but clear analysis section instead of noisy individual readings
- Rolling averages — A 7-day rolling average is applied to ET data to smooth out daily fluctuations and make the underlying trend much clearer
- Streak detection — A custom algorithm detects consecutive days where ET or temperature exceeded a threshold — because sustained above-average conditions signal water stress far more than a single bad day does. The algorithm groups consecutive dates, finds the longest streak, and extracts its start and end dates to help avoid weather and irrigation based crop damages.
Week-over-week comparison — Each analysis script calculates the percentage change between the most recent week and the previous week, giving researchers a directional signal: is stress increasing or decreasing heading into the next week?
- Seasonal baseline — Rather than comparing against a fixed threshold, ET is compared against the past 4-week average, which automatically adjusts for the season and helps researchers identify where the season/weather is heading going into next week.


# Irrigation Recommendation Engine

<img width="1655" height="488" alt="Screenshot 2026-09-23 at 3 58 24 PM" src="https://github.com/user-attachments/assets/c638236f-50ba-414b-b3e1-904850986bda" />


---



The recommendation script reads from both analysis collections and combines the signals into a single water stress score. ET streak length, rainfall deficit, heat stress days, and humidity trends each contribute points to the score. The final number (0–100) maps to one of four plain-English recommendations. This makes the output immediately actionable for a farmer or researcher without requiring them to interpret multiple charts.


# Automation & Security


The full pipeline runs automatically every day via GitHub Actions with four sequential jobs — each waits for the previous to succeed before starting. All credentials are managed through GitHub Secrets and local .env files, never hardcoded in the codebase. The pipeline includes error handling that stops execution cleanly if a connection fails, and guard clauses that protect analysis steps from crashing when data conditions don't meet thresholds.


# Visualization


MongoDB aggregation pipelines written in JSON connect the database directly to Grafana. A single source query feeds multiple visualization panels through Grafana's dashboard data source pattern, reducing redundant database calls. The result is a live, auto-refreshing dashboard that updates daily without any manual intervention.

# How it Works


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
| [OpenET](https://etdata.org) | Daily satellite-derived ET estimates using an ensemble of five ET models from Nasa satellite data|
| [Ambient Weather WS-1965](https://ambientweather.com) | On-site temperature, humidity, rainfall, wind, barometric pressure, air quality, leaf wetness |
| MongoDB Atlas | Cloud storage for all raw and analyzed data |
| Grafana | Live visualization dashboard |



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

## Research Locations

| Location | Coordinates | ET Satellite Model |
|----------|------------|---------|
| SOAC Sandpoint | 48.3222°N, 116.5541°W | Ensemble |
| Harbor Center CDA | 47.6834°N, 116.7969°W | SSEBop |
| Deary Forest | 46.8801°N, 116.5562°W | eeMETRIC |


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

## Project Background
---

- This project was developed during the summer of 2026 through the **Western SARE I-CREWS project** at the University of Idaho, with support from the Department of Computer Science. The goal was to build an open-source, accessible water management tool for SOAC, a working certified organic research farm sit of University of Idaho's Agriculture research program that needed a better way to monitor field conditions and plan irrigation without manual data collection and analysis.

- The project demonstrates how publicly available satellite data (OpenET) can be combined with low-cost on-site sensor data to create real, actionable insights for agricultural researchers and small-scale farming operations across the Western United States.

# Authors

- Tengisbolor "Tebo" Shinetulga — University of Idaho / North Idaho College
- Joseph Harris — University of Idaho / North Idaho College
- Dr. Mary Everett — University of Idaho, Department of Computer Science CDA Associate Director 
- Dr. John Shovic — University of Idaho, Department of Computer Science CDA Director

# Acknowledgments

The project described was supported by NSF award number OIA-2242769 from the NSF Idaho EPSCoR Program and by the National Science Foundation. 

# License

MIT License — free to use, modify, and distribute with attribution.
