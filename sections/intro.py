import streamlit as st

def render(start_date=None, end_date=None):
    st.title("Crisis seen from above")

    st.caption(
        "Explore how air traffic in France has changed (1990–2024) with clear visuals "
        "and simple words. Data: DGAC Open Data."
    )

    st.markdown("""
### Introduction

Air travel is a big part of life and work in France.  
This dashboard shows **how passengers and freight changed from 1990 to 2024**, using open data from the **DGAC**.

The main idea is simple: **watch traffic over time**, see **which airports and routes matter most**, and notice how big events shape the numbers.  
We put a special spotlight on **COVID-19**, because it caused the deepest, fastest drop ever seen in the data.

---

### COVID-19 in one look

From **early 2020** to **mid-2021**, traffic collapsed.  
Flights stopped, borders closed, and airports went quiet.  
After that, traffic started to come back, month by month.  
In the charts, you will see a **red band** over this period to make it clear.

---

### What you can do here

- Follow **passenger** and **freight** trends over the years  
- Find the **busiest airports** and how they compare  
- Check **airlines** and how their market share moves  
- Explore **routes** and how people move across the network  
- Measure **recovery vs 2019** (before COVID-19)

---

### About the data

- **Source:** DGAC Open Data — *Trafic aérien commercial mensuel français*  
- **Granularity:** monthly

**Files used in this app**
- **APT (airports):** 1990–2024 — passengers, freight, movements, coordinates  
- **CIE (airlines):** 2010–2024 — passengers, flights, passenger-km, freight  
- **LSN (routes/links):** 1990–2024 — flows between areas (e.g., Métropole → pays/zone)

Main columns you’ll meet: 
- `month`, `date`
- `recovery_vs_2019_pct` : means how much traffic has recovered compared to 2019 levels
- `passengers_total` : total number of passengers (departures + arrivals + transit)
- `freight_total` : total freight (departures + arrivals)
- `cie_nom`, `carrier`: airline name
- `cie_pkt` : passenger-kilometers for airlines
- `cie_vol` : freight volume for airlines
- `cie_pax` : number of passengers for airlines
- `lsn_pax` : number of passengers on routes
- `route_pair` : route between two locations
 


---

### Why it matters

Understanding air traffic helps:
- **Public decision-makers** plan airports and greener transport
- **Economists** track tourism, trade, and recovery after shocks
- **Everyone** see how world events change daily mobility

---

### How to read the dashboard

- Use the **date filter in the left sidebar** to set your period  
- Start with **Intro** and **Trends**, then dive into **Airports**, **Airlines**, and **Routes**  
- Watch the **COVID-19 red band** on time charts to compare before/after

Enjoy exploring the data!
""")
