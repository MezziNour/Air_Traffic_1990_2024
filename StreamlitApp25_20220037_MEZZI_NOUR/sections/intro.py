import streamlit as st

def app():
    st.title("✈️ Evolution of Air Traffic in France (1990–2024)")
    st.markdown("""
    ### Introduction

    Over the past three decades, **air transportation has become a key pillar of mobility and economic activity** in France.  
    This dashboard explores **the evolution of passenger and freight traffic across French airports from 1990 to 2024**, 
    based on open data published by the **Direction Générale de l’Aviation Civile (DGAC)**.

    The aim is to **analyze how traffic has evolved** through major events — such as economic crises, 
    technological progress, and the COVID-19 pandemic — and to highlight **regional differences and long-term trends**.

    ---

    ### The Hook : Crises Seen from Above

    **1990–2024: 30 years of air traffic, and just as many shocks.**  
    From **9/11** and the **2008 financial crisis**, to **COVID-19** and the **war in Ukraine**,  
    this project investigates how these global disruptions are reflected in **France’s air traffic flows**.  
    When the world stops moving, **the skies tell the story**.

    ---

    ### Objectives

    - Examine the **evolution of total passenger and freight traffic** between 1990 and 2024.  
    - Identify the **most active airports and regions** in France.  
    - Explore **the geographical distribution** of air traffic.  
    - Discuss **the impact of disruptions** (e.g., 9/11, 2008 crisis, COVID-19, Ukraine war).  

    ---

    ### Dataset Description

    - **Source:** [data.gouv.fr — DGAC Open Data](https://www.data.gouv.fr/)  
    - **Period covered:** 1990–2024  
    - **Granularity:** Monthly data aggregated by airport and zone  
    - **Key variables:**
        - `code_aeroport` — Airport code  
        - `nom_aeroport` — Airport name  
        - `zone` — Region (Metropolitan or Overseas)  
        - `passagers_depart`, `passagers_arrivee`, `passagers_transit`  
        - `fret_depart`, `fret_arrivee`  
        - `mouvements_passagers`, `mouvements_cargo`  
        - `annee`, `mois`, `ville`, `latitude`, `longitude`  

    ---

    ### Why This Topic Matters

    Understanding air traffic patterns is essential for:
    - **Policy-makers**: planning sustainable mobility and airport infrastructure.  
    - **Economists**: measuring tourism and trade performance.  
    - **Citizens**: observing how mobility evolves through crises.  

    This app offers a **data storytelling approach**, transforming raw data into an interactive narrative 
    that connects numbers with real-world events and implications.

    ---
    """)

