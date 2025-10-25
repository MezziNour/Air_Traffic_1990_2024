import streamlit as st
import pandas as pd

from utils.io import load_apt_processed, load_lsn_processed
from utils.prep import prep_apt, prep_lsn
from utils.geo import geo_bundle, to_pydeck_airports
from utils.metrics import kpis_apt
from utils.viz import (
    map_bubbles,
    bar_top_n,
    scatter_with_size_color,
)

@st.cache_data(show_spinner=False)
def _load_airport_data():
    """Load and prepare airport (APT) and route (LSN) datasets."""
    apt = prep_apt(load_apt_processed())
    lsn = prep_lsn(load_lsn_processed())
    return apt, lsn


def render(start_date=None, end_date=None):
    st.title("Airports and Hubs")
    st.caption("Explore the geography of air traffic in France — where are the main hubs and busiest routes?")

    apt, lsn = _load_airport_data()

    
    # Apply global date filter (from app.py)
    if start_date and end_date:
        if not apt.empty and "date" in apt.columns:
            apt = apt[(apt["date"] >= start_date) & (apt["date"] <= end_date)]
        if not lsn.empty and "date" in lsn.columns:
            lsn = lsn[(lsn["date"] >= start_date) & (lsn["date"] <= end_date)]

    
    # Key metrics
    
    st.header("Main Airport Indicators")

    if not apt.empty:
        k_apt = kpis_apt(apt)
        col1, col2, col3 = st.columns([0.5, 1.5, 0.3])
        col1.metric("Total passengers", f"{k_apt.get('total_passengers', 0):,.0f}".replace(",", " "))

        with col2:
            st.markdown(
                f"""
                <div style='text-align:center'>
                    <small style='color:darkblue;'>Top airport</small><br>
                    <span style='font-size:1.8rem; font-weight:700; color:#001F54; white-space:nowrap;'>
                        {k_apt.get("top_airport_name") or k_apt.get("top_airport_code") or "—"}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        rec = k_apt.get("recovery_vs_2019_pct")
        col3.metric("Recovery vs 2019", f"{rec:.1f}%" if rec == rec else "Not yet")

    
    # Airport map
    
    st.header("Map of Airports")

    if not apt.empty:
        apt_map = to_pydeck_airports(apt)
        if not apt_map.empty:
            apt_map["value_label"] = (
                pd.to_numeric(apt_map["value"], errors="coerce")
                .fillna(0)
                .round(0)
                .astype(int)
                .map(lambda x: f"{x:,}".replace(",", " "))
            )

            map_bubbles(
                apt_map,
                lat_col="latitude",
                lon_col="longitude",
                size_col="value",
                tooltip_cols=["nom_aeroport", "value_label"],
                title="Traffic by Airport (Bubble size = passengers)",
                center=(46.5, 2.5),
                zoom=4.5,
                radius_scale=5.0
            )

            st.caption(
                "Bigger circles show airports with higher passenger numbers. "
                "Hover to see airport names and passengers. You can zoom and pan freely."
            )


    
    # Top airports ranking
    
    st.header("Top Airports by Traffic")

    if not apt.empty:
        bar_top_n(
            apt,
            category_col="nom_aeroport",
            value_col="passagers_total",
            n=10,
            title="Top 10 Airports by Passengers"
        )

    
    # Airport activity patterns
    
    st.header("Airport Size vs Freight")
    zones = sorted(apt["zone"].dropna().unique().tolist())
    chosen = st.multiselect("Zones", zones, default=zones)
    apt = apt[apt["zone"].isin(chosen)]

    if not apt.empty and {"fret_total", "passagers_total"}.issubset(apt.columns):
        scatter_with_size_color(
            apt,
            x="passagers_total",
            y="fret_total",
            size_col="passagers_total",
            color_col="zone" if "zone" in apt.columns else None,
            title="Passengers vs Freight per Airport",
            tooltip_cols=["nom_aeroport", "passagers_total", "fret_total", "zone"],
            color_domain=["MT", "OM"],
            color_range=["#3B82F6", "#F59E0B"]
        )
        st.caption("This helps see which airports carry a lot of cargo compared to passengers.")


    
    # Geo summary and hubs
    
    st.header("Geo Insights")

    if not apt.empty:
        g = geo_bundle(apt, lsn)
        if "airport_geo_summary" in g:
            s = g["airport_geo_summary"]
            st.write(f"**Approximate center of traffic:** {s['centroid_lat']:.2f}°, {s['centroid_lon']:.2f}°")
            st.write(f"**Number of airports:** {s['airport_count']}")
        if "avg_route_distance_km" in g:
            st.write(f"**Average route distance:** {g['avg_route_distance_km']:.0f} km")

        if "top_hubs" in g:
            st.markdown("#### Top 10 Hubs by Passenger Volume")
            st.dataframe(
                g["top_hubs"]
                .rename(columns={"passengers": "Passengers", "freight": "Freight (tons)"})[
                    ["code_aeroport", "nom_aeroport", "Passengers", "Freight (tons)"]
                ]
            )

   



if __name__ == "__main__":
    render()
