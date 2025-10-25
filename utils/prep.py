from typing import List, Optional, Tuple, Dict
import pandas as pd
import numpy as np
import streamlit as st


def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.lower()
                .str.strip()
                .str.replace("\uFEFF", "", regex=False)
                .str.replace(" ", "_")
                .str.replace("-", "_")
    )

    return df

def to_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def add_date_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure date, year, month, quarter columns exist when possible."""
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

    if "date" in df.columns:
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    return df


# Schema validations (per dataset) 


APT_EXPECTED = [
    "annee_mois","code_aeroport","nom_aeroport","zone","unites_trafic",
    "passagers_depart","passagers_arrivee","passagers_transit","fret_depart",
    "fret_arrivee","mouvements_passagers","mouvements_cargo","source",
    "annee","mois","ville","latitude","longitude"
]

CIE_EXPECTED = [
    "anmois","cie","cie_nom","cie_nat","cie_pays","cie_pax","cie_frp","cie_peq",
    "cie_pkt","cie_tkt","cie_peqkt","cie_vol","source_file","annee","mois"
]

LSN_EXPECTED = [
    "anmois","lsn_seg","lsn_fsc","lsn_1","lsn_2","lsn_2_cont","lsn_peq","lsn_peqkt",
    "lsn_pax","lsn_pkt","lsn_frp","lsn_tkt","lsn_drt","source_file","annee","mois"
]
KNOWN_DERIVED = {
    # generic
    "date", "year", "month", "quarter",
    # APT derived
    "passagers_total", "fret_total", "has_geo",
    # LSN derived
    "route_dir", "route_pair",
}

def validate_schema(df: pd.DataFrame, expected: List[str], allowed_extras: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """
    Compare dataframe columns to expected schema, but do not flag known
    derived columns as problems. Returns {missing, extras, derived}.
    """
    present = set(df.columns)
    exp = {c.lower() for c in expected}
    allowed = KNOWN_DERIVED.union({c.lower() for c in (allowed_extras or [])})

    missing = sorted([c for c in exp if c not in present])
    derived = sorted(list((present & allowed) - exp))
    extras  = sorted([c for c in present if c not in exp and c not in allowed])

    return {"missing": missing, "extras": extras, "derived": derived}



# Dataset-specific preparation 


def prep_apt(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_cols(df)
    df = add_date_fields(df)
    df = df.replace(["", " ", "-", "nan", "NaN", "None"], np.nan)
    df = to_numeric(df, [
        "passagers_depart","passagers_arrivee","passagers_transit",
        "fret_depart","fret_arrivee","mouvements_passagers","mouvements_cargo",
        "latitude","longitude","annee","mois"
    ])
    # Derived totals
    if {"passagers_depart","passagers_arrivee"}.issubset(df.columns):
        df["passagers_total"] = df["passagers_depart"].fillna(0) + df["passagers_arrivee"].fillna(0)
    if {"fret_depart","fret_arrivee"}.issubset(df.columns):
        df["fret_total"] = df["fret_depart"].fillna(0) + df["fret_arrivee"].fillna(0)

    # Simple geographic sanity
    if "latitude" in df.columns and "longitude" in df.columns:
        df["has_geo"] = df["latitude"].notna() & df["longitude"].notna()

    # lightweight airport dim (for labels/tooltips)
    dim_cols = ["code_aeroport","nom_aeroport","zone","ville","latitude","longitude"]
    df.attrs["airport_dim"] = (
        df[dim_cols].drop_duplicates().reset_index(drop=True)
        if all(c in df.columns for c in dim_cols) else pd.DataFrame()
    )

    df.attrs["schema_issues"] = validate_schema(df, APT_EXPECTED)
    return df

def prep_cie(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_cols(df)
    df = add_date_fields(df)
    df = to_numeric(df, [
        "cie_pax","cie_pkt","cie_tkt","cie_frp","cie_vol","cie_peq","cie_peqkt","annee","mois"
    ])

    dim_cols = ["cie","cie_nom","cie_pays"]
    df.attrs["airline_dim"] = (
        df[dim_cols].drop_duplicates().reset_index(drop=True)
        if all(c in df.columns for c in dim_cols) else pd.DataFrame()
    )

    
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)

    df.attrs["schema_issues"] = validate_schema(df, CIE_EXPECTED)
    return df


def prep_lsn(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_cols(df)
    df = add_date_fields(df)
    df = to_numeric(df, [
        "lsn_pax","lsn_pkt","lsn_tkt","lsn_frp","lsn_peq","lsn_peqkt","annee","mois"
    ])

    if {"lsn_1","lsn_2"}.issubset(df.columns):
        df["route_dir"] = df["lsn_1"].astype(str) + " → " + df["lsn_2"].astype(str)
        df["route_pair"] = np.where(
            df["lsn_1"] < df["lsn_2"],
            df["lsn_1"].astype(str) + " — " + df["lsn_2"].astype(str),
            df["lsn_2"].astype(str) + " — " + df["lsn_1"].astype(str),
        )

    
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)

    df.attrs["schema_issues"] = validate_schema(df, LSN_EXPECTED)
    return df



# Filters 


def filter_by_date(df: pd.DataFrame, start, end) -> pd.DataFrame:
    if "date" not in df.columns:
        return df.copy()
    out = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))].copy()
    return out

def filter_by_airports(df: pd.DataFrame, airports: Optional[List[str]]) -> pd.DataFrame:
    if not airports:
        return df.copy()
    if "code_aeroport" in df.columns:
        return df[df["code_aeroport"].isin(airports)].copy()
    if "lsn_1" in df.columns and "lsn_2" in df.columns:
        return df[(df["lsn_1"].isin(airports)) | (df["lsn_2"].isin(airports))].copy()
    return df.copy()

def filter_by_airlines(df: pd.DataFrame, airlines: Optional[List[str]]) -> pd.DataFrame:
    if not airlines or "cie" not in df.columns:
        return df.copy()
    return df[df["cie"].isin(airlines)].copy()


# KPIs & analytics helpers


def yoy_growth(s: pd.Series) -> pd.Series:
    """Year-over-year growth for a time-indexed Series (monthly or yearly)."""
    return s.pct_change(periods=12) * 100.0

def rolling_mean(s: pd.Series, window: int = 3) -> pd.Series:
    return s.rolling(window=window, min_periods=max(1, window // 2)).mean()

def recovery_vs_baseline(df: pd.DataFrame, value_col: str, baseline_year: int = 2019) -> float:
    """Compute recovery percentage vs. baseline year total (e.g., 2024 vs 2019)."""
    if "year" not in df.columns:
        return np.nan
    base = df.loc[df["year"] == baseline_year, value_col].sum()
    current_year = int(df["year"].max()) if len(df) else None
    curr = df.loc[df["year"] == current_year, value_col].sum() if current_year else np.nan
    if base and base > 0:
        return (curr / base) * 100.0
    return np.nan


# Pre-aggregations (per dataset)


#  APT 

def agg_apt_timeseries(df, freq="M"):
    """
    Aggregate APT dataset over time (month, quarter, year).
    Safely removes attrs metadata that may break Pandas operations.
    """
    if df.empty or "date" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df.attrs = {}  
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # List of potential numeric columns
    cols = [
        "passagers_total",
        "fret_total",
        "mouvements_passagers",
        "mouvements_cargo",
    ]

    # Keep only existing numeric columns
    agg_dict = {
        c: "sum"
        for c in cols
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c])
    }

    if not agg_dict:
        return pd.DataFrame()

    try:
        grp = (
            df.set_index("date")
            .resample(freq)
            .agg(agg_dict)
            .reset_index()
            .sort_values("date")
        )
    except Exception as e:
        # Safety fallback in case of any weird type
        st.warning(f"Aggregation error: {e}")
        grp = df[["date"] + list(agg_dict.keys())].copy()

    return grp



def agg_apt_by_airport(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    if "code_aeroport" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby(["code_aeroport","nom_aeroport"], dropna=False)
          .agg(passagers_total=("passagers_total","sum"),
               fret_total=("fret_total","sum"))
          .reset_index()
          .sort_values("passagers_total", ascending=False)
    )
    return grp.head(top_n)

def agg_apt_geo_bubbles(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per airport with coordinates for map bubbles."""
    needed = {"code_aeroport","nom_aeroport","latitude","longitude","passagers_total"}
    if not needed.issubset(df.columns):
        return pd.DataFrame()
    grp = (
        df.groupby(["code_aeroport","nom_aeroport","latitude","longitude"], dropna=False)["passagers_total"]
          .sum().reset_index()
    )
    grp = grp.dropna(subset=["latitude","longitude"])
    return grp

