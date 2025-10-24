import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# -----------------------------
# Line Chart for Time Series
# -----------------------------
def line_chart(df, highlight_events=False):
    """
    Interactive line chart for passenger, freight, or movements over time.
    highlight_events=True adds vertical lines for major events.
    """
    if df.empty:
        st.warning("No data to display for line chart.")
        return

    fig = px.line(
        df,
        x='date',
        y='metric_total',
        color='zone' if 'zone' in df.columns else None,
        labels={'date': 'Date', 'metric_total': 'Metric Value', 'zone': 'Zone'},
        title='Traffic Trend Over Time'
    )

    # Highlight major events
    if highlight_events:
        events = {
            '2001-09-01': '9/11 Attacks',
            '2008-09-01': 'Financial Crisis',
            '2020-03-01': 'COVID-19 Pandemic',
            '2022-02-24': 'Ukraine War'
        }
        for date, label in events.items():
            fig.add_vline(x=pd.to_datetime(date), line_dash="dash", line_color="red")
            fig.add_annotation(x=pd.to_datetime(date), y=df['metric_total'].max()*0.95,
                               text=label, showarrow=True, arrowhead=2, arrowcolor='red')

    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Bar Chart for Comparison
# -----------------------------
def bar_chart(df, top_n=10):
    """
    Bar chart to show top airports or regions based on a metric.
    """
    if df.empty:
        st.warning("No data to display for bar chart.")
        return

    # If metric_total not precomputed
    if 'metric_total' not in df.columns:
        df['metric_total'] = df.select_dtypes(include='number').sum(axis=1)

    top_df = df.sort_values('metric_total', ascending=False).head(top_n)
    fig = px.bar(
        top_df,
        x='nom_aeroport' if 'nom_aeroport' in df.columns else 'zone',
        y='metric_total',
        color='zone' if 'zone' in df.columns else None,
        labels={'metric_total': 'Metric Value', 'nom_aeroport': 'Airport', 'zone': 'Zone'},
        text='metric_total',
        title=f"Top {top_n} by Selected Metric"
    )
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Map Chart for Geo Visualization
# -----------------------------
import streamlit as st
import plotly.express as px

def map_chart(df):
    """
    Display geographic distribution of air traffic.
    Expects df with columns: 'nom_aeroport', 'latitude', 'longitude', 'metric_total'.
    """
    # Drop rows with missing coordinates
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Ensure numeric types
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    
    if df.empty:
        st.info("No data or coordinates to display on the map.")
        return

    # Compute map center: France coordinates or mean of df
    center_lat = 46.6  # approximate center of France
    center_lon = 2.5

    fig = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        size='metric_total',
        hover_name='nom_aeroport',
        hover_data={'zone': True, 'metric_total': True, 'latitude': False, 'longitude': False},
        color='metric_total',
        color_continuous_scale='Viridis',
        zoom=5,  # adjusted zoom to show whole France
        height=600,
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin={"r":0,"t":0,"l":0,"b":0},
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Static Summary Table
# -----------------------------
def summary_table(df, metric='metric_total', top_n=10):
    """
    Display a static table with top N airports or regions.
    """
    if df.empty:
        st.warning("No data to display in summary table.")
        return
    if metric not in df.columns:
        df[metric] = df.select_dtypes(include='number').sum(axis=1)
    top_df = df.sort_values(metric, ascending=False).head(top_n)
    st.dataframe(top_df[['nom_aeroport', 'zone', metric]] if 'nom_aeroport' in df.columns else top_df)


# -----------------------------
# Small Multiples for Comparison
# -----------------------------
def small_multiples(df, value_col='metric_total', category_col='zone'):
    """
    Generates a faceted bar chart for comparing zones or airports across time.
    """
    if df.empty or value_col not in df.columns:
        st.warning("No data to display for small multiples.")
        return

    fig = px.bar(
        df,
        x='annee_mois' if 'annee_mois' in df.columns else 'annee',
        y=value_col,
        color=category_col if category_col in df.columns else None,
        facet_col=category_col if category_col in df.columns else None,
        labels={value_col: 'Metric Value', 'annee_mois': 'Date'},
        title="Small Multiples Comparison"
    )
    fig.update_layout(showlegend=True, height=400)
    st.plotly_chart(fig, use_container_width=True)
