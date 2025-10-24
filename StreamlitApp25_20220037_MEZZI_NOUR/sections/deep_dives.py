import streamlit as st
import pandas as pd
from utils.viz import line_chart, bar_chart, map_chart, stacked_area_chart

def app(tables, raw):
    st.header("Deep Dives: Regional Insights & Event Impacts")

    st.markdown("""
    In this section, we explore **regional variations**, **airport rankings**, and how **major global events**
    have shaped air traffic in France. You can filter data by zone, year, and metric to uncover detailed insights.
    """)

    # Sidebar Filters
    st.sidebar.subheader("Deep Dive Filters")
    zones = raw['zone'].unique().tolist()
    selected_zones = st.sidebar.multiselect("Select Zone(s)", zones, default=zones)

    years = sorted(raw['annee'].unique())
    start_year, end_year = st.sidebar.select_slider(
        "Select Year Range",
        options=years,
        value=(years[0], years[-1])
    )

    metrics = ['passengers', 'freight', 'movements']
    selected_metric = st.sidebar.selectbox("Select Metric", metrics, index=0)

    # ---------------------------
    # Regional Comparisons
    # ---------------------------
    st.subheader("Regional Traffic Comparison")
    by_region_table = tables['by_region'].copy()
    by_region_filtered = by_region_table[
        by_region_table['zone'].isin(selected_zones)
    ]

    # Use aggregated columns from prep.py
    metric_col_map = {
        'passengers': 'passengers_total',
        'freight': 'freight_total',
        'movements': 'movements_total'
    }
    metric_col = metric_col_map[selected_metric]
    by_region_filtered['metric_total'] = by_region_filtered[metric_col]

    bar_chart(by_region_filtered.sort_values('metric_total', ascending=False))

    # ---------------------------
    # Airport Distribution
    # ---------------------------
    st.markdown("---")
    st.subheader("Airport Distribution by Selected Metric")
    by_airport_table = tables['by_airport'].copy()
    by_airport_filtered = by_airport_table[
        by_airport_table['zone'].isin(selected_zones)
    ]
    by_airport_filtered['metric_total'] = by_airport_filtered[metric_col]
    top_airports = by_airport_filtered.sort_values('metric_total', ascending=False).head(15)
    bar_chart(top_airports)

    # ---------------------------
    # Major Events Overlay
    # ---------------------------
    st.markdown("---")
    st.subheader("Impact of Major Events on Traffic")
    st.markdown("""
    Key events affecting air traffic:
    - **2001: September 11 attacks**
    - **2008: Global Financial Crisis**
    - **2020: COVID-19 pandemic**
    - **2022: Ukraine war impact on European airspace**
    
    Observe the **traffic trends** across these periods.
    """)

    timeseries_table = tables['timeseries'].copy()
    timeseries_filtered = timeseries_table[
        (timeseries_table['zone'].isin(selected_zones)) &
        (timeseries_table['date'].dt.year >= start_year) &
        (timeseries_table['date'].dt.year <= end_year)
    ]
    timeseries_filtered['metric_total'] = timeseries_filtered[metric_col]
    line_chart(timeseries_filtered, highlight_events=True)

    # ---------------------------
    # Geo Insights
    # ---------------------------
    st.markdown("---")
    st.subheader("Regional Map Insights")
    map_table = tables['geo'].copy()
    map_table_filtered = map_table[
        map_table['zone'].isin(selected_zones)
    ]

    # The geo table already has 'metric_total', no need to compute it
    map_chart(map_table_filtered)


    st.markdown("""
    This deep dive allows users to:
    - Identify **which regions and airports dominate** each metric.  
    - Observe **traffic fluctuations during crises**.  
    - Explore **geographic patterns** and hotspots over time.  

    Use the sidebar filters to **customize your view** and uncover hidden trends in French air traffic.
    """)

    st.markdown("---")
    st.subheader("Zone Composition Over Time")
    stacked_area_chart(timeseries_filtered)
