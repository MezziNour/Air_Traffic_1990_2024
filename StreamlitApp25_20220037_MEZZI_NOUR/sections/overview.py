import streamlit as st
import pandas as pd
from utils.viz import line_chart, bar_chart, map_chart, seasonality_heatmap

def app(tables, raw):
    # Page header
    st.header("Overview of Air Traffic Trends in France")

    # Intro
    st.markdown("""
    This part gives a **general view of how air traffic has evolved** in France between 1990 and 2024.  
    You can explore **passenger and freight totals**, find out **which airports dominate**,  
    and spot **long-term changes** in the data.
    """)

    # Sidebar filters 
    st.sidebar.subheader("Overview Filters")
    zones = raw['zone'].unique().tolist()
    selected_zones = st.sidebar.multiselect("Select Zone(s)", zones, default=zones)

    # Year range slider 
    years = sorted(raw['annee'].dropna().astype(int).unique())
    start_year, end_year = st.sidebar.select_slider(
        "Select Year Range",
        options=years,
        value=(years[0], years[-1])
    )

    # Filter data based on user input 
    df_filtered = raw[
        (raw['zone'].isin(selected_zones)) &
        (raw['annee'] >= start_year) &
        (raw['annee'] <= end_year)
    ]

    # KPIs 
    total_passengers = df_filtered[['passagers_depart', 'passagers_arrivee', 'passagers_transit']].sum().sum()
    total_freight = df_filtered[['fret_depart', 'fret_arrivee']].sum().sum()
    total_movements = df_filtered[['mouvements_passagers', 'mouvements_cargo']].sum().sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Passengers", f"{int(total_passengers):,}")
    c2.metric("Total Freight (kg)", f"{int(total_freight):,}")
    c3.metric("Total Movements", f"{int(total_movements):,}")

    st.markdown("---")

    # Passenger traffic over time 
    st.subheader("Passenger Traffic Over Time")
    timeseries_table = tables['timeseries']
    timeseries_table_filtered = timeseries_table[
        (timeseries_table['zone'].isin(selected_zones)) &
        (timeseries_table['date'].dt.year >= start_year) &
        (timeseries_table['date'].dt.year <= end_year)
    ]
    line_chart(timeseries_table_filtered)

    # Analysis text
    st.markdown("""
    #### **Analysis:**  
    Passenger traffic shows a **stable growth** from 1990 to 2019, mainly in **Metropolitan France (MT)**.  
    The graph highlights **strong seasonal peaks** each year, usually during summer.  
    A clear **drop in 2020** reflects the **COVID-19 crisis**, followed by a gradual recovery.  
    **Overseas territories (OM)** display much lower traffic levels.
    """)

    st.markdown("---")

    # --- Top airports by traffic ---
    st.subheader("Top Airports by Passenger Traffic")
    by_airport_table = tables['by_airport'].copy()
    by_airport_table_filtered = by_airport_table[
        by_airport_table['zone'].isin(selected_zones)
    ]
    top_airports = by_airport_table_filtered.sort_values('passengers_total', ascending=False).head(10)
    bar_chart(top_airports)

    # Analysis text
    st.markdown("""
    #### **Analysis:**  
    **Paris–Charles de Gaulle** and **Paris–Orly** clearly dominate air traffic in France, together handling most of the country’s passengers.  
    Airports like **Nice**, **Lyon**, **Marseille**, and **Toulouse** form the **secondary network**, reflecting regional tourism and business travel.  
    """)

    st.markdown("---")

    # --- Map of air traffic ---
    st.subheader("Geographic Distribution of Air Traffic")
    map_table = tables['geo'].copy()
    map_table_filtered = map_table[
        map_table['zone'].isin(selected_zones)
    ]
    map_chart(map_table_filtered)

    # Analysis text
    st.markdown("""
    #### **Analysis:**  
    The map shows that **Île-de-France** is the main hub of French air traffic, with **Paris airports** dominating the national network.  
    Major regional airports **Nice, Lyon, Marseille, Toulouse, and Bordeaux** act as key connectors across the country.  
    **Overseas territories** play a smaller role.
    """)

    st.markdown("---")

    # --- Seasonal patterns heatmap ---
    st.subheader("Seasonal Patterns in Air Traffic")
    seasonality_heatmap(df_filtered)

    # Analysis text
    st.markdown("""
    #### **Analysis:**  
    The heatmap reveals **repeating seasonal peaks** each year, especially in **July and August**, driven by summer holidays.  
    Noticeable drops appear around **2009** (financial crisis) and **2020** (COVID-19).  
    Over time, both the **intensity** and **consistency** of these peaks have grown, showing how demand for air travel has increased.
    """)
