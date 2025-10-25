import os
from typing import List, Dict, Optional, Tuple
import pandas as pd
import streamlit as st

#  Directory layout (processed-only) 
BASE_DATA = os.getenv("AIR_DATA_DIR", "data")
APT_DIR = os.path.join(BASE_DATA, "APT", "processed")
CIE_DIR = os.path.join(BASE_DATA, "CIE", "processed")
LSN_DIR = os.path.join(BASE_DATA, "LSN", "processed")

# Default processed filenames 
APT_PROCESSED_FILE = "apt.csv"
CIE_PROCESSED_FILE = "cie.csv"
LSN_PROCESSED_FILE = "lsn.csv"

#  internals 
def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _auto_sep(path: str) -> str:
    """Pick a reasonable CSV separator by trial."""
    for sep in [";", ",", "\t", "|"]:
        try:
            df = pd.read_csv(path, sep=sep, nrows=5, encoding="utf-8")
            if df.shape[1] >= 3:
                return sep
        except Exception:
            continue
    return ";"  # fallback

def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.replace("\uFEFF", "", regex=False)
        .str.lower()
    )
    return df

def _derive_date(df: pd.DataFrame) -> pd.DataFrame:
    """Create a 'date' column from (annee, mois) or ANMOIS/annee_mois when present."""
    df = df.copy()
    cols = set(df.columns)

    if {"annee", "mois"}.issubset(cols):
        df["date"] = pd.to_datetime(
            df["annee"].astype(str) + "-" + df["mois"].astype(str).str.zfill(2) + "-01",
            errors="coerce"
        )
    elif "anmois" in cols:
        s = df["anmois"].astype(str).str.replace(r"[^0-9]", "", regex=True).str.zfill(6)
        df["date"] = pd.to_datetime(s.str[:4] + "-" + s.str[4:6] + "-01", errors="coerce")
        df["annee"] = df["date"].dt.year
        df["mois"]  = df["date"].dt.month
    elif "annee_mois" in cols:
        s = df["annee_mois"].astype(str).str.replace(r"[^0-9]", "", regex=True).str.zfill(6)
        df["date"] = pd.to_datetime(s.str[:4] + "-" + s.str[4:6] + "-01", errors="coerce")
        df["annee"] = df["date"].dt.year
        df["mois"]  = df["date"].dt.month

    return df

def _read_processed_csv(path: str) -> pd.DataFrame:
    sep = _auto_sep(path)
    df = pd.read_csv(path, sep=sep, encoding="utf-8")
    df = _normalize(df)
    df = _derive_date(df)
    return df

def _list_csvs(folder: str) -> List[str]:
    _ensure_dir(folder)
    return sorted([f for f in os.listdir(folder) if f.lower().endswith(".csv")])

#  path helpers (processed only) 
def path_apt(filename: Optional[str] = None) -> str:
    _ensure_dir(APT_DIR)
    return os.path.join(APT_DIR, filename or APT_PROCESSED_FILE)

def path_cie(filename: Optional[str] = None) -> str:
    _ensure_dir(CIE_DIR)
    return os.path.join(CIE_DIR, filename or CIE_PROCESSED_FILE)

def path_lsn(filename: Optional[str] = None) -> str:
    _ensure_dir(LSN_DIR)
    return os.path.join(LSN_DIR, filename or LSN_PROCESSED_FILE)

#  loaders (processed only) 
@st.cache_data(show_spinner=False)
def load_apt_processed(filename: str = APT_PROCESSED_FILE) -> pd.DataFrame:
    p = path_apt(filename)
    if not os.path.exists(p):
        st.error(f"APT processed file not found: {p}")
        return pd.DataFrame()
    df = _read_processed_csv(p)
    # convenience totals
    if {"passagers_depart", "passagers_arrivee"}.issubset(df.columns):
        df["passagers_total"] = df["passagers_depart"].fillna(0) + df["passagers_arrivee"].fillna(0)
    if {"fret_depart", "fret_arrivee"}.issubset(df.columns):
        df["fret_total"] = df["fret_depart"].fillna(0) + df["fret_arrivee"].fillna(0)
    return df

@st.cache_data(show_spinner=False)
def load_cie_processed(filename: str = CIE_PROCESSED_FILE) -> pd.DataFrame:
    p = path_cie(filename)
    if not os.path.exists(p):
        st.error(f"CIE processed file not found: {p}")
        return pd.DataFrame()
    df = _read_processed_csv(p)
    for col in ["cie_pax", "cie_pkt", "cie_tkt", "cie_frp", "cie_vol", "cie_peq", "cie_peqkt"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

@st.cache_data(show_spinner=False)
def load_lsn_processed(filename: str = LSN_PROCESSED_FILE) -> pd.DataFrame:
    p = path_lsn(filename)
    if not os.path.exists(p):
        st.error(f"LSN processed file not found: {p}")
        return pd.DataFrame()
    df = _read_processed_csv(p)
    for col in ["lsn_pax", "lsn_pkt", "lsn_tkt", "lsn_frp", "lsn_peq", "lsn_peqkt"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

#  discovery / diagnostics (processed only) 
@st.cache_data(show_spinner=False)
def list_processed() -> Dict[str, List[str]]:
    return {
        "APT": _list_csvs(APT_DIR),
        "CIE": _list_csvs(CIE_DIR),
        "LSN": _list_csvs(LSN_DIR),
    }

def date_bounds(df: pd.DataFrame) -> Optional[Tuple[pd.Timestamp, pd.Timestamp]]:
    if "date" not in df.columns or df["date"].isna().all():
        return None
    return (pd.to_datetime(df["date"].min()), pd.to_datetime(df["date"].max()))

def quick_report(df: pd.DataFrame) -> Dict[str, object]:
    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "missing_cells": int(df.isna().sum().sum()),
        "date_min": str(df["date"].min()) if "date" in df.columns else None,
        "date_max": str(df["date"].max()) if "date" in df.columns else None,
        "columns": list(df.columns),
    }

def show_quick_report(df: pd.DataFrame, title: str = "Data Quality Snapshot") -> None:
    rpt = quick_report(df)
    with st.expander(title, expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{rpt['rows']:,}")
        c2.metric("Columns", f"{rpt['cols']:,}")
        c3.metric("Missing cells", f"{rpt['missing_cells']:,}")
        st.json(rpt)
