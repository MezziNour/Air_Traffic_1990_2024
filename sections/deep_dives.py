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

    
    # Regional Comparisons
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
    # Dynamic analysis text per metric 
    ANALYSIS = {
        'passengers': {
            'regional': "Passenger traffic is **much higher in MT (4,655,322,719)** than in OM (327,446,950). Mainland airports carry most travellers.",
            'airport': "**Paris–CDG** and **Paris–Orly** dominate. Strong regionals (**Nice, Lyon, Marseille, Toulouse, Bordeaux**) follow.",
            'events': """Traffic dropped after 9/11 (2001), again during the 2008 financial crisis, and reached an all-time low during the COVID-19 pandemic (2020). 
            Recovery started soon after but was slowed by the Ukraine war (2022).""",
            'map': "Activity is **centered on Île-de-France (Paris)** with a second ring along the south/west. OM adds smaller links.",
            'composition': "**MT dominates** passengers over time. **OM** has a small, similar pattern (summer peaks, crisis dips) and recovers after 2020."
        },
        'freight': {
            'regional': "Most air freight is concentrated in Metropolitan France (75,768,091), with only a small share from Overseas territories (3,089,632).",
            'airport': """**Paris–CDG** dominates France’s air freight network by far. 
            It serves as the country’s main cargo hub, followed by Orly, Marseille, and Lyon, which handle smaller volumes. 
            Tourism airports like Nice and Toulouse play a minimal role in freight.""",
            'events': """Freight traffic drops slightly after **2001** and **2008** with a sharper fall in **2020** due to the COVID-19 crisis, but recovers faster than passengers.
            That shows how cargo remains essential even during crises.
            The Ukraine conflict (2022) has a smaller impact but it is visible.""",
            'map': "The map shows that **Ile-de-France (Paris)** is the main freight hub, with some activity in **Marseille**,**Lyon** and **Nice**.",
            'composition': """**Metropolitan France (MT)** clearly dominates freight traffic through all years.
            **Overseas territories (OM)** follow similar ups and downs but remain minor contributors.
            Seasonal variation is less visible than for passengers, and the **2020 drop** stands out with a quick rebound afterward."""
        },
        'movements': {
            'regional': "**Flight movements** are far **higher in MT** (52,592,479); OM shows **fewer but stable** operations (7,273,607).",
            'airport': """**Paris–CDG** records the highest number of movements, followed by **Orly**, **Nice**, and **Lyon**.
            Regional airports like **Marseille**, **Toulouse**, and **Bordeaux** also show strong traffic activity.""",
            'events': """Flight movements dropped after 9/11 (2001) and 2008’s financial crisis, but the COVID-19 pandemic (2020) caused the sharpest decline ever.
            After 2020, there’s a recovery, though traffic hasn’t fully returned to pre-pandemic levels.""",
            'map':"""The **Ile-de-France region (Paris)** stands out clearly, with the highest number of aircraft movements.
            Other active regions include Provence–Alpes–Côte d’Azur, Rhône–Alpes, and Occitanie.
            Overseas territories contribute less but have an important role in connecting territories.""",
            'composition': """**Metropolitan France (MT)** dominates flight movements across all years, while **OM** follow similar ups and downs but remain minor contributors.
            The graph shows seasonal peaks each year, a huge drop in 2020, and a gradual rise afterward."""
        }
    }

    by_region_filtered['metric_total'] = by_region_filtered[metric_col]

    bar_chart(by_region_filtered.sort_values('metric_total', ascending=False))
    st.markdown(f"**Analysis for {selected_metric}:** {ANALYSIS[selected_metric]['regional']}")

    
    # Airport Distribution
    st.markdown("---")
    st.subheader("Airport Distribution by Selected Metric")
    by_airport_table = tables['by_airport'].copy()
    by_airport_filtered = by_airport_table[
        by_airport_table['zone'].isin(selected_zones)
    ]
    by_airport_filtered['metric_total'] = by_airport_filtered[metric_col]
    top_airports = by_airport_filtered.sort_values('metric_total', ascending=False).head(15)
    bar_chart(top_airports)
    st.markdown(f"**Analysis for {selected_metric}:** {ANALYSIS[selected_metric]['airport']}")


    
    # Major Events Overlay
    st.markdown("---")
    st.subheader("Impact of Major Events on Traffic")
    st.markdown("""
    Key events affecting air traffic:
    - **2001: September 11 attacks**
    - **2008: Global Financial Crisis**
    - **2020: COVID-19 pandemic**
    - **2022: Ukraine war impact on European airspace**
    
    You can observe the **traffic trends** across these periods.
    """)

    timeseries_table = tables['timeseries'].copy()
    timeseries_filtered = timeseries_table[
        (timeseries_table['zone'].isin(selected_zones)) &
        (timeseries_table['date'].dt.year >= start_year) &
        (timeseries_table['date'].dt.year <= end_year)
    ]
    timeseries_filtered['metric_total'] = timeseries_filtered[metric_col]
    line_chart(timeseries_filtered, highlight_events=True)
    st.markdown(f"**Analysis for {selected_metric}:** {ANALYSIS[selected_metric]['events']}")

    
    
    # Geo Insights
    st.markdown("---")
    st.subheader("Regional Map Insights")
    st.markdown("""
    This deep dive allows users to:
    - Identify **which regions and airports dominate** each metric.  
    - Observe **traffic fluctuations during crises**.  
    - Explore **geographic patterns** and hotspots over time.  

    You can use the sidebar filters to **customize your view** and uncover hidden trends in French air traffic.
    """)
    map_table = tables['geo'].copy()
    map_table_filtered = map_table[
        map_table['zone'].isin(selected_zones)
    ]
    map_chart(map_table_filtered)
    st.markdown(f"**Analysis for {selected_metric}:** {ANALYSIS[selected_metric]['map']}")

    

    st.markdown("---")
    st.subheader("Zone Composition Over Time")
    stacked_area_chart(timeseries_filtered, value_col=metric_col)
    st.markdown(f"**Analysis for {selected_metric}:**  {ANALYSIS[selected_metric]['composition']}")
