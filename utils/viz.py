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
    legend_columns: int = 4,
    bottom_padding: int = 64,
):
    """Stacked area to show composition over time (market shares) with Top-N carriers and 'Others'."""
    needed = {date_col, category_col, value_col}
    if df.empty or not needed.issubset(df.columns):
        st.info("Not enough data for stacked area.")
        return

    
    d = df[[date_col, category_col, value_col]].copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna(subset=[date_col])

    
    totals = (
        d.groupby(category_col, dropna=False)[value_col]
         .sum()
         .sort_values(ascending=False)
    )
    top_list = totals.head(top_n).index.tolist()

    
    d[category_col] = np.where(d[category_col].isin(top_list), d[category_col], "Others")

    
    d = (
        d.groupby([date_col, category_col], as_index=False, dropna=False)[value_col]
         .sum()
    )

    
    y_enc = alt.Y(
        f"{value_col}:Q",
        stack="normalize" if normalize else "zero",
        title="Share" if normalize else value_col.replace("_", " ").title(),
        axis=alt.Axis(format="~%") if normalize else alt.Undefined,
    )

    # Chart
    chart = (
        alt.Chart(d)
        .mark_area()
        .encode(
            x=alt.X(f"{date_col}:T", title="Date", axis=alt.Axis(titlePadding=12, labelPadding=6)),
            y=y_enc,
            color=alt.Color(
                f"{category_col}:N",
                legend=alt.Legend(
                    title=None,
                    orient="top",
                    direction="horizontal",
                    columns=legend_columns,
                    labelLimit=1000,
                    symbolLimit=0,
                ),
            ),
            tooltip=[
                alt.Tooltip(f"{date_col}:T", title="Date"),
                alt.Tooltip(f"{category_col}:N", title="Carrier"),
                alt.Tooltip(f"{value_col}:Q", title="Passengers", format=",.0f"),
            ],
        )
        .properties(title=title, height=420, width="container")
        .configure(padding={"left": 5, "right": 5, "top": 5, "bottom": bottom_padding})
        .configure_axis(labelFontSize=12, titleFontSize=12)
        .configure_legend(labelFontSize=12)
    )

    st.altair_chart(chart, use_container_width=True)



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

# utils/viz.py
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

def boxplot_distribution_px(
    df: pd.DataFrame,
    x_col: str,          
    y_col: str,          
    title: str = "",
    show_points: bool = True,
):
    """Distribution chart (box + optional points) using Plotly (JSON-safe on Streamlit Cloud)."""
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


def boxplot_distribution(
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
    if "datetime" in str(d[x_col].dtype):
        d[x_col] = pd.to_datetime(d[x_col], errors="coerce")
  
    if not np.issubdtype(d[x_col].dtype, np.number):
        coerced = pd.to_numeric(d[x_col], errors="coerce")
        if coerced.notna().any():
            d[x_col] = coerced.astype("Int64").astype("float")  
        else:
            d[x_col] = d[x_col].astype(str)

   
    d[y_col] = pd.to_numeric(d[y_col], errors="coerce")
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
    size_col: Optional[str] = None,
    color_col: Optional[str] = None,
    title: str = "",
    tooltip_cols: Optional[List[str]] = None,
    legend_select: bool = True,
    color_domain: Optional[List[str]] = None,   
    color_range: Optional[List[str]] = None,    
    top_n: int = 15                              
):
    """Scatter plot showing top N categories by size or y-value."""
    if df.empty or x not in df.columns or y not in df.columns:
        return

    d = df.copy()

    # Select top N airlines by total passengers
    
    if color_col:
        metric = size_col or y
        totals = (
            d.groupby(color_col, dropna=False)[metric]
             .sum()
             .sort_values(ascending=False)
        )
        top_list = totals.head(top_n).index.tolist()
        d = d[d[color_col].isin(top_list)]


    # Tooltip and color setup
    tooltip = tooltip_cols or [c for c in [color_col, x, y, size_col] if c]

    if color_col:
        color_enc = alt.Color(
            f"{color_col}:N",
            legend=alt.Legend(title=color_col),
            scale=alt.Scale(
                domain=color_domain,
                range=color_range,
                clamp=True
            ) if (color_domain and color_range) else alt.Undefined,
            sort=color_domain if color_domain else alt.Undefined,
        )
    else:
        color_enc = alt.value("#1f77b4")

    # Build scatter chart
    base = alt.Chart(d).mark_circle(opacity=0.8).encode(
        x=alt.X(x, title=x.replace("_", " ")),
        y=alt.Y(y, title=y.replace("_", " ")),
        size=alt.Size(size_col, title=size_col.replace("_", " ")) if size_col else alt.value(60),
        color=color_enc,
        tooltip=tooltip,
    ).properties(title=title, height=420)

    
    # Enable interactive legend 
    if legend_select and color_col:
        sel = alt.selection_point(fields=[color_col], bind="legend")
        base = base.add_params(sel).encode(
            opacity=alt.condition(sel, alt.value(1), alt.value(0.15))
        )

    st.altair_chart(base.interactive(), use_container_width=True)




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
