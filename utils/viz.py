from typing import List, Optional, Tuple, Dict, Sequence
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

try:
    import plotly.express as px
except Exception:  
    px = None

# Make Altair render faster in Streamlit
alt.data_transformers.disable_max_rows()


# Styling & helpers

PALETTE = [
    "#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
    "#14b8a6", "#6b7280", "#f43f5e", "#84cc16", "#eab308"
]

def _fmt(n, decimals: int = 0) -> str:
    try:
        return f"{n:,.{decimals}f}".replace(",", " ")
    except Exception:
        return str(n)

def _tooltip_fields(df: pd.DataFrame, cols: Sequence[str]) -> List[alt.Tooltip]:
    tips = []
    for c in cols:
        if c in df.columns:
            tips.append(alt.Tooltip(c, type="nominal" if df[c].dtype == "O" else "quantitative"))
    return tips


# LINE / AREA 

def line_trend(df, date_col, value_cols, title="", subtitle="", y_title="", bands=None):
    

    fig = go.Figure()

    # Plot each column
    for c in value_cols:
        if c in df.columns:
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df[c],
                mode="lines",
                name=c,
                line=dict(width=2)
            ))

    # Add COVID band or other shaded periods
    if bands:
        for (start, end, label) in bands:
            
            start = pd.to_datetime(start)
            end = pd.to_datetime(end)
            fig.add_vrect(
                x0=start,
                x1=end,
                fillcolor="red",
                opacity=0.1,
                layer="below",
                line_width=0,
            )
            fig.add_annotation(
                x=start + (end - start) / 2,
                y=df[value_cols[0]].max() * 0.95,
                text=label,
                showarrow=False,
                font=dict(color="red", size=12)
            )

    fig.update_layout(
        title=f"{title}<br><sup>{subtitle}</sup>",
        yaxis_title=y_title,
        template="simple_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)



def stacked_area_share(
    df: pd.DataFrame,
    date_col: str,
    category_col: str,
    value_col: str,
    title: str = "",
    normalize: bool = True,
    top_n: int = 15,
):
    """
    Stacked area (Plotly) with optional share normalization and top-N categories.
    JSON-safe for Streamlit Cloud.
    """
    need = {date_col, category_col, value_col}
    if df.empty or not need.issubset(df.columns):
        st.info("Not enough data for stacked area.")
        return

    d = df[list(need)].copy()

    # Coerce date to datetime (drop tz); category to str; value to float
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce").dt.tz_localize(None)
    d[category_col] = d[category_col].astype(str)
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")

    # Aggregate by date/category
    d = (
        d.groupby([date_col, category_col], dropna=False, as_index=False)[value_col]
        .sum()
    )

    # Keep top-N categories by total value over the whole period
    totals = d.groupby(category_col, as_index=False)[value_col].sum()
    keep = (
        totals.sort_values(value_col, ascending=False)
        .head(top_n)[category_col]
        .tolist()
    )
    d[category_col] = np.where(d[category_col].isin(keep), d[category_col], "Others")

    # Re-aggregate after lumping Others
    d = (
        d.groupby([date_col, category_col], as_index=False)[value_col]
        .sum()
        .sort_values([date_col, category_col])
    )

    # Normalize per date to shares if requested
    if normalize:
        d["__total__"] = d.groupby(date_col)[value_col].transform("sum")
        # guard against divide-by-zero
        d["share"] = np.where(d["__total__"] > 0, d[value_col] / d["__total__"], 0.0)
        y_col = "share"
        y_title = "Share"
        d.drop(columns=["__total__"], inplace=True)
    else:
        y_col = value_col
        y_title = value_col.replace("_", " ")

    # Replace NaN with None for safe JSON
    d = d.replace({np.nan: None}).reset_index(drop=True)

    fig = px.area(
        d,
        x=date_col,
        y=y_col,
        color=category_col,
        title=title or None,
    )
    if normalize:
        fig.update_yaxes(tickformat=".0%", range=[0, 1])

    fig.update_layout(
        height=420,
        xaxis_title="Date",
        yaxis_title=y_title,
        legend_title="",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)




# BAR / RANKINGS / DISTRIBUTIONS

def bar_top_n(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    n: int = 10,
    title: str = "",
    sort_desc: bool = True,
    annotate: bool = True
):
    """Horizontal top-N bar chart that is Arrow/Altair-agnostic (uses Plotly)."""
    if df.empty or not {category_col, value_col}.issubset(df.columns):
        st.info("No data to rank.")
        return

    
    d = df[[category_col, value_col]].copy()
    d[category_col] = d[category_col].astype(str)              
    # ensure purely numeric measure
    if "datetime" in str(d[value_col].dtype):
        d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    elif not np.issubdtype(d[value_col].dtype, np.number):
        d[value_col] = pd.to_numeric(d[value_col], errors="coerce")

    d = (
        d.groupby(category_col, dropna=False, as_index=False)[value_col]
         .sum()
         .sort_values(value_col, ascending=not sort_desc)
         .head(n)
         .replace({np.nan: 0.0})
    )

    # Plotly horizontal bars
    fig = px.bar(
        d,
        x=value_col,
        y=category_col,
        orientation="h",
        text=value_col if annotate else None,
        title=title or None,
    )

    # Style
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_layout(
        height=max(260, 28 * len(d)),
        xaxis_title=value_col,
        yaxis_title="",
        margin=dict(l=10, r=10, t=60, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)


def boxplot_distribution_px(
    df: pd.DataFrame,
    x_col: str,          
    y_col: str,          
    title: str = "",
    show_points: bool = True,
):
    """Distribution chart (box + optional points) using Plotly to avoid Arrow/Altair issues."""
    if df.empty or not {x_col, y_col}.issubset(df.columns):
        st.info("No data to plot.")
        return

    d = df[[x_col, y_col]].copy()

    # X should be simple numeric or string
    if "datetime" in str(d[x_col].dtype):
        d[x_col] = pd.to_datetime(d[x_col], errors="coerce")
        d[x_col] = d[x_col].dt.month

    # Coerce x to numeric if possible, else string
    if not np.issubdtype(d[x_col].dtype, np.number):
        coerced = pd.to_numeric(d[x_col], errors="coerce")
        if coerced.notna().any():
            d[x_col] = coerced.astype(float)
        else:
            d[x_col] = d[x_col].astype(str)

    # Y must be numeric
    d[y_col] = pd.to_numeric(d[y_col], errors="coerce")

    # Replace NaNs with None to be JSON-serializable
    d = d.replace({np.nan: None}).reset_index(drop=True)

    fig = px.box(
        d,
        x=x_col,
        y=y_col,
        points="all" if show_points else False,
        title=title or None,
    )
    fig.update_traces(marker=dict(size=4, opacity=0.35))
    fig.update_layout(
        height=420,
        xaxis_title=x_col.replace("_", " "),
        yaxis_title=y_col.replace("_", " "),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def scatter_with_size_color(
    df: pd.DataFrame,
    x: str,
    y: str,
    size_col: str | None = None,
    color_col: str | None = None,
    title: str = "",
    tooltip_cols: list[str] | None = None,
    legend_select: bool = True,             
    color_domain: list[str] | None = None,  
    color_range: list[str] | None = None,   
    top_n: int | None = None,               
):
    """Bubble scatter using Plotly (JSON-safe on Streamlit Cloud)."""
    need = {x, y}
    if df.empty or not need.issubset(df.columns):
        st.info("No data to plot.")
        return

    d = df.copy()

    # --- Coerce dtypes to JSON-safe ---
    # numeric axes
    d[x] = pd.to_numeric(d[x], errors="coerce")
    d[y] = pd.to_numeric(d[y], errors="coerce")
    if size_col and size_col in d.columns:
        d[size_col] = pd.to_numeric(d[size_col], errors="coerce")
    # color/category column as string
    if color_col and color_col in d.columns:
        d[color_col] = d[color_col].astype(str)
    # tooltips made safe
    if tooltip_cols:
        for c in tooltip_cols:
            if c in d.columns and not np.issubdtype(d[c].dtype, np.number):
                # stringify everything non-numeric to avoid complex objects (e.g., tuples)
                d[c] = d[c].astype(str)

    # Optional: restrict to top N (by size_col if provided, else by x)
    if top_n and top_n > 0:
        sort_key = size_col if size_col and size_col in d.columns else x
        d = d.sort_values(sort_key, ascending=False).head(top_n)

    # Replace NaN with None (JSON-friendly) and drop rows with missing axes
    d = d.replace({np.nan: None})
    d = d.dropna(subset=[x, y])

    # Fixed colors and stable legend order
    color_map = None
    category_orders = None
    if color_col and color_domain and color_range and len(color_domain) == len(color_range):
        color_map = {k: v for k, v in zip(color_domain, color_range)}
        category_orders = {color_col: color_domain}

    fig = px.scatter(
        d,
        x=x,
        y=y,
        size=size_col if size_col in d.columns else None,
        color=color_col if color_col in d.columns else None,
        hover_data=tooltip_cols if tooltip_cols else None,
        color_discrete_map=color_map,
        category_orders=category_orders,
        title=title or None,
    )

    # Improve readability
    fig.update_traces(marker=dict(opacity=0.75, line=dict(width=0)))
    fig.update_layout(
        height=420,
        xaxis_title=x.replace("_", " "),
        yaxis_title=y.replace("_", " "),
        margin=dict(l=10, r=10, t=50, b=10),
        legend_title="",
    )

    # Plotly legends already support click-to-hide; nothing else needed.
    st.plotly_chart(fig, use_container_width=True)





# MAPS — PyDeck

def map_bubbles(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    size_col: str = "passagers_total",
    tooltip_cols: Optional[List[str]] = None,   
    title: str = "Traffic by Airport (bubble size = passengers)",
    center: tuple = (46.5, 2.5),                # France center
    zoom: float = 4.5,                           
    initial_view_state: Optional[Dict] = None,
    radius_scale: float = 5.0
):
    """Bubble map using PyDeck. df must have latitude/longitude and a numeric size column."""
    # Basic guard
    needed = {lat_col, lon_col, size_col}
    if df.empty or not needed.issubset(df.columns):
        st.info("Map needs latitude, longitude, and the size column.")
        return

    # Clean data + bubble radius
    d = df.dropna(subset=[lat_col, lon_col]).copy()
    if d.empty:
        st.info("No points with valid coordinates to display.")
        return

    d["__radius"] = np.sqrt(np.clip(pd.to_numeric(d[size_col], errors="coerce").fillna(0), 0, None)) * radius_scale

    if tooltip_cols and len(tooltip_cols) >= 2:
        name_field = tooltip_cols[0]
        value_field = tooltip_cols[1]
        # single braces -> pydeck will substitute values
        tooltip_html = f"<b>{{{name_field}}}</b><br/>Passengers: {{{value_field}}}"
    elif tooltip_cols and len(tooltip_cols) == 1:
        only = tooltip_cols[0]
        tooltip_html = f"<b>{{{only}}}</b><br/>{size_col}: {{{size_col}}}"
    else:
        fallback_name = "nom_aeroport" if "nom_aeroport" in d.columns else None
        if fallback_name:
            tooltip_html = f"<b>{{{fallback_name}}}</b><br/>{size_col}: {{{size_col}}}"
        else:
            tooltip_html = f"<b>{{{lat_col}}}, {{{lon_col}}}</b><br/>{size_col}: {{{size_col}}}"

    tooltip = {
        "html": tooltip_html,
        "style": {"backgroundColor": "rgba(0,0,0,0.75)", "color": "white", "fontSize": "12px"}
    }


    # View state: center on France by default 
    view_state = pdk.ViewState(
        latitude=center[0],
        longitude=center[1],
        zoom=zoom,
        pitch=0,
        bearing=0
    )
    
    if initial_view_state:
        view_state = pdk.ViewState(**{**view_state.__dict__, **initial_view_state})

    
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=d,
        get_position=[lon_col, lat_col],
        get_radius="__radius",
        pickable=True,
        radius_min_pixels=2,
        radius_max_pixels=80,
        get_fill_color=[37, 99, 235, 160],  
        auto_highlight=True,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
    )

    if title:
        st.markdown(f"### {title}")
    st.pydeck_chart(deck, use_container_width=True)


# DATA QUALITY

def missingness_bar(df: pd.DataFrame, title: str = "Missing values by column"):
    if df.empty:
        st.info("No data.")
        return
    miss = df.isna().sum()
    miss = miss[miss > 0].sort_values(ascending=False).rename("missing").to_frame().reset_index().rename(columns={"index": "column"})
    if miss.empty:
        st.success("No missing values detected.")
        return
    ch = alt.Chart(miss).mark_bar().encode(
        x=alt.X("missing:Q", title="Missing cells"),
        y=alt.Y("column:N", sort="-x", title=""),
        tooltip=["column", "missing"]
    ).properties(title=title, height=max(240, 20 * len(miss)))
    st.altair_chart(ch, use_container_width=True)


# WHAT-IF / PROJECTION

def overlay_projection(df, date_col, value_col, pct_change=10, title="Projection", subtitle=None):
    if df.empty or date_col not in df.columns or value_col not in df.columns:
        return

    d = df[[date_col, value_col]].dropna()
    d = d.sort_values(date_col)

    # Simple linear projection from last point
    if d.empty:
        return
    last_date = pd.to_datetime(d[date_col].max())
    last_val = float(d[value_col].iloc[-1])

    proj_dates = pd.date_range(last_date, periods=13, freq="MS")  
    growth = 1 + (pct_change / 100.0)
    proj_vals = [last_val * (growth ** i) for i in range(len(proj_dates))]
    proj = pd.DataFrame({date_col: proj_dates, value_col: proj_vals})
    proj[value_col] = proj[value_col].astype(float)

    base = alt.Chart(d).mark_line().encode(
        x=alt.X(date_col, title="Date"),
        y=alt.Y(value_col, title=value_col.replace("_", " ").title()),
        color=alt.value("#1f77b4"),
        tooltip=[date_col, value_col]
    )

    future = alt.Chart(proj).mark_line(strokeDash=[4, 3]).encode(
        x=date_col, y=value_col, color=alt.value("#d62728"),
        tooltip=[date_col, value_col]
    )

    
    title_params = alt.TitleParams(title or "", anchor="start")
    if subtitle:  # only set when it's a non-empty string
        title_params.subtitle = subtitle

    chart = (base + future).properties(
        title=title_params,
        height=360
    )

    st.altair_chart(chart, use_container_width=True)



# PLOTLY (optional) — quick alternatives

def plotly_line(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, title: str = ""):
    if px is None:
        st.info("Plotly is not installed.")
        return
    fig = px.line(df, x=x, y=y, color=color, title=title)
    st.plotly_chart(fig, use_container_width=True)

def plotly_bar(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, title: str = ""):
    if px is None:
        st.info("Plotly is not installed.")
        return
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    st.plotly_chart(fig, use_container_width=True)
