# Evolution of Air Traffic in France (1990–2024)


**Author:** Mezzi Nour

**Email:** [[nour.mezzi@efrei.net](mailto:your.email@efrei.fr)]

**Instructor:** Mano Joseph Mathew

**Hashtags:** #EFREIDataStories2025 #DataVisualization #Streamlit #OpenData

---

## Project Overview

This project is a **data storytelling dashboard** built with **Streamlit**.
It explores how **air traffic in France** has evolved from **1990 to 2024**, using open data from the **Direction Générale de l’Aviation Civile (DGAC)**.

The app lets users explore **passenger, freight, and flight movement trends** over time, showing how traffic reacts to **major global events** such as the **9/11 attacks**, the **2008 financial crisis**, the **COVID-19 pandemic**, and the **Ukraine war**.

It combines **data analysis, visualization, and narrative storytelling** to turn 34 years of raw data into meaningful insights.

---

## Objectives

* Show how **air traffic changed** in France between **1990 and 2024**
* Compare **Metropolitan France (MT)** and **Overseas territories (OM)**
* Identify **top airports** for passengers and freight
* Highlight the **impact of major crises** on air travel
* Present the findings in an **interactive and educational dashboard**

---

## Dataset Information

* **Source:** [DGAC Open Data – French Monthly Air Traffic](https://www.data.gouv.fr/datasets/trafic-aerien-commercial-mensuel-francais-par-paire-daeroports-par-sens-depuis-1990/)
* **Period covered:** 1990–2024
* **Granularity:** Monthly data per airport and region
* **Main columns:**

  * `code_aeroport` — Airport code
  * `nom_aeroport` — Airport name
  * `zone` — Region (MT or OM)
  * `passagers_depart`, `passagers_arrivee`, `passagers_transit`
  * `fret_depart`, `fret_arrivee`
  * `mouvements_passagers`, `mouvements_cargo`
  * `annee`, `mois`, `ville`, `latitude`, `longitude`
---

## Data Cleaning and Enrichment 

To enhance the dataset and improve the geographic accuracy of the visualizations, I enriched the original DGAC data with airport coordinates and city names.
This was done by merging it with the [OurAirports database](https://github.com/davidmegginson/ourairports-data/blob/main/airports.csv) and manually adding missing entries for certain airport codes that were not in the OurAirports database.

---

## App Structure

```
app.py
├── sections/
│   ├── intro.py               # Context, objectives, and dataset o
│   ├── overview.py            # KPIs and general traffic trends
│   ├── deep_dives.py          # Regional comparisons, events, maps
│   └── conclusions.py         # Insights, implications, and next steps
│
├── utils/
│   ├── io_utils.py                  # Data loading and caching
│   ├── prep.py                # Cleaning, feature engineering
│   ├── prep.ipynb             # Data cleaning and preprocessing
│   └── viz.py                 # Reusable visualization functions
│
├── data/                      # Raw and processed data files
└── assets/                    # Bakground Image
```

---

## Features & Interactivity

**Sidebar filters**

* Choose one or both zones (MT / OM)
* Select year range (1990–2024)
* Pick metric: passengers, freight, or movements

**Interactive charts**

* Line charts for time evolution
* Bar charts for top airports and regions
* Heatmaps for seasonal patterns
* Map visualizations for geographic insights
* Stacked area chart for zone composition

**Caching & performance**

* Uses `st.cache_data` for faster loading
* Efficient filtering and aggregation

---

## Key Insights

* Air traffic **grew consistently** from 1990 to 2019, before collapsing in **2020 (COVID-19)**.
* **Metropolitan France (MT)** dominates all metrics, while **OM** stays smaller but stable.
* **Paris–CDG and Orly** remain the **core hubs**, with **Nice, Lyon, Marseille, Toulouse, Bordeaux** as strong regional airports.
* **Freight traffic** is heavily centered at **CDG** and recovers faster after crises.
* **Flight movements** reflect global shocks and recovery patterns clearly over time.

---

## Insights, Implications & Next Steps

### What the data shows

* Traffic grew strongly for 30 years, with major dips during world crises.
* Air travel is highly centralized around Paris.
* Overseas regions maintain stable, essential connections.

### Why it matters

* Understanding these patterns helps with **planning, resilience, and sustainability**.
* Data-driven insights can support decisions on **airport capacity**, **logistics**, and **green mobility**.

### What’s next

* Add **forecasting models** to predict recovery and growth.
* Integrate **CO₂ and fuel metrics** for environmental impact.
* Compare **air and rail traffic** for short-distance routes.
* Include **data quality dashboards** and export tools.

---

## Technical Requirements

* **Python ≥ 3.9**
* **Streamlit ≥ 1.33**
* **pandas, numpy, plotly, altair, geopandas, pydeck**
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
* Streamlit Documentation — [streamlit.io](https://docs.streamlit.io/)
* Plotly Python Library — [plotly.com/python](https://plotly.com/python/)
* EFREI Data Storytelling Project Guide — 2025

