from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


# Generic helpers


def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")

def _safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if (b is not None and b != 0) else np.nan

def _yearly_sum(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    if "year" not in df.columns:
        if "date" in df.columns:
            df = df.assign(year=pd.to_datetime(df["date"]).dt.year)
        else:
            raise ValueError("Need 'year' or 'date' column for yearly sums.")
    d = df.copy()
    d[value_col] = _to_num(d[value_col])
    return d.groupby("year", dropna=False)[value_col].sum().reset_index()

def cagr(df: pd.DataFrame, value_col: str, start_year: Optional[int] = None, end_year: Optional[int] = None) -> float:
    """Compound Annual Growth Rate based on yearly totals."""
    y = _yearly_sum(df, value_col)
    if y.empty or y[value_col].le(0).all():
        return np.nan
    if start_year is None:
        start_year = int(y["year"].min())
    if end_year is None:
        end_year = int(y["year"].max())
    y = y[(y["year"] >= start_year) & (y["year"] <= end_year)]
    if y.empty:
        return np.nan
    v0, v1 = float(y.loc[y["year"] == start_year, value_col].sum()), float(y.loc[y["year"] == end_year, value_col].sum())
    n = max(1, end_year - start_year)
    if v0 <= 0 or v1 <= 0:
        return np.nan
    return (v1 / v0) ** (1 / n) - 1

def yoy_monthly(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Return a table with YoY change for a monthly series (needs 'date')."""
    if "date" not in df.columns:
        return pd.DataFrame()
    d = df.copy()
    d = d.sort_values("date")
    d[value_col] = _to_num(d[value_col])
    d["yoy_pct"] = d[value_col].pct_change(periods=12) * 100.0
    return d[["date", value_col, "yoy_pct"]]

def mom(df: pd.DataFrame, value_col: str) -> float:
    """Last month vs previous month percentage change."""
    if "date" not in df.columns or df.empty:
        return np.nan
    d = df.sort_values("date")[[value_col]].copy()
    d[value_col] = _to_num(d[value_col])
    if len(d) < 2:
        return np.nan
    last, prev = d[value_col].iloc[-1], d[value_col].iloc[-2]
    return (last / prev - 1) * 100.0 if prev and prev != 0 else np.nan

def recent_yoy(df: pd.DataFrame, value_col: str) -> float:
    """Last value vs value 12 months earlier (%)."""
    if "date" not in df.columns or len(df) < 13:
        return np.nan
    d = df.sort_values("date")[[value_col]].copy()
    d[value_col] = _to_num(d[value_col])
    last, prev = d[value_col].iloc[-1], d[value_col].iloc[-13]
    return (last / prev - 1) * 100.0 if prev and prev != 0 else np.nan

def recovery_vs_baseline_year(df: pd.DataFrame, value_col: str, baseline_year: int = 2019) -> float:
    y = _yearly_sum(df, value_col)
    if y.empty:
        return np.nan
    current_year = int(y["year"].max())
    base = float(y.loc[y["year"] == baseline_year, value_col].sum())
    curr = float(y.loc[y["year"] == current_year, value_col].sum())
    return (curr / base) * 100.0 if base and base != 0 else np.nan

def seasonality_index(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Month index = value / average_month_value (across years). 1.0 = average."""
    if "date" not in df.columns:
        return pd.DataFrame()
    d = df.copy()
    d["month"] = pd.to_datetime(d["date"]).dt.month
    d[value_col] = _to_num(d[value_col])
    monthly = d.groupby("month")[value_col].mean()
    overall = monthly.mean()
    if overall == 0 or np.isnan(overall):
        return pd.DataFrame()
    idx = (monthly / overall).rename("seasonality_index").reset_index()
    return idx

def hhi_concentration(df: pd.DataFrame, entity_col: str, value_col: str) -> float:
    """Herfindahl–Hirschman Index: sum of squared shares (0–1). Higher = more concentrated."""
    if df.empty or not set([entity_col, value_col]).issubset(df.columns):
        return np.nan
    s = df.groupby(entity_col, dropna=False)[value_col].sum()
    total = s.sum()
    if total <= 0:
        return np.nan
    shares = (s / total).fillna(0.0)
    return float((shares ** 2).sum())

def topn_share(df: pd.DataFrame, entity_col: str, value_col: str, n: int = 3) -> float:
    if df.empty or not set([entity_col, value_col]).issubset(df.columns):
        return np.nan
    s = df.groupby(entity_col, dropna=False)[value_col].sum().sort_values(ascending=False)
    total = s.sum()
    return float(s.head(n).sum() / total) if total and total != 0 else np.nan

def contribution_to_change(
    df: pd.DataFrame,
    entity_col: str,
    value_col: str,
    period_a: Tuple[pd.Timestamp, pd.Timestamp],
    period_b: Tuple[pd.Timestamp, pd.Timestamp],
    top_n: int = 10
) -> pd.DataFrame:
    """Which entities drove the change between period A and period B?
    Returns a table with delta and share of total delta.
    """
    if "date" not in df.columns:
        return pd.DataFrame()
    a = df[(df["date"] >= pd.to_datetime(period_a[0])) & (df["date"] <= pd.to_datetime(period_a[1]))]
    b = df[(df["date"] >= pd.to_datetime(period_b[0])) & (df["date"] <= pd.to_datetime(period_b[1]))]
    a_sum = a.groupby(entity_col, dropna=False)[value_col].sum()
    b_sum = b.groupby(entity_col, dropna=False)[value_col].sum()
    all_keys = a_sum.index.union(b_sum.index)
    out = pd.DataFrame({
        entity_col: all_keys,
        "value_A": a_sum.reindex(all_keys).fillna(0).values,
        "value_B": b_sum.reindex(all_keys).fillna(0).values
    })
    out["delta"] = out["value_B"] - out["value_A"]
    total_delta = out["delta"].sum()
    out["share_of_delta"] = out["delta"] / total_delta if total_delta != 0 else np.nan
    out = out.sort_values("delta", ascending=False).head(top_n).reset_index(drop=True)
    return out


# APT KPIs


def kpis_apt(df_apt: pd.DataFrame) -> Dict[str, object]:
    if df_apt.empty:
        return {}
    d = df_apt.copy()
    d["passagers_total"] = _to_num(d.get("passagers_total", d.get("passagers_depart", 0))) + _to_num(d.get("passagers_arrivee", 0))
    d["fret_total"] = _to_num(d.get("fret_total", d.get("fret_depart", 0))) + _to_num(d.get("fret_arrivee", 0))

    total_pax = float(d["passagers_total"].sum())
    total_freight = float(d["fret_total"].sum())

    # Top airport by pax
    g_air = d.groupby(["code_aeroport","nom_aeroport"], dropna=False)["passagers_total"].sum().sort_values(ascending=False)
    if len(g_air):
        top_airport_code, top_airport_name = g_air.index[0]
        top_airport_pax = float(g_air.iloc[0])
    else:
        top_airport_code = top_airport_name = None
        top_airport_pax = 0.0

    # Peaks
    ts = d.groupby("date", dropna=False)["passagers_total"].sum().reset_index()
    ts = ts.dropna(subset=["date"])
    peak_month = ts.loc[ts["passagers_total"].idxmax()] if not ts.empty else None

    # Growth metrics
    yoy_pct = recent_yoy(ts, "passagers_total")
    mom_pct = mom(ts, "passagers_total")
    rec_2019 = recovery_vs_baseline_year(d, "passagers_total", baseline_year=2019)
    growth_cagr = cagr(d, "passagers_total")

    # Concentration among airports
    hhi_air = hhi_concentration(d, "code_aeroport", "passagers_total")
    top3_share = topn_share(d, "code_aeroport", "passagers_total", 3)

    return {
        "total_passengers": total_pax,
        "total_freight": total_freight,
        "top_airport_code": top_airport_code,
        "top_airport_name": top_airport_name,
        "top_airport_pax": top_airport_pax,
        "peak_month_date": (pd.to_datetime(peak_month["date"]) if peak_month is not None else None),
        "peak_month_pax": (float(peak_month["passagers_total"]) if peak_month is not None else None),
        "yoy_pct": yoy_pct,
        "mom_pct": mom_pct,
        "recovery_vs_2019_pct": rec_2019,
        "cagr": growth_cagr,
        "hhi_airports": hhi_air,
        "top3_airport_share": top3_share,
    }


# CIE KPIs


def kpis_cie(df_cie: pd.DataFrame) -> Dict[str, object]:
    if df_cie.empty:
        return {}
    d = df_cie.copy()
    d["cie_pax"] = _to_num(d.get("cie_pax", 0))
    d["cie_vol"] = _to_num(d.get("cie_vol", 0))

    total_pax = float(d["cie_pax"].sum())
    total_flights = float(d["cie_vol"].sum()) if "cie_vol" in d.columns else np.nan

    # Top airline by pax
    g_airline = d.groupby(["cie","cie_nom"], dropna=False)["cie_pax"].sum().sort_values(ascending=False)
    if len(g_airline):
        top_cie_code, top_cie_name = g_airline.index[0]
        top_cie_pax = float(g_airline.iloc[0])
    else:
        top_cie_code = top_cie_name = None
        top_cie_pax = 0.0

    # Timeseries for growth
    ts = d.groupby("date", dropna=False)["cie_pax"].sum().reset_index()
    ts = ts.dropna(subset=["date"])
    yoy_pct = recent_yoy(ts, "cie_pax")
    mom_pct = mom(ts, "cie_pax")
    rec_2019 = recovery_vs_baseline_year(d, "cie_pax", baseline_year=2019)
    growth_cagr = cagr(d, "cie_pax")

    # Market concentration
    hhi_airlines = hhi_concentration(d, "cie", "cie_pax")
    top3_share = topn_share(d, "cie", "cie_pax", 3)

    return {
        "total_airline_passengers": total_pax,
        "total_flights_reported": total_flights,
        "top_airline_code": top_cie_code,
        "top_airline_name": top_cie_name,
        "top_airline_pax": top_cie_pax,
        "yoy_pct": yoy_pct,
        "mom_pct": mom_pct,
        "recovery_vs_2019_pct": rec_2019,
        "cagr": growth_cagr,
        "hhi_airlines": hhi_airlines,
        "top3_airline_share": top3_share,
    }


# LSN KPIs


def kpis_lsn(df_lsn: pd.DataFrame) -> Dict[str, object]:
    if df_lsn.empty:
        return {}
    d = df_lsn.copy()
    d["lsn_pax"] = _to_num(d.get("lsn_pax", 0))

    total_route_pax = float(d["lsn_pax"].sum())

    # Top route (undirected if available)
    if "route_pair" in d.columns:
        g_route = d.groupby("route_pair", dropna=False)["lsn_pax"].sum().sort_values(ascending=False)
        top_route = g_route.index[0] if len(g_route) else None
        top_route_pax = float(g_route.iloc[0]) if len(g_route) else 0.0
    else:
        key = "route_dir" if "route_dir" in d.columns else ("lsn_seg" if "lsn_seg" in d.columns else None)
        if key is None:
            top_route, top_route_pax = None, 0.0
        else:
            g_route = d.groupby(key, dropna=False)["lsn_pax"].sum().sort_values(ascending=False)
            top_route = g_route.index[0] if len(g_route) else None
            top_route_pax = float(g_route.iloc[0]) if len(g_route) else 0.0

    # Growth metrics
    ts = d.groupby("date", dropna=False)["lsn_pax"].sum().reset_index()
    ts = ts.dropna(subset=["date"])
    yoy_pct = recent_yoy(ts, "lsn_pax")
    mom_pct = mom(ts, "lsn_pax")
    rec_2019 = recovery_vs_baseline_year(d, "lsn_pax", baseline_year=2019)
    growth_cagr = cagr(d, "lsn_pax")

    # Concentration of traffic by route
    if "route_pair" in d.columns:
        hhi_routes = hhi_concentration(d, "route_pair", "lsn_pax")
        top3_share = topn_share(d, "route_pair", "lsn_pax", 3)
    else:
        key = "route_dir" if "route_dir" in d.columns else ("lsn_seg" if "lsn_seg" in d.columns else None)
        hhi_routes = hhi_concentration(d, key, "lsn_pax") if key else np.nan
        top3_share = topn_share(d, key, "lsn_pax", 3) if key else np.nan

    return {
        "total_route_passengers": total_route_pax,
        "top_route": top_route,
        "top_route_pax": top_route_pax,
        "yoy_pct": yoy_pct,
        "mom_pct": mom_pct,
        "recovery_vs_2019_pct": rec_2019,
        "cagr": growth_cagr,
        "hhi_routes": hhi_routes,
        "top3_route_share": top3_share,
    }
