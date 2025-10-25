import streamlit as st
import pandas as pd

from utils.io import load_apt_processed, load_cie_processed, load_lsn_processed
from utils.prep import (
    prep_apt, prep_cie, prep_lsn,
    agg_apt_timeseries, agg_cie_timeseries, agg_lsn_timeseries
)
from utils.metrics import seasonality_index, cagr, recovery_vs_baseline_year
from utils.viz import (
    line_trend,
    stacked_area_share,
    overlay_projection,
    boxplot_distribution_px,
)

COVID_BANDS = [("2020-03-01", "2021-06-01", "COVID-19")]


@st.cache_data(show_spinner=False)
def _load_trends_data():
    """Load and prepare all three datasets (APT, CIE, LSN)."""
    apt = prep_apt(load_apt_processed())
    cie = prep_cie(load_cie_processed())
    lsn = prep_lsn(load_lsn_processed())
    return apt, cie, lsn


def render(start_date=None, end_date=None):
    st.title("Air Traffic Trends — 1990 to 2024")
    st.caption("Explore how French air traffic changed over time, with simple visuals and key insights.")

    apt, cie, lsn = _load_trends_data()

    
    # Apply global date filter (from app.py)
    
    if start_date and end_date:
        if not apt.empty and "date" in apt.columns:
            apt = apt[(apt["date"] >= start_date) & (apt["date"] <= end_date)]
        if not cie.empty and "date" in cie.columns:
            cie = cie[(cie["date"] >= start_date) & (cie["date"] <= end_date)]
        if not lsn.empty and "date" in lsn.columns:
            lsn = lsn[(lsn["date"] >= start_date) & (lsn["date"] <= end_date)]

    
    # Passengers trend
    
    st.header("Passenger Evolution Over Time")

    if not apt.empty:
        ts_apt = agg_apt_timeseries(apt, freq="M")
        if not ts_apt.empty:
            line_trend(
                ts_apt,
                date_col="date",
                value_cols=["passagers_total"],
                title="Total Passengers (Monthly)",
                subtitle="Red band marks COVID-19 impact.",
                y_title="Passengers",
                bands=COVID_BANDS
            )

            # Recovery and CAGR metrics
            rec_2019 = recovery_vs_baseline_year(apt, "passagers_total", 2019)
            cagr_val = cagr(apt, "passagers_total", start_year=1990, end_year=2024)
            st.markdown(f"**Recovery vs 2019:** {'Not yet' if pd.isna(rec_2019) else f'{rec_2019:.1f}%'}") 
            st.markdown(f"**Compound Annual Growth Rate (1990–2024):** {'Not yet' if pd.isna(cagr_val) else f'{cagr_val * 100:.2f}%'}")


            
            st.markdown("### What if traffic grows in the future?")
            pct = st.slider("Growth scenario (%)", -30, 50, 10)
            overlay_projection(ts_apt, "date", "passagers_total", pct_change=pct)

    
    # Seasonality
    df_month = apt.copy()
    df_month["month"] = pd.to_datetime(df_month["date"], errors = "coerce").dt.month
    st.header("Seasonality of Air Traffic")

    if not apt.empty:
        idx = seasonality_index(apt, "passagers_total")
        if not idx.empty:
            boxplot_distribution_px(
                df_month,
                x_col="month",
                y_col="passagers_total",
                title="Distribution of passengers per month",
                show_points=True,
            )
            st.caption("Months above the average line show higher seasonal peaks (e.g. summer holidays).")

    
    # Airlines share
    
    st.header("Market Share of Airlines")

    if not cie.empty:
        # Aggregate passengers by airline and month
        d = cie.groupby(["date", "cie_nom"], dropna=False)["cie_pax"].sum().reset_index()
        stacked_area_share(
            d,
            date_col="date",
            category_col="cie_nom",
            value_col="cie_pax",
            title="Airlines Market Share Over Time (Top Carriers)",
            normalize=True
        )
        st.caption("This shows how the market share of airlines changes over time. Dominant colors show top players.")

    
    # Freight and Cargo
    
    st.header("Freight and Cargo Movement")

    if not apt.empty:
        ts_freight = agg_apt_timeseries(apt, freq="M")
        if "fret_total" in ts_freight.columns:
            line_trend(
                ts_freight,
                date_col="date",
                value_cols=["fret_total"],
                title="Freight Volume Over Time",
                y_title="Freight (tons)",
                bands=COVID_BANDS
            )
            st.caption("Freight trends help see how cargo traffic behaves differently from passenger flow.")

    
    # Routes growth
    
    st.header("Route Activity Over Time")

    if not lsn.empty:
        ts_lsn = agg_lsn_timeseries(lsn, freq="M")
        if not ts_lsn.empty:
            line_trend(
                ts_lsn,
                date_col="date",
                value_cols=["lsn_pax"],
                title="Total Route Passengers (Monthly)",
                y_title="Passengers",
                bands=COVID_BANDS
            )
            st.caption("Shows the number of passengers flying between airport pairs each month.")

   



if __name__ == "__main__":
    render()
