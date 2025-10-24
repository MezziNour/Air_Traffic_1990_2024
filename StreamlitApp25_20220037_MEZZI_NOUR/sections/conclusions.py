import streamlit as st

def app():
    st.header("🏁 Conclusions & Key Takeaways")

    st.markdown("""
    After exploring **30+ years of air traffic data across French airports**, several key insights emerge:

    ---

    ### 1️⃣ Long-Term Trends
    - Air traffic in France has generally **increased steadily** from 1990 until the COVID-19 pandemic in 2020.  
    - Passenger traffic dominates the overall movement numbers, with freight representing a smaller but **essential component of airport activity**.  
    - Certain airports (Paris Charles de Gaulle, Orly, Lyon, Nice) consistently serve as **major hubs**.

    ---

    ### 2️⃣ Impact of Major Crises
    - **9/11 (2001)**: Temporary drop in international traffic.  
    - **2008 Financial Crisis**: Slower growth in passenger movements.  
    - **COVID-19 (2020)**: Massive drop across all airports; recovery varies by region.  
    - **Ukraine War (2022)**: Slight reduction in international air traffic, mostly in freight and transit passengers.  
    - The skies reflect the rhythm of global and regional disruptions — a **“crises seen from above”** perspective.

    ---

    ### 3️⃣ Regional & Airport Insights
    - **Metropolitan France** dominates total traffic; Overseas territories see smaller volumes but are crucial for connectivity.  
    - Top airports account for a **large share of total traffic**, reinforcing the hub-and-spoke structure of air transport.  
    - Regional differences suggest **targeted infrastructure or policy interventions** may be required to balance traffic growth and sustainability.

    ---

    ### 4️⃣ Recommendations & Next Steps
    - **Policy & Planning**: Use this data to plan airport capacity, regional connectivity, and crisis response strategies.  
    - **Further Analysis**: Explore **seasonal trends, weather impacts, or airline-specific contributions**.  
    - **Scenario Planning**: Incorporate **“what-if” scenarios** for future disruptions or policy changes.  
    - **Sustainability Focus**: Integrate environmental metrics (CO₂, noise, fuel consumption) for holistic mobility planning.

    ---

    ### 5️⃣ Dashboard Takeaways
    - Interactive filters allow users to **explore traffic by zone, year, and metric**.  
    - Visual storytelling highlights **trends, disruptions, and geographic patterns**.  
    - Provides a **transparent and reproducible data narrative** linking numbers to real-world events.
    
    ---
    
    Thank you for exploring this dashboard. For further details, all datasets, methods, and code are **documented in the repository**.
    """)
