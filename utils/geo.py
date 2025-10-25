from typing import Dict, Optional, List, Tuple
import unicodedata

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st



# Core: Haversine distance (km)


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km (vectorized)."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * (2 * np.arcsin(np.sqrt(a)))



# Airports (APT) geo helpers


def geo_summary_airports(df_apt: pd.DataFrame) -> Dict[str, float]:
    """Centroid + bounding box for airport coordinates."""
    if df_apt.empty or not {"latitude", "longitude"}.issubset(df_apt.columns):
        return {}
    d = df_apt.dropna(subset=["latitude", "longitude"]).copy()
    bbox = {
        "lat_min": float(d["latitude"].min()),
        "lat_max": float(d["latitude"].max()),
        "lon_min": float(d["longitude"].min()),
        "lon_max": float(d["longitude"].max()),
    }
    return {
        "centroid_lat": float(d["latitude"].mean()),
        "centroid_lon": float(d["longitude"].mean()),
        **bbox,
        "airport_count": int(d["code_aeroport"].nunique()) if "code_aeroport" in d.columns else None,
    }


def detect_top_hubs(df_apt: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top airports by passengers/freight."""
    if df_apt.empty:
        return pd.DataFrame()
    group = (
        df_apt.groupby(["code_aeroport", "nom_aeroport"], dropna=False)
        .agg(
            passengers=("passagers_total", "sum"),
            freight=("fret_total", "sum"),
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
        )
        .reset_index()
        .sort_values("passengers", ascending=False)
    )
    group["rank"] = np.arange(1, len(group) + 1)
    return group.head(top_n)



# Legacy: APT → PyDeck bubbles, LSN (with coords)


def to_pydeck_airports(df_apt: pd.DataFrame) -> pd.DataFrame:
    """Aggregate passengers by airport, output columns: latitude, longitude, value, nom_aeroport, code_aeroport."""
    if df_apt.empty or not {"latitude", "longitude"}.issubset(df_apt.columns):
        return pd.DataFrame()
    d = df_apt.dropna(subset=["latitude", "longitude"]).copy()
    if "passagers_total" not in d.columns:
        d["passagers_total"] = d.get("passagers_depart", 0) + d.get("passagers_arrivee", 0)
    d = (
        d.groupby(["code_aeroport", "nom_aeroport", "latitude", "longitude"], dropna=False)["passagers_total"]
        .sum()
        .reset_index()
        .rename(columns={"passagers_total": "value"})
    )
    return d


def to_pydeck_routes(df_lsn: pd.DataFrame) -> pd.DataFrame:
    """
    Convert an LSN already enriched with columns o_lat/o_lon/d_lat/d_lon into a minimal arc format.
    (Kept for backward compatibility.)
    """
    need = {"o_lat", "o_lon", "d_lat", "d_lon"}
    if df_lsn.empty or not need.issubset(df_lsn.columns):
        return pd.DataFrame()
    cols = ["o_lat", "o_lon", "d_lat", "d_lon"]
    if "lsn_pax" in df_lsn.columns:
        cols.append("lsn_pax")
    d = df_lsn[cols].dropna().copy()
    if "lsn_pax" in d.columns:
        d = d.rename(columns={"lsn_pax": "value"})
    return d



# Geo insight bundle (for Airports & Routes tab)


def top_longest_routes(df_lsn: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Top-N longest routes by average distance_km (requires distance_km column)."""
    if df_lsn.empty or "distance_km" not in df_lsn.columns:
        return pd.DataFrame()
    grp = (
        df_lsn.groupby("route_pair", dropna=False)["distance_km"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    return grp


def top_busiest_routes(df_lsn: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Top-N routes by passengers using any available route key."""
    if df_lsn.empty:
        return pd.DataFrame()
    key = "route_pair" if "route_pair" in df_lsn.columns else ("route_dir" if "route_dir" in df_lsn.columns else "lsn_seg" if "lsn_seg" in df_lsn.columns else None)
    if key is None or "lsn_pax" not in df_lsn.columns:
        return pd.DataFrame()
    grp = (
        df_lsn.groupby(key, dropna=False)["lsn_pax"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
        .rename(columns={key: "route", "lsn_pax": "passengers"})
    )
    return grp


def average_route_distance(df_lsn: pd.DataFrame) -> float:
    """Weighted average distance (needs distance_km & lsn_pax)."""
    if df_lsn.empty or not {"distance_km", "lsn_pax"}.issubset(df_lsn.columns):
        return np.nan
    d = df_lsn.dropna(subset=["distance_km", "lsn_pax"]).copy()
    tot = d["lsn_pax"].sum()
    return float((d["distance_km"] * d["lsn_pax"]).sum() / tot) if tot > 0 else np.nan


def geo_bundle(df_apt: pd.DataFrame, df_lsn: Optional[pd.DataFrame] = None) -> Dict[str, object]:
    """Quick geo insights to feed the story."""
    out: Dict[str, object] = {}
    if not df_apt.empty:
        out["airport_geo_summary"] = geo_summary_airports(df_apt)
        out["top_hubs"] = detect_top_hubs(df_apt, top_n=10)
    if df_lsn is not None and not df_lsn.empty:
       
        if {"distance_km", "lsn_pax"}.issubset(df_lsn.columns):
            out["avg_route_distance_km"] = average_route_distance(df_lsn)
        out["top_busiest_routes"] = top_busiest_routes(df_lsn, 10)
    return out