#  CIE 

def agg_cie_timeseries(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """Aggregate CIE dataset over time with safe attrs/date handling."""
    if df.empty or "date" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df.attrs = {}  # prevent pandas concat/agg from comparing attrs
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    agg_map = {
        c: "sum"
        for c in ["cie_pax", "cie_pkt", "cie_tkt", "cie_frp", "cie_vol"]
        if c in df.columns
    }
    if not agg_map:
        return pd.DataFrame()

    # ensure numeric types for safety
    for c in agg_map.keys():
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    try:
        grp = (
            df.set_index("date")
              .resample(freq)
              .agg(agg_map)
              .reset_index()
              .sort_values("date")
        )
    except Exception as e:
        # fallback to simple groupby if resample chokes
        st.warning(f"CIE aggregation fallback due to: {e}")
        grp = (
            df.assign(__period=df["date"].dt.to_period(freq))
              .groupby("__period", as_index=False)
              .agg(agg_map)
        )
        grp["date"] = grp["__period"].dt.to_timestamp()
        grp = grp.drop(columns="__period")

    return grp


def agg_cie_market_share(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if not {"cie","cie_pax"}.issubset(df.columns):
        return pd.DataFrame()
    totals = (
        df.groupby("cie")["cie_pax"].sum().sort_values(ascending=False).reset_index()
    )
    totals["share"] = totals["cie_pax"] / totals["cie_pax"].sum()
    return totals.head(top_n)

#  LSN 

def agg_lsn_top_routes(df: pd.DataFrame, value: str = "lsn_pax", top_n: int = 20, undirected: bool = True) -> pd.DataFrame:
    if value not in df.columns:
        return pd.DataFrame()
    if undirected and "route_pair" in df.columns:
        grp = df.groupby("route_pair")[value].sum().sort_values(ascending=False).head(top_n).reset_index()
        grp = grp.rename(columns={"route_pair": "route"})
    else:
        key = "route_dir" if "route_dir" in df.columns else "lsn_seg"
        grp = df.groupby(key)[value].sum().sort_values(ascending=False).head(top_n).reset_index()
        grp = grp.rename(columns={key: "route"})
    return grp

def agg_lsn_timeseries(df: pd.DataFrame, value: str = "lsn_pax", freq: str = "M") -> pd.DataFrame:
    if "date" not in df.columns or value not in df.columns:
        return pd.DataFrame()
    grp = df.set_index("date")[value].resample(freq).sum().reset_index()
    return grp


# Data quality diagnostics (for the Quality section)


def missing_by_column(df: pd.DataFrame) -> pd.DataFrame:
    ser = df.isna().sum().sort_values(ascending=False)
    return ser[ser > 0].rename("missing").to_frame().reset_index().rename(columns={"index": "column"})

def duplicate_keys_apt(df: pd.DataFrame) -> pd.DataFrame:
    """Detect duplicates for (annee, mois, code_aeroport)."""
    keys = ["annee","mois","code_aeroport"]
    if not set(keys).issubset(df.columns):
        return pd.DataFrame()
    dup = df[df.duplicated(keys, keep=False)].sort_values(keys)
    return dup

def duplicate_keys_cie(df: pd.DataFrame) -> pd.DataFrame:
    """Detect duplicates for (annee, mois, cie)."""
    keys = ["annee","mois","cie"]
    if not set(keys).issubset(df.columns):
        return pd.DataFrame()
    dup = df[df.duplicated(keys, keep=False)].sort_values(keys)
    return dup

def duplicate_keys_lsn(df: pd.DataFrame) -> pd.DataFrame:
    """Detect duplicates for (annee, mois, lsn_seg) when available."""
    keys = ["annee","mois","lsn_seg", "lsn_fsc", "lsn_1", "lsn_2"]
    if not set(keys).issubset(df.columns):
        return pd.DataFrame()
    dup = df[df.duplicated(keys, keep=False)].sort_values(keys)
    return dup

def iqr_outliers(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Return rows with values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]."""
    if col not in df.columns:
        return pd.DataFrame()
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return pd.DataFrame()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    return df[(df[col] < lo) | (df[col] > hi)]

def get_date_range(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Return the min and max date of a dataframe, if available.
    Used to restrict Streamlit sliders and filters.
    """
    if "date" not in df.columns or df["date"].dropna().empty:
        return (pd.Timestamp(1990, 1, 1), pd.Timestamp(2024, 12, 31))
    
    start = df["date"].min()
    end = df["date"].max()
    return (start, end)



# Convenience: bundles for sections


def apt_bundle_for_section(df_apt: pd.DataFrame, start, end, top_n: int = 15) -> Dict[str, pd.DataFrame]:
    view = filter_by_date(df_apt, start, end)
    return {
        "timeseries_M": agg_apt_timeseries(view, "M"),
        "timeseries_Y": agg_apt_timeseries(view, "Y"),
        "by_airport":   agg_apt_by_airport(view, top_n=top_n),
        "geo_bubbles":  agg_apt_geo_bubbles(view),
    }

def cie_bundle_for_section(df_cie: pd.DataFrame, start, end, top_n: int = 15) -> Dict[str, pd.DataFrame]:
    view = filter_by_date(df_cie, start, end)
    return {
        "timeseries_M": agg_cie_timeseries(view, "M"),
        "timeseries_Y": agg_cie_timeseries(view, "Y"),
        "market_share": agg_cie_market_share(view, top_n=top_n),
    }

def lsn_bundle_for_section(df_lsn: pd.DataFrame, start, end, top_n: int = 20) -> Dict[str, pd.DataFrame]:
    view = filter_by_date(df_lsn, start, end)
    return {
        "timeseries_M": agg_lsn_timeseries(view, "lsn_pax", "M"),
        "timeseries_Y": agg_lsn_timeseries(view, "lsn_pax", "Y"),
        "top_routes":   agg_lsn_top_routes(view, "lsn_pax", top_n=top_n, undirected=True),
    }