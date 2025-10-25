import streamlit as st
import pandas as pd

from utils.io import load_apt_processed, load_cie_processed, load_lsn_processed
from utils.prep import prep_apt, prep_cie, prep_lsn, agg_apt_timeseries
from utils.metrics import kpis_apt, kpis_cie, kpis_lsn
from utils.viz import line_trend, missingness_bar

COVID_BANDS = [("2019-12-01", "2021-05-01", "COVID-19")]

@st.cache_data(show_spinner=False)
def _load_all():
    """Load preprocessed datasets (clean and fast)."""
    apt = prep_apt(load_apt_processed())
    cie = prep_cie(load_cie_processed())
    lsn = prep_lsn(load_lsn_processed())
    return apt, cie, lsn

def render(start_date=None, end_date=None):
    st.title("Overview")
    st.caption("A fast view: KPIs, main trend, and quick facts. Filters from the sidebar are applied.")

    # Load
    apt, cie, lsn = _load_all()

    # Apply global date filter (from app.py)
    if start_date is not None and end_date is not None:
        if not apt.empty and "date" in apt.columns:
            apt = apt[(apt["date"] >= start_date) & (apt["date"] <= end_date)]
        if not cie.empty and "date" in cie.columns:
            cie = cie[(cie["date"] >= start_date) & (cie["date"] <= end_date)]
        if not lsn.empty and "date" in lsn.columns:
            lsn = lsn[(lsn["date"] >= start_date) & (lsn["date"] <= end_date)]

    
    # KPIs
    
    col1, col2, col3 = st.columns([0.5, 1.5, 0.3])

    if not apt.empty:
        k_apt = kpis_apt(apt)
        col1.metric(
            "Total passengers",
            f"{k_apt.get('total_passengers', 0):,.0f}".replace(",", " ")
        )

        with col2:
            st.markdown(
                f"""
                <div style='text-align:center'>
                    <small style='color:#0a2a66;'>Top airport</small><br>
                    <span style='font-size:1.8rem; font-weight:700; color:#001F54; white-space:nowrap;'>
                        {k_apt.get("top_airport_name") or k_apt.get("top_airport_code") or "—"}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        rec = k_apt.get("recovery_vs_2019_pct")
        col3.metric("Recovery vs 2019", f"{rec:.1f}%" if rec == rec else "Not yet")

    
    # Main time series
    
    if not apt.empty:
        ts_apt_M = agg_apt_timeseries(apt, freq="M")
        if not ts_apt_M.empty:
            line_trend(
                ts_apt_M,
                date_col="date",
                value_cols=["passagers_total"],
                title="Passengers over time",
                subtitle="Monthly totals. The red band marks the COVID-19 period.",
                y_title="Passengers",
                bands=COVID_BANDS
            )

    
    # Quick facts
    
    if not cie.empty:
        k_cie = kpis_cie(cie)
        with st.expander("Airlines — quick facts", expanded=False):
            st.write(
                f"Total airline passengers: **{k_cie.get('total_airline_passengers', 0):,.0f}**"
                .replace(",", " ")
            )
            st.write("Top airline:", k_cie.get("top_airline_name") or k_cie.get("top_airline_code") or "—")

    if not lsn.empty:
        k_lsn = kpis_lsn(lsn)
        with st.expander("Routes — quick facts", expanded=False):
            st.write(
                f"Total route passengers: **{k_lsn.get('total_route_passengers', 0):,.0f}**"
                .replace(",", " ")
            )
            st.write("Top route:", k_lsn.get("top_route") or "—")

    
    # Data quality preview
    
    st.markdown("### Data quality (quick view)")
    if not apt.empty:
        st.caption("Missing values in APT (airports)")
        missingness_bar(apt, title="APT missing values")

    if not cie.empty:
        st.caption("Missing values in CIE (airlines)")
        missingness_bar(cie, title="CIE missing values")

    if not lsn.empty:
        st.caption("Missing values in LSN (routes)")
        missingness_bar(lsn, title="LSN missing values")


if __name__ == "__main__":
    render()
