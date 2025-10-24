import streamlit as st
import pandas as pd
from utils.viz import line_chart, bar_chart, map_chart

def app(tables, raw):
    st.header("📊 Overview of Air Traffic Trends in France")

    st.markdown("""
    This section provides a **high-level view of air traffic evolution** across French airports from 1990 to 2024.
    Explore the **total passenger and freight traffic**, identify **major hubs**, and observe **long-term trends**.
    """)

    # Sidebar Filters
    st.sidebar.subheader("Overview Filters")
    zones = raw['zone'].unique().tolist()
    selected_zones = st.sidebar.multiselect("Select Zone(s)", zones, default=zones)

    # Year range from the 'annee' column
    years = sorted(raw['annee'].dropna().astype(int).unique())
    start_year, end_year = st.sidebar.select_slider(
        "Select Year Range",
        options=years,
        value=(years[0], years[-1])
    )

    # Filter raw data for KPIs
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
    st.subheader("📈 Passenger Traffic Over Time")
    # Filter timeseries table
    timeseries_table = tables['timeseries']
    timeseries_table_filtered = timeseries_table[
        (timeseries_table['zone'].isin(selected_zones)) &
        (timeseries_table['date'].dt.year >= start_year) &
        (timeseries_table['date'].dt.year <= end_year)
    ]
    line_chart(timeseries_table_filtered)

    st.markdown("---")
    st.subheader("🏢 Top Airports by Passenger Traffic")
    by_airport_table = tables['by_airport'].copy()
    by_airport_table_filtered = by_airport_table[
        by_airport_table['zone'].isin(selected_zones)
    ]
    top_airports = by_airport_table_filtered.sort_values('passengers_total', ascending=False).head(10)
    bar_chart(top_airports)

    st.markdown("---")
    st.subheader("🗺️ Geographic Distribution of Air Traffic")
    map_table = tables['geo'].copy()
    map_table_filtered = map_table[
        map_table['zone'].isin(selected_zones)
    ]
    map_chart(map_table_filtered)

    st.markdown("""
    This overview allows users to **identify trends, hotspots, and fluctuations** in air traffic.
    You can further explore **regional comparisons and distribution details** in the next section.
    """)
