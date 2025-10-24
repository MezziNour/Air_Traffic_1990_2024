import streamlit as st
from utils.io_utils import load_cleaned_data
from utils.prep import make_tables
from sections import intro, overview, deep_dives, conclusions


def display_banner():
    import os
    from pathlib import Path

    # Build the correct absolute path to your image
    image_path = Path(__file__).parent / "assets" / "plane.jpg"

    # Convert it to a URL that Streamlit can read
    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.warning("Banner image not found. Check the path in display_banner().")


st.set_page_config(
    page_title="Air Traffic Data Storytelling Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load Data
@st.cache_data(show_spinner=False)
def get_data():
    df_cleaned = load_cleaned_data()
    tables = make_tables(df_cleaned)
    return df_cleaned, tables

df_cleaned, tables = get_data()


# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ("Introduction", "Overview", "Deep Dives", "Conclusions")
)


# Display Selected Section
if page == "Introduction":
    display_banner()
    intro.app()
elif page == "Overview":
    display_banner()
    overview.app(tables, df_cleaned)
elif page == "Deep Dives":
    display_banner()
    deep_dives.app(tables, df_cleaned)
elif page == "Conclusions":
    display_banner()
    conclusions.app()



# Footer
st.markdown("""
<footer style='text-align:center; color:gray; margin-top:50px;'>
© 2025 — Nour MEZZI - Data Storytelling Dashboard | Source: <a href="https://www.data.gouv.fr/datasets/trafic-aerien-commercial-mensuel-francais-par-paire-daeroports-par-sens-depuis-1990/" target="_blank">DGAC Open Data</a>
</footer>
""", unsafe_allow_html=True)
