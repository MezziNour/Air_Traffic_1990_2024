import streamlit as st

def app():
    st.title("Evolution of Air Traffic in France (1990–2024)")

    st.markdown("""
    ### Introduction

    Over the past 30 years, **air travel has become a key part of mobility and the economy** in France.  
    This dashboard shows **how passenger and freight traffic changed in French airports from 1990 to 2024**,  
    using open data from the **Direction Générale de l’Aviation Civile (DGAC)**.

    The goal is to **see how air traffic evolved** through major world events — such as financial crises,  
    new technologies, and the COVID-19 pandemic — and to highlight **regional differences and long-term trends**.

    ---

    ### Crises seen from above

    **1990–2024: 30 years of air traffic, full of ups and downs.**  
    From **9/11** and the **2008 financial crisis** to **COVID-19** and the **war in Ukraine**,  
    this project shows how these world events are reflected in **France’s air traffic data**.  
    When the world slows down, **the skies tell the story**.

    ---

    ### Objectives

    - Track how **passenger and freight traffic** changed between 1990 and 2024  
    - Identify the **most active airports and regions**  
    - Visualize **how traffic is spread across France**  
    - Analyze the **impact of major crises** (9/11, 2008, COVID-19, Ukraine war)  

    ---

    ### About the Dataset

    - **Source:** [DGAC Open Data](https://www.data.gouv.fr/datasets/trafic-aerien-commercial-mensuel-francais-par-paire-daeroports-par-sens-depuis-1990/)  
    - **Period covered:** 1990–2024  
    - **Level of detail:** Monthly data by airport and region  
    - **Main columns:**
        - `code_aeroport` — Airport code  
        - `nom_aeroport` — Airport name  
        - `zone` — Region (Metropolitan or Overseas)  
        - `passagers_depart`, `passagers_arrivee`, `passagers_transit`  
        - `fret_depart`, `fret_arrivee`  
        - `mouvements_passagers`, `mouvements_cargo`  
        - `annee`, `mois`, `ville`, `latitude`, `longitude`  

    ---

    ### Why it matters

    Studying air traffic helps:
    - **Policy makers** plan for more sustainable airports and transport systems  
    - **Economists** measure tourism, trade, and recovery after crises  
    - **Citizens** understand how global events affect daily mobility  
    ---
    """)
