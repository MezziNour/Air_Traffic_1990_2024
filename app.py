import streamlit as st
import pandas as pd
from utils import io
from PIL import Image
from sections import intro, overview, trends, airports, airlines, routes, quality, conclusions

def display_banner():
    import os
    from pathlib import Path

    # Build the correct absolute path to your image
    image_path = Path(__file__).parent / "assets" / "plane.jpg"

    # Convert it to a URL that Streamlit can read
    if image_path.exists():
        img = Image.open(image_path)
        img = img.resize((1800, 450))
        st.image(img)
        
    else:
        st.warning("Banner image not found.")
# Page setup
st.set_page_config(
    page_title="French Air Traffic — Storytelling Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal CSS
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .stMetric label { font-size: 0.9rem; }
    .stMetric .metric-value { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


# Load processed datasets once

apt_df = io.load_apt_processed()
cie_df = io.load_cie_processed()
lsn_df = io.load_lsn_processed()

def _bounds(df):
    b = io.date_bounds(df)
    return b if b else None

#  Sidebar nav 
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Introduction", "Overview", "Trends", "Airports", "Airlines", "Routes", "Data quality", "Conclusions"],
    index=0,
)

# Page-specific bounds 
def bounds_for_page(page_name: str):
    """Return (min_dt, max_dt) for the active page."""
    if page_name == "Airlines":
        return _bounds(cie_df) or _bounds(apt_df) or _bounds(lsn_df)
    if page_name == "Routes":
        return _bounds(lsn_df) or _bounds(apt_df) or _bounds(cie_df)
    if page_name in ("Airports", "Trends", "Intro"):
        return _bounds(apt_df) or _bounds(cie_df) or _bounds(lsn_df)
    # Quality / Conclusions: use global union
    candidates = [b for b in (_bounds(apt_df), _bounds(cie_df), _bounds(lsn_df)) if b]
    if candidates:
        return (min(b[0] for b in candidates), max(b[1] for b in candidates))
    return None

page_bounds = bounds_for_page(page)

#  Sidebar date slider 
if page_bounds:
    bmin, bmax = page_bounds
    st.sidebar.markdown("### Date range filter")
    date_range = st.sidebar.slider(
        "Select analysis period:",
        min_value=bmin.to_pydatetime().date(),
        max_value=bmax.to_pydatetime().date(),
        value=(bmin.to_pydatetime().date(), bmax.to_pydatetime().date()),
        format="YYYY-MM-DD",
        key=f"date_range_{page}", 
    )
    start_date, end_date = map(pd.to_datetime, date_range)
else:
    start_date = end_date = None

#  Render selected page 
if page == "Introduction":
    display_banner()
    intro.render(start_date, end_date)
elif page == "Overview":
    display_banner()
    overview.render(start_date, end_date)
elif page == "Trends":
    display_banner()
    trends.render(start_date, end_date)
elif page == "Airports":
    display_banner()
    airports.render(start_date, end_date)
elif page == "Airlines":
    display_banner()
    airlines.render(start_date, end_date)
elif page == "Routes":
    display_banner()
    routes.render(start_date, end_date)
elif page == "Data quality":
    display_banner()
    quality.render(start_date, end_date)
elif page == "Conclusions":
    display_banner()
    conclusions.render(start_date, end_date)
else:
    display_banner()
    intro.render(start_date, end_date)

#  Footer 
st.markdown(
    """
<footer style='text-align:center; color:gray; margin-top:50px;'>
© 2025 — Nour MEZZI - Data Storytelling Dashboard | Source:
<a href="https://www.data.gouv.fr/datasets/trafic-aerien-commercial-mensuel-francais-par-paire-daeroports-par-sens-depuis-1990/" target="_blank">DGAC Open Data</a>
</footer>
""",
    unsafe_allow_html=True,
)
