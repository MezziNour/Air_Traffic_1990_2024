import pandas as pd

def make_tables(df):
    tables = {}

    df = df.copy()
    df['passengers_total'] = df[['passagers_depart', 'passagers_arrivee', 'passagers_transit']].sum(axis=1)
    df['freight_total'] = df[['fret_depart', 'fret_arrivee']].sum(axis=1)
    df['movements_total'] = df[['mouvements_passagers', 'mouvements_cargo']].sum(axis=1)
    df['metric_total'] = df['passengers_total']

    # -----------------------------
    # Handle date columns safely
    # -----------------------------
    if 'annee_mois' in df.columns:
        df['annee_mois'] = pd.to_datetime(df['annee_mois'].astype(str), format='%Y%m', errors='coerce')

    df['annee'] = df['annee_mois'].dt.year
    df['mois'] = df['annee_mois'].dt.month

    # Drop rows with missing year or month
    df = df.dropna(subset=['annee', 'mois'])

    # Create date column
    df['date'] = pd.to_datetime(
        df['annee'].astype(int).astype(str) + '-' +
        df['mois'].astype(int).astype(str).str.zfill(2) + '-01'
    )

    # -----------------------------
    # Timeseries Table
    # -----------------------------
    timeseries = df.groupby(['date', 'zone'], as_index=False).agg({
        'passengers_total': 'sum',
        'freight_total': 'sum',
        'movements_total': 'sum',
        'metric_total': 'sum'
    })
    tables['timeseries'] = timeseries

    # -----------------------------
    # By Region Table
    # -----------------------------
    by_region = df.groupby(['zone'], as_index=False).agg({
        'passengers_total': 'sum',
        'freight_total': 'sum',
        'movements_total': 'sum',
        'metric_total': 'sum'
    })
    tables['by_region'] = by_region

    # -----------------------------
    # By Airport Table
    # -----------------------------
    by_airport = df.groupby(['code_aeroport', 'nom_aeroport', 'zone'], as_index=False).agg({
        'passengers_total': 'sum',
        'freight_total': 'sum',
        'movements_total': 'sum',
        'metric_total': 'sum'
    })
    tables['by_airport'] = by_airport

    # -----------------------------
    # Geo Table
    # -----------------------------
    geo = df.groupby(['nom_aeroport', 'zone', 'latitude', 'longitude'], as_index=False).agg({
        'metric_total': 'sum'
    })
    tables['geo'] = geo

    return tables
