import io
import json
import pandas as pd
import streamlit as st

from utils.io import load_apt_processed, load_cie_processed, load_lsn_processed, date_bounds
from utils.prep import (
    prep_apt, prep_cie, prep_lsn,
    missing_by_column,
    duplicate_keys_apt, duplicate_keys_cie, duplicate_keys_lsn,
    iqr_outliers
)
from utils.viz import missingness_bar


@st.cache_data(show_spinner=False)
def _load_all_prepped():
    """Load and prepare all datasets for quality checks."""
    apt = prep_apt(load_apt_processed())
    cie = prep_cie(load_cie_processed())
    lsn = prep_lsn(load_lsn_processed())
    return apt, cie, lsn


def _schema_box(df, title: str):
    issues = df.attrs.get("schema_issues", {}) if hasattr(df, "attrs") else {}
    with st.expander(title, expanded=False):
        if not issues:
            st.success("No schema issues recorded.")
            return

        missing = issues.get("missing", [])
        extras  = issues.get("extras", [])
        derived = issues.get("derived", [])

        if not missing and not extras:
            st.success("All expected columns found.")
            if derived:
                st.info(f"Derived/known extra columns (OK): {derived}")
            return

        if missing:
            st.error(f"Missing expected columns: {missing}")
        if extras:
            st.warning(f"Unexpected extra columns: {extras}")
        if derived:
            st.info(f"Derived/known extra columns (OK): {derived}")



def _date_coverage(df, label: str):
    """Show dataset temporal coverage."""
    rng = date_bounds(df)
    if rng:
        st.caption(f"**{label}** date coverage: {rng[0].date()} → {rng[1].date()}")
    else:
        st.caption(f"**{label}** date coverage: not available")


def _download_report_button(report_dict: dict, filename: str = "data_quality_report.json"):
    """Offer JSON download for quality summary."""
    data = json.dumps(report_dict, indent=2, ensure_ascii=False).encode("utf-8")
    st.download_button("Download full report (JSON)", data=data, file_name=filename, mime="application/json")


