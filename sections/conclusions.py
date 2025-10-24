import streamlit as st

def app():
    st.header("Conclusions & Key Takeaways")

    st.markdown("""
    After looking at **air traffic in France from 1990 to 2024**, we can see how travel, freight, and flight activity have changed over time.

    ---

    ### What We Learned
    - From **1990 to 2019**, air traffic in France kept **growing consistently**, with clear **summer peaks** every year.  
      In **2020**, traffic fell sharply because of **COVID-19**, then started to recover slowly.
    - **Metropolitan France (MT)** handles **most of the traffic**, while **Overseas territories (OM)** show **smaller but stable** numbers.  
    - **Paris–Charles de Gaulle (CDG)** and **Paris–Orly (ORY)** remain the main hubs.  
      Airports like **Nice, Lyon, Marseille, Toulouse, and Bordeaux** also play an important role regionally.
    - **Freight traffic** is mostly at **CDG**, making it France’s main cargo hub.  
      It was less affected by crises and recovered faster than passenger traffic.
    - **Flight movements** clearly dropped during COVID-19 but show a strong rebound after 2021.
    - Global events such as **9/11 (2001)**, the **2008 financial crisis**, and the **2020 pandemic** left visible marks in the data.

    ---

    ### Why It Matters
    - Big events can **disrupt the air network fast**, so **resilience and crisis planning** are essential.  
    - Heavy traffic around **Paris airports** shows a need to **spread activity** more evenly across regions.  
    - **Regional airports** help connect cities and support tourism, so keeping them active is important for local economies.  
    - With most **freight centered in Ile-de-France**, improving **logistics links** to other regions could make air transport more balanced.  
    - Environmental issues are now a key part of planning — reducing **CO₂ emissions and noise** should go hand in hand with growth.

    ---

    ### What Comes Next  
    - **Predict the future**: we can try simple forecasting models to estimate how traffic might evolve after crises.  
    - **Add new data**: we can include information on **emissions, fuel use, and train alternatives** for short routes.  
    - **Improve the app**: we can offer options to **download filtered data**, **compare airports**, and show **data quality checks**.

    ---

    Thank you for exploring this dashboard!  
    All data sources and methods are explained in the **[project repository](https://github.com/MezziNour/Air_Traffic_1990_2024)**.
    """)
