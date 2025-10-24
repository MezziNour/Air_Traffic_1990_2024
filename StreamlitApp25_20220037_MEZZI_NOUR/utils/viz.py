import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk


# Line Chart – Time Series View
def line_chart(df, highlight_events=False):
    """
    Show how traffic evolves over time.
    If highlight_events=True, adds red lines for key historical events.
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

    # Add key global events on the chart
    if highlight_events:
        events = {
            '2001-09-01': '9/11 Attacks',
            '2008-09-01': 'Financial Crisis',
            '2020-03-01': 'COVID-19 Pandemic',
            '2022-02-24': 'Ukraine War'
        }
        for date, label in events.items():
            fig.add_vline(x=pd.to_datetime(date), line_dash="dash", line_color="red")
            fig.add_annotation(
                x=pd.to_datetime(date),
                y=df['metric_total'].max() * 0.95,
                text=label,
                showarrow=True,
                arrowhead=2,
                arrowcolor='red'
            )

    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)



# Bar Chart – Ranking Comparison
def bar_chart(df, top_n=10):
    """
    Show top airports or regions by selected metric.
    """
    if df.empty:
        st.warning("No data to display for bar chart.")
        return

    # Compute total metric if missing
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


# Map Chart – Geographic View
def map_chart(df):
    """
    Show the geographic spread of air traffic.
    Needs columns: 'nom_aeroport', 'latitude', 'longitude', 'metric_total'.
    """
    # Remove airports with missing coordinates
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Make sure coordinates are numbers
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    
    if df.empty:
        st.info("No data or coordinates to display on the map.")
        return

    # France center (used to center the map)
    center_lat = 46.6
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
        zoom=5,
        height=600,
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    st.plotly_chart(fig, use_container_width=True)


# Summary Table – Top Results
def summary_table(df, metric='metric_total', top_n=10):
    """
    Show a simple table of top airports or regions.
    """
    if df.empty:
        st.warning("No data to display in summary table.")
        return

    if metric not in df.columns:
        df[metric] = df.select_dtypes(include='number').sum(axis=1)

    top_df = df.sort_values(metric, ascending=False).head(top_n)
    st.dataframe(top_df[['nom_aeroport', 'zone', metric]] if 'nom_aeroport' in df.columns else top_df)



# Small Multiples – Compare Groups
def small_multiples(df, value_col='metric_total', category_col='zone'):
    """
    Create a faceted bar chart to compare different zones or airports over time.
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



# Seasonal Heatmap – Monthly Patterns
def seasonality_heatmap(df):
    """
    Show how passenger traffic changes by month and year (seasonal trends).
    """
    if df.empty:
        st.warning("No data available to generate seasonality heatmap.")
        return

    # Create passengers_total if missing
    if 'passengers_total' not in df.columns:
        if all(col in df.columns for col in ['passagers_depart', 'passagers_arrivee', 'passagers_transit']):
            df['passengers_total'] = df[['passagers_depart', 'passagers_arrivee', 'passagers_transit']].sum(axis=1)
        else:
            st.error("Required passenger columns are missing.")
            return

    # Make sure we have year and month columns
    if 'annee' not in df.columns or 'mois' not in df.columns:
        st.error("Columns 'annee' and 'mois' are required for the heatmap.")
        return

    # Group by year and month
    pivot_df = (
        df.groupby(['annee', 'mois'], as_index=False)['passengers_total']
        .sum()
        .pivot(index='annee', columns='mois', values='passengers_total')
        .fillna(0)
    )

    # Month labels for the x-axis
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_df.columns = month_labels[:len(pivot_df.columns)]

    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="Year", color="Passengers"),
        color_continuous_scale="YlOrBr",
        title="Seasonal Heatmap of Passenger Traffic (1990–2024)"
    )

    fig.update_xaxes(side="top")
    st.plotly_chart(fig, use_container_width=True)



# Stacked Area Chart – Zone Composition
def stacked_area_chart(df):
    """
    Show how each zone contributes to total traffic over time.
    """
    if df.empty or not {'date', 'zone', 'metric_total'}.issubset(df.columns):
        st.warning("No sufficient data to generate stacked area chart.")
        return

    # Sort by date for a cleaner timeline
    df = df.sort_values('date')

    fig = px.area(
        df,
        x='date',
        y='metric_total',
        color='zone',
        title="Traffic Composition by Zone Over Time",
        labels={'metric_total': 'Total Traffic', 'zone': 'Region'},
    )

    fig.update_layout(
        hovermode="x unified",
        legend_title_text='Zone',
        yaxis_title="Total Passengers",
        xaxis_title="Date",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
