import streamlit as st

def app():
    # App title and main introduction
    st.title("Evolution of Air Traffic in France (1990–2024)")
    
    # Intro text – sets the context and explains what the dashboard is about
    st.markdown("""
    ### Introduction

    Over the last three decades, **air transport has become a major part of mobility and economic activity** in France.  
    This dashboard looks at **how passenger and freight traffic have changed across French airports from 1990 to 2024**,  
    using open data from the **Direction Générale de l’Aviation Civile (DGAC)**.

    The goal is to **understand how air traffic evolved** through key world events — like financial crises, 
    technological progress, and the COVID-19 pandemic — and to show **regional differences and long-term trends**.

    ---

    ### The Hook: Crises Seen from Above

    **1990–2024: 30 years of air traffic, and just as many shocks.**  
    From **9/11** and the **2008 financial crisis**, to **COVID-19** and the **war in Ukraine**,  
    this project explores how these global events appear in **France’s air traffic data**.  
    When the world stops moving, **the skies tell the story**.

    ---

    ### Objectives

    - Follow the **changes in passenger and freight traffic** between 1990 and 2024.  
    - Find out which **airports and regions are the most active**.  
    - Explore **how traffic is spread across the country**.  
    - Understand the **impact of major crises** (9/11, 2008, COVID-19, Ukraine war).  

    ---

    ### Dataset Overview

    - **Source:** [DGAC Open Data](https://www.data.gouv.fr/datasets/trafic-aerien-commercial-mensuel-francais-par-paire-daeroports-par-sens-depuis-1990/)  
    - **Period:** 1990–2024  
    - **Detail level:** Monthly data by airport and region  
    - **Main columns:**
        - `code_aeroport` — Airport code  
        - `nom_aeroport` — Airport name  
        - `zone` — Region (Metropolitan or Overseas)  
        - `passagers_depart`, `passagers_arrivee`, `passagers_transit`  
        - `fret_depart`, `fret_arrivee`  
        - `mouvements_passagers`, `mouvements_cargo`  
        - `annee`, `mois`, `ville`, `latitude`, `longitude`  

    ---

    ### Why This Topic Matters

    Understanding air traffic trends helps:
    - **Policy-makers** plan sustainable airports and transport systems.  
    - **Economists** track tourism, trade, and recovery after crises.  
    - **Everyone** see how mobility reacts when the world changes.  

    This app takes a **data storytelling** approach — turning raw numbers into an interactive story  
    that links data with real-world events and meaning.

    ---
    """)