def render(start_date=None, end_date=None):
    st.title("Data Quality and Validation")
    st.caption("Quick checks to trust the data: missing values, duplicates, schema validation, and outliers.")

    apt, cie, lsn = _load_all_prepped()

    
    # Apply global date filter (from app.py)
    
    if start_date and end_date:
        if not apt.empty and "date" in apt.columns:
            apt = apt[(apt["date"] >= start_date) & (apt["date"] <= end_date)]
        if not cie.empty and "date" in cie.columns:
            cie = cie[(cie["date"] >= start_date) & (cie["date"] <= end_date)]
        if not lsn.empty and "date" in lsn.columns:
            lsn = lsn[(lsn["date"] >= start_date) & (lsn["date"] <= end_date)]

    
    # Date coverage
    
    st.markdown("### Date coverage")
    _date_coverage(apt, "APT (Airports)")
    _date_coverage(cie, "CIE (Airlines)")
    _date_coverage(lsn, "LSN (Routes)")

    
    # Schema issues
    
    st.markdown("### Schema validation")
    if not apt.empty:
        _schema_box(apt, "APT expected columns")
    if not cie.empty:
        _schema_box(cie, "CIE expected columns")
    if not lsn.empty:
        _schema_box(lsn, "LSN expected columns")

    
    # Missing data
    
    st.markdown("### Missing data overview")
    if not apt.empty:
        st.caption("APT missing values")
        missingness_bar(apt, title="APT missing values")
    if not cie.empty:
        st.caption("CIE missing values")
        missingness_bar(cie, title="CIE missing values")
    if not lsn.empty:
        st.caption("LSN missing values")
        missingness_bar(lsn, title="LSN missing values")

    
    # Duplicate keys
    
    st.markdown("### Duplicate keys")
    if not apt.empty:
        dups = duplicate_keys_apt(apt)
        st.write("**APT duplicates** (same year, month, airport code)")
        st.dataframe(dups.head(200) if not dups.empty else pd.DataFrame({"info": ["No duplicates found"]}))
    if not cie.empty:
        dups = duplicate_keys_cie(cie)
        st.write("**CIE duplicates** (same year, month, airline code)")
        st.dataframe(dups.head(200) if not dups.empty else pd.DataFrame({"info": ["No duplicates found"]}))
    if not lsn.empty:
        dups = duplicate_keys_lsn(lsn)
        st.write("**LSN duplicates** (same year, month, segment id)")
        st.dataframe(dups.head(200) if not dups.empty else pd.DataFrame({"info": ["No duplicates found"]}))

    
    # Outliers 
    
    st.markdown("### Outliers detection")
    ds_choice = st.selectbox("Pick a dataset", ["APT (airports)", "CIE (airlines)", "LSN (routes)"])

    if "APT" in ds_choice and not apt.empty:
        cols = [c for c in apt.columns if pd.api.types.is_numeric_dtype(apt[c])]
        col = st.selectbox("APT numeric column", cols or ["No numeric columns"])
        if cols:
            out = iqr_outliers(apt, col)
            st.write(f"Outliers in **{col}** (showing first 200 rows):")
            st.dataframe(out.head(200) if not out.empty else pd.DataFrame({"info": ["No outliers found by IQR"]}))

    elif "CIE" in ds_choice and not cie.empty:
        cols = [c for c in cie.columns if pd.api.types.is_numeric_dtype(cie[c])]
        col = st.selectbox("CIE numeric column", cols or ["No numeric columns"])
        if cols:
            out = iqr_outliers(cie, col)
            st.write(f"Outliers in **{col}** (showing first 200 rows):")
            st.dataframe(out.head(200) if not out.empty else pd.DataFrame({"info": ["No outliers found by IQR"]}))

    elif "LSN" in ds_choice and not lsn.empty:
        cols = [c for c in lsn.columns if pd.api.types.is_numeric_dtype(lsn[c])]
        col = st.selectbox("LSN numeric column", cols or ["No numeric columns"])
        if cols:
            out = iqr_outliers(lsn, col)
            st.write(f"Outliers in **{col}** (showing first 200 rows):")
            st.dataframe(out.head(200) if not out.empty else pd.DataFrame({"info": ["No outliers found by IQR"]}))

    
    # Export report
    
    st.markdown("### Export summary report")
    report = {
        "coverage": {
            "apt": [str(x) for x in date_bounds(apt)] if not apt.empty else None,
            "cie": [str(x) for x in date_bounds(cie)] if not cie.empty else None,
            "lsn": [str(x) for x in date_bounds(lsn)] if not lsn.empty else None,
        },
        "schema": {
            "apt": apt.attrs.get("schema_issues", {}) if hasattr(apt, "attrs") else {},
            "cie": cie.attrs.get("schema_issues", {}) if hasattr(cie, "attrs") else {},
            "lsn": lsn.attrs.get("schema_issues", {}) if hasattr(lsn, "attrs") else {},
        },
        "missing": {
            "apt": missing_by_column(apt).to_dict(orient="list") if not apt.empty else {},
            "cie": missing_by_column(cie).to_dict(orient="list") if not cie.empty else {},
            "lsn": missing_by_column(lsn).to_dict(orient="list") if not lsn.empty else {},
        },
        "duplicates": {
            "apt_rows": int(duplicate_keys_apt(apt).shape[0]) if not apt.empty else 0,
            "cie_rows": int(duplicate_keys_cie(cie).shape[0]) if not cie.empty else 0,
            "lsn_rows": int(duplicate_keys_lsn(lsn).shape[0]) if not lsn.empty else 0,
        },
    }

    _download_report_button(report, filename="data_quality_report.json")

    



if __name__ == "__main__":
    render()
