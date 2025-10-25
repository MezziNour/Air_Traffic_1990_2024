# sections/conclusions.py

import streamlit as st
import pandas as pd

from utils.io import load_apt_processed, load_cie_processed, load_lsn_processed
from utils.prep import prep_apt, prep_cie, prep_lsn
from utils.metrics import kpis_apt, kpis_cie, kpis_lsn


@st.cache_data(show_spinner=False)
def _load_all():
    """Load & prep all three processed datasets."""
    apt = prep_apt(load_apt_processed())
    cie = prep_cie(load_cie_processed())
    lsn = prep_lsn(load_lsn_processed())
    return apt, cie, lsn


def _apply_range(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    if df.empty or "date" not in df.columns or start_date is None or end_date is None:
        return df
    m = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
    return df.loc[m].copy()


def _cagr_yearly(df: pd.DataFrame, value_col: str = "passagers_total") -> float:
    """
    Rough CAGR on yearly totals (handles gaps).
    Returns a percent (e.g. 3.1 for 3.1%).
    """
    if df.empty or "date" not in df.columns or value_col not in df.columns:
        return float("nan")
    y = (
        df.dropna(subset=["date"])
          .assign(year=lambda x: x["date"].dt.year)
          .groupby("year", dropna=False)[value_col]
          .sum()
          .sort_index()
    )
    if len(y) < 2 or y.iloc[0] <= 0:
        return float("nan")
    years = y.index[-1] - y.index[0]
    if years <= 0:
        return float("nan")
    cagr = (y.iloc[-1] / y.iloc[0]) ** (1 / years) - 1
    return round(cagr * 100, 2)


def render(start_date=None, end_date=None):
    st.title("Conclusions & Next Steps")
    st.caption("A short wrap-up of what the data shows — and what to do with it.")

    # Load & filter
    apt, cie, lsn = _load_all()
    apt = _apply_range(apt, start_date, end_date)
    cie = _apply_range(cie, start_date, end_date)
    lsn = _apply_range(lsn, start_date, end_date)

    #  Key numbers (from your visuals) 
    st.header("Key takeaways")

    c1, c2, c3 = st.columns([0.5, 1, 0.3])
    if not apt.empty:
        k_apt = kpis_apt(apt)
        c1.metric("Total passengers (APT)", f"{k_apt.get('total_passengers', 0):,.0f}".replace(",", " "))
        c2.metric("Top airport", k_apt.get("top_airport_name") or k_apt.get("top_airport_code") or "—")
        rec = k_apt.get("recovery_vs_2019_pct")
        c3.metric("Recovery vs 2019", f"{rec:.1f}%" if rec == rec else "Not yet")

    if not cie.empty:
        k_cie = kpis_cie(cie)
        st.caption(
            f"**Airlines:** {k_cie.get('total_airline_passengers', 0):,.0f}".replace(",", " ")
            + f" passengers • Leader: {k_cie.get('top_airline_name') or k_cie.get('top_airline_code') or '—'}"
        )

    if not lsn.empty:
        k_lsn = kpis_lsn(lsn)
        st.caption(
            f"**Routes:** {k_lsn.get('total_route_passengers', 0):,.0f}".replace(",", " ")
            + f" passengers • Busiest route: {k_lsn.get('top_route') or '—'}"
        )

    # CAGR from airports series (1990→latest) inside the selected range
    cagr = _cagr_yearly(apt, "passagers_total") if not apt.empty else float("nan")
    if cagr == cagr:  # not NaN
        st.caption(f"Approx. long-run growth: **{cagr}% CAGR** on yearly passenger totals.")

    st.markdown("---")

    #  Plain-language insights 
    st.header("What the charts tell us")

    st.markdown(
        """
        - **Strong seasonality :** peaks happen every summer, Winters are lower.  
        - **COVID-19 was a deep shock, then a fast rebound :** traffic fell hard in 2020 and climbed back near 2019 levels soon after.  
        - **France is hub-centric :** Paris–Charles de Gaulle and Paris–Orly carry a very large share of flows; Nice, Lyon, Marseille follow.  
        - **Air France leads, low-cost carriers matter :** Air France stays number one, while EasyJet brands and others hold a large slice of demand.  
        - **Short/medium-haul dominates :** many passengers fly within France or to nearby countries; long-haul is important but smaller.  
        - **Freight is stable :** cargo dipped during COVID but overall shows smaller swings than passengers.
        """
    )

    st.markdown("---")

    #  Why it matters / implications 
    st.header("What this means")

    st.markdown(
        """
          - **Resilience:** the market absorbs shocks and returns to trend. Planning should allow for quick ramp-downs and ramp-ups.  
          - **Concentration risk:** Paris hubs are efficient but also single points of failure. Regional capacity and rail links help reduce risk.  
          - **Competitive pressure:** legacy + low-cost mix keeps prices and load factors tight; efficiency and punctuality remain key levers.  
          - **Sustainability pressure:** most flights are short-haul, where CO₂ per trip is more visible; greener operations and modal shift will be in focus.
        """
    )

    st.markdown("---")

    #  Data quality (from your checks) 
    st.header("Data quality ")
    st.success("All expected columns found. No duplicates, no missing values, no IQR outliers detected in APT / CIE / LSN.")

    st.markdown("---")

    #  Next steps 
    st.header("Next steps")

    st.markdown(
        """
        1) **Add emissions** — estimate CO₂ per route/aircraft to compare airports and airlines on climate impact.  
        2) **Blend modes** — combine air with **TGV/rail** to study real door-to-door travel and substitution on short routes.  
        3) **Forecast demand** — simple models (seasonal ARIMA/Prophet) at airport, airline, and route level for 12–24-month outlooks.  
        4) **Stress tests** — simulate new shocks (oil price, ATC strike, extreme weather) to see which hubs/routes are most exposed.  
        5) **Automate refresh** — monthly ingestion from DGAC with validation, then publish an **open dashboard** for cities and regions.  
        """
    )

    st.markdown("---")
    st.success("**In short:** French air traffic grew over the long run, fell sharply in 2020, and has almost fully recovered. "
               "Paris anchors the network, Air France leads, and low-cost carriers play a big role. "
               "The next chapter would be about climate performance.")
    


if __name__ == "__main__":
    render()
