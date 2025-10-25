# Evolution of Air Traffic in France (1990–2024)


**Author:** Mezzi Nour

**Email:** [[nour.mezzi@efrei.net](mailto:your.email@efrei.fr)]

**Instructor:** Mano Joseph Mathew

**Hashtags:** #EFREIDataStories2025 #DataVisualization #Streamlit #OpenData

---

## Project Overview

This project is a Streamlit data-storytelling dashboard that traces how French air traffic evolved from 1990 to 2024 using open data from the Direction Générale de l’Aviation Civile (DGAC).
It turns 34 years of raw monthly data into an interactive story: you can explore passengers, freight, airlines, and routes; see the shock of COVID-19 and the recovery; and identify the airports and carriers that structure the French network.

---

## Objectives

* Track how passenger and freight changed between 1990–2024
* Surface top airports, airlines, and routes
* Show the COVID-19 impact and the recovery vs 2019
* Compare Metropolitan (MT) vs Overseas (OM) where relevant
* Provide a clean data-quality view (schema, duplicates, outliers, missing)

---

## Dataset Information

* **Source:** [DGAC Open Data – French Monthly Air Traffic](https://www.data.gouv.fr/datasets/trafic-aerien-commercial-mensuel-francais-par-paire-daeroports-par-sens-depuis-1990/)
* **Period covered:** 1990–2024
* **Granularity:** Monthly data per airport and region
* **Main columns:**

  * Airports (APT): code_aeroport, nom_aeroport, zone, passagers_depart, passagers_arrivee, fret_depart, fret_arrivee, latitude, longitude, annee, mois
  * Airlines (CIE): cie_nom, cie_pax, cie_vol, cie_pkt, annee, mois
  * Routes (LSN): lsn_1, lsn_2, lsn_pax, annee, mois
---

## Data Cleaning and Enrichment 

To enhance the Airport dataset and improve the geographic accuracy of the visualizations, I enriched the original DGAC data with airport coordinates and city names.
This was done by merging it with the [OurAirports database](https://github.com/davidmegginson/ourairports-data/blob/main/airports.csv) and manually adding missing entries for certain airport codes that were not in the OurAirports database.

---

## App Structure

```
app.py
├── sections/
│   ├── intro.py         # Textual context only (story intro)
│   ├── trends.py        # Long-run trends, COVID band, scenario/projection
│   ├── airports.py      # Bubbles map, freight vs passengers, top airports
│   ├── airlines.py      # KPIs, top-10, market share (stacked area), scatter
│   ├── routes.py        # KPIs, long-run route trend, busiest routes
│   ├── quality.py       # Schema checks + duplicates/missing/outliers overview
│   └── conclusions.py   # Insights, implications, next steps (plain language)
│
└── utils/
    ├── io.py            # Processed-data loaders (+ caching), date bounds
    ├── prep.py          # Feature engineering & aggregations (timeseries, etc.)
    ├── viz.py           # Reusable Altair/PyDeck charts (bands, maps, bars…)
    ├── metrics.py       # KPIs (totals, recovery vs 2019, top entities)
    └── geo.py           # Airport geo helpers (centroid, hubs) + conversions

data/
├── APT/processed/apt.csv
├── CIE/processed/cie.csv
└── LSN/processed/lsn.csv

assets/
└── plane.jpg            # Background image
```

---

## Features & Interactivity

**Global**

* Sidebar navigation across pages
* Global date range slider (defaults to the full available range)
* Choose one or both zones (MT / OM) when meaningful

**Trends**

* Monthly passenger trend with a COVID-19 red band
* Optional projection with a “Growth scenario (%)” slider
* Seasonality views (monthly distribution)

**Airports**

* Bubble map centered on France (size = passengers, tooltip = name & value)
* Passengers vs Freight scatter with zone filter (MT / OM) and fixed colors
* Top airports bar chart (passengers)
* Geo insights (approx. center, airport count, top hubs)

**Airlines**

* KPI cards: total passengers, top airline, recovery vs 2019
* Top-10 airlines (bar)
* Market share over time (stacked area, top 15 carriers)
* Flights vs PKT scatter (top 15 carriers), legend click to isolate carriers
* Competition hints (HHI & top-3 share) shown textually under the scatter

**Routes**

* KPI cards: total passengers, top route, recovery vs 2019
* Total route passengers (monthly) with COVID band
* Busiest routes (top-10) and CAGR (1990–2024)

**Data Quality**

* Schema validation: expected columns OK + derived columns listed
* No duplicates, no missing values, no outliers reported across APT / CIE / LSN

**Caching & performance**

* Uses `st.cache_data` for faster loading

---

## Key Insights

* Clear long-run growth until 2019, sharp drop in 2020, then recovery close to 2019 levels today.
* The network is highly centralized: CDG and Orly dominate; Nice, Lyon, Marseille, Toulouse, Bordeaux anchor the regions.
* Freight concentrates at CDG and shows stability, recovering faster after shocks.
* Airlines: Air France is the clear leader; low-cost carriers (e.g. : easyJet brands, Transavia, Volotea, Ryanair) gained share post-2010.
* Routes: Paris—Province flows are the busiest; long-haul and leisure corridors amplify seasonality.

---

## Implications & Next Steps

### Why it matters

* Supports capacity planning and resilience (identify chokepoints & recovery dynamics).
* Informs policy on short-haul alternatives and sustainability (especially MT domestic).
* Helps airlines/airports optimize network design, freight strategy, and seasonal resources.

### What’s next

* Forecasting (statistical + ML) for traffic through 2030 with scenarios.
* Add CO2 per route / aircraft family to quantify climate impacts.
* Rail vs air comparisons.
* Monthly ingestion jobs to keep dashboards up to date (data.gouv.fr).

---

## Technical Requirements

* **Python ≥ 3.10**
* **Streamlit ≥ 1.33**
* **pandas, numpy, plotly, altair, pydeck**
* (See `requirements.txt` for full list)

### To run the project :

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Learning Outcomes

Through this project, I learned how to:

* Turn open data into a **coherent data story**
* Apply **EDA and visualization** in Streamlit
* Communicate insights with **clarity and context**
* Combine **data, design, and narrative** for storytelling

---

## Project Links

* [GitHub Repository](https://github.com/MezziNour/Air_Traffic_1990_2024)
* [Deployed App](https://airtraffic.streamlit.app)

---

## References

* DGAC Open Data Portal — [data.gouv.fr](https://www.data.gouv.fr/datasets/trafic-aerien-commercial-mensuel-francais-par-paire-daeroports-par-sens-depuis-1990/)
* OurAirpots Database - [github.com](https://github.com/davidmegginson/ourairports-data/blob/main/airports.csv)
* Streamlit Documentation — [streamlit.io](https://docs.streamlit.io/)
* Plotly Python Library — [plotly.com/python](https://plotly.com/python/)
* EFREI Data Storytelling Project Guide — 2025

