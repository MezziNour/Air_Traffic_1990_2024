import streamlit as st
import pandas as pd

from utils.io import load_cie_processed
from utils.prep import prep_cie, agg_cie_timeseries
from utils.metrics import (
    kpis_cie, hhi_concentration, topn_share, cagr, recovery_vs_baseline_year
)
from utils.viz import (
    stacked_area_share,
    line_trend,
    bar_top_n,
    scatter_with_size_color,
)

COVID_BANDS = [("2020-03-01", "2021-06-01", "COVID-19")]


@st.cache_data(show_spinner=False)
def _load_airline_data():
    """Load and prepare airline (CIE) dataset."""
    cie = prep_cie(load_cie_processed())
    return cie


def render(start_date=None, end_date=None):
    st.title("Airlines and Market Dynamics")
    st.caption("See how airlines changed over time, which companies lead, and how competition looks today.")

    cie = _load_airline_data()

    # Apply global date filter (from app.py)
    if start_date and end_date and "date" in cie.columns:
        cie = cie[(cie["date"] >= start_date) & (cie["date"] <= end_date)]


    # Airline KPIs
   
    st.header("Main Airline Numbers")

    if not cie.empty:
        k_cie = kpis_cie(cie)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total passengers", f"{k_cie.get('total_airline_passengers', 0):,.0f}".replace(",", " "))
        col2.metric("Top airline", k_cie.get("top_airline_name") or k_cie.get("top_airline_code") or "—")
        rec = k_cie.get("recovery_vs_2019_pct")
        col3.metric("Recovery vs 2019", f"{rec:.1f}%" if rec == rec else "—")


    # Airlines over time
    st.header("Passenger Trend Over Time")

    if not cie.empty:
        ts_cie = agg_cie_timeseries(cie, freq="M")
        if not ts_cie.empty:
            line_trend(
                ts_cie,
                date_col="date",
                value_cols=["cie_pax"],
                title="Total Passengers Carried by Airlines (Monthly)",
                subtitle="Red band marks COVID-19 period.",
                y_title="Passengers",
                bands=COVID_BANDS,
            )
            rec_2019 = recovery_vs_baseline_year(cie, "cie_pax", 2019)
            cagr_val = cagr(cie, "cie_pax", start_year=2010, end_year=2024)
            st.markdown(f"**Recovery vs 2019:** {rec_2019:.1f}%")
            st.markdown(f"**Compound Annual Growth Rate (2010–2024):** {cagr_val * 100:.2f}%")

    
    # Market share dynamics
    st.header("Market Share of Airlines (Top 16)")

    if not cie.empty:
        df_share = cie.groupby(["date", "cie_nom"], dropna=False)["cie_pax"].sum().reset_index()
        stacked_area_share(
            df_share,
            date_col="date",
            category_col="cie_nom",
            value_col="cie_pax",
            title="Airlines Market Share Over Time (Top Carriers)",
            normalize=True,
        )
        st.caption("Each color shows an airline's market share. Dominant colors mean leading airlines.")

    
    # Top airlines
    st.header("Top Airlines by Total Passengers")

    if not cie.empty:
        bar_top_n(
            cie,
            category_col="cie_nom",
            value_col="cie_pax",
            n=10,
            title="Top 10 Airlines by Passengers",
        )

    
    # Airline efficiency and concentration
    st.header("Airline Performance and Competition")

    if not cie.empty:
        if {"cie_pkt", "cie_vol"}.issubset(cie.columns):
            scatter_with_size_color(
                cie,
                x="cie_vol",
                y="cie_pkt",
                size_col="cie_pax",
                color_col="cie_nom",
                title="Flights vs Passenger-Kilometers per Airline",
                tooltip_cols=["cie_nom", "cie_vol", "cie_pkt", "cie_pax"]
            )
            st.caption("Shows how passenger output (pkt) compares with number of flights — bigger dots = more passengers.")

        # Concentration metrics
        hhi_val = hhi_concentration(cie, "cie_nom", "cie_pax")
        top3_share = topn_share(cie, "cie_nom", "cie_pax", 3)
        st.markdown(f"**Market concentration (HHI):** {hhi_val:.3f}")
        st.markdown(f"**Top 3 airlines' combined share:** {top3_share * 100:.1f}%")

        st.caption("Higher HHI means less competition. A large top-3 share means a few airlines dominate the market.")



if __name__ == "__main__":
    render()
