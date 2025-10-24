import pandas as pd
import streamlit as st
import os

# Folder where processed data is stored
DATA_DIR = os.path.join("data", "processed")

def get_cleaned_file_path(filename="trafic_aerien_1990_2024_cleaned.csv"):
    """Build and return the full path to the cleaned CSV file."""
    return os.path.join(DATA_DIR, filename)

@st.cache_data(show_spinner=False)
def load_cleaned_data(filename="trafic_aerien_1990_2024_cleaned.csv"):
    """
    Load the cleaned air traffic file from the processed folder.
    """
    path = get_cleaned_file_path(filename)
    if not os.path.exists(path):
        st.error(f"Cleaned data file not found: {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path, sep=';', encoding='utf-8')
    
    # Create a proper date column (useful for filters and charts)
    if 'annee' in df.columns and 'mois' in df.columns:
        df['date'] = pd.to_datetime(
            df['annee'].astype(str) + '-' + df['mois'].astype(str).str.zfill(2) + '-01',
            errors='coerce'
        )
    
    return df

def save_cleaned_data(df, filename="trafic_aerien_1990_2024_cleaned.csv"):
    """
    Save the cleaned dataset inside the processed data folder.
    """
    path = get_cleaned_file_path(filename)
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(path, sep=';', index=False, encoding='utf-8')
    st.success(f"Cleaned data saved to {path}")

@st.cache_data(show_spinner=False)
def load_and_cache_data():
    """
    Load the cleaned data (cached for better performance).
    """
    df_cleaned = load_cleaned_data()
    return df_cleaned
