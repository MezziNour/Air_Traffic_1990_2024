import streamlit as st
import pandas as pd
from utils.io import load_lsn_processed, load_apt_processed
from utils.prep import prep_lsn, prep_apt, agg_lsn_timeseries
from utils.metrics import kpis_lsn, cagr, recovery_vs_baseline_year
from utils.viz import (
    line_trend,
    bar_top_n,
)

COVID_BANDS = [("2020-03-01", "2021-06-01", "COVID-19")]


@st.cache_data(show_spinner=False)
def _load_route_data():
    """Load and prepare LSN (routes) and APT (airports) datasets."""
    lsn = prep_lsn(load_lsn_processed())
    apt = prep_apt(load_apt_processed())
    return lsn, apt


def render(start_date=None, end_date=None):
    st.title("Routes and Air Network")
    st.caption("Explore how French air routes evolved — busiest connections, distances, and total flows.")

    lsn, apt = _load_route_data()

    
    # Apply global date filter (from app.py)
    
    if start_date and end_date:
        if not lsn.empty and "date" in lsn.columns:
            lsn = lsn[(lsn["date"] >= start_date) & (lsn["date"] <= end_date)]
        if not apt.empty and "date" in apt.columns:
            apt = apt[(apt["date"] >= start_date) & (apt["date"] <= end_date)]

    
    # Key route metrics
    
    st.header("Main Route Indicators")

    if not lsn.empty:
        k_lsn = kpis_lsn(lsn)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total passengers", f"{k_lsn.get('total_route_passengers', 0):,.0f}".replace(",", " "))
        col2.metric("Top route", k_lsn.get("top_route") or "—")
        rec = k_lsn.get("recovery_vs_2019_pct")
        col3.metric("Recovery vs 2019", f"{rec:.1f}%" if rec == rec else "—")

    
    # Route trend over time
    
    st.header("Total Route Passengers Over Time")

    if not lsn.empty:
        ts_lsn = agg_lsn_timeseries(lsn, freq="M")
        if not ts_lsn.empty:
            line_trend(
                ts_lsn,
                date_col="date",
                value_cols=["lsn_pax"],
                title="Total Route Passengers (Monthly)",
                subtitle="Red band marks COVID-19 period.",
                y_title="Passengers",
                bands=COVID_BANDS
            )

            rec_2019 = recovery_vs_baseline_year(lsn, "lsn_pax", 2019)
            cagr_val = cagr(lsn, "lsn_pax", start_year=1990, end_year=2024)
            st.markdown(f"**Compound Annual Growth Rate (1990–2024):** {cagr_val * 100:.2f}%")

    
    # Top routes
    
    st.header("Busiest Routes")

    if not lsn.empty:
        route_key = "route_pair" if "route_pair" in lsn.columns else (
            "route_dir" if "route_dir" in lsn.columns else "lsn_seg"
        )
        bar_top_n(
            lsn,
            category_col=route_key,
            value_col="lsn_pax",
            n=10,
            title="Top 10 Busiest Routes (by Passengers)"
        )
        st.caption("Each bar shows one connection between two airports. The higher the bar, the busier the route.")

    
if __name__ == "__main__":
    render()
