from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import requests

DATA_FILE = Path("data/clean/ecommerce_features.csv")

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="SunnyX E-Commerce Sales Dashboard",
    layout="wide"
)

# -----------------------------
# Theme colors
# -----------------------------
PURPLE = "#6C3BD1"
DARK_PURPLE = "#4B1FA8"
LIGHT_PURPLE = "#F3ECFF"
YELLOW = "#F4C430"
LIGHT_YELLOW = "#FFF8DB"
TEXT_DARK = "#2B2B2B"
WHITE = "#FFFFFF"
SOFT_BG = "#FCFAFF"

# -----------------------------
# Custom styling
# -----------------------------
st.markdown(
    f"""
    <style>
    .main {{
        background-color: {SOFT_BG};
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3 {{
        color: {DARK_PURPLE};
        font-family: "Segoe UI", sans-serif;
    }}

    .dashboard-card {{
        background: linear-gradient(135deg, {LIGHT_PURPLE}, {LIGHT_YELLOW});
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #E7D9FF;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        color: {TEXT_DARK};
    }}

    .summary-banner {{
        background: linear-gradient(90deg, {DARK_PURPLE}, {PURPLE});
        padding: 1rem 1.2rem;
        border-radius: 16px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        margin-bottom: 1.2rem;
    }}

    .summary-title {{
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }}

    .summary-text {{
        font-size: 0.98rem;
        line-height: 1.5;
    }}

    .section-title {{
        color: {DARK_PURPLE};
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }}

    .small-note {{
        color: #5C5C5C;
        font-size: 0.95rem;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {LIGHT_PURPLE}, {LIGHT_YELLOW});
    }}

    div[data-testid="stDataFrame"] {{
        border: 2px solid #E4D4FF;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        background-color: white;
    }}

    div[data-testid="stDataFrame"] thead tr th {{
        background-color: #EEE3FF !important;
        color: {DARK_PURPLE} !important;
        font-weight: 700 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing file: {DATA_FILE}")
    return pd.read_csv(DATA_FILE)

# -----------------------------
# API
# -----------------------------
def get_exchange_rate(base="USD", target="PHP"):
    url = f"https://open.er-api.com/v6/latest/{base}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            return data["rates"].get(target)
    except Exception:
        return None
    return None

# -----------------------------
# Helper functions
# -----------------------------
def find_sales_column(df):
    candidates = ["sales", "sale", "revenue", "amount", "total_sales", "sales_amount"]
    for col in candidates:
        if col in df.columns:
            return col
    return None

def find_quantity_column(df):
    candidates = ["quantity", "qty", "units_sold", "order_quantity"]
    for col in candidates:
        if col in df.columns:
            return col
    return None

def find_category_column(df):
    candidates = ["category", "product_category", "item_category", "segment"]
    for col in candidates:
        if col in df.columns:
            return col
    for col in df.columns:
        if "category" in col.lower():
            return col
    return None

def find_product_column(df):
    candidates = ["product", "product_name", "item", "item_name", "product_title"]
    for col in candidates:
        if col in df.columns:
            return col
    for col in df.columns:
        low = col.lower()
        if "product" in low or "item" in low:
            return col
    return None

def find_region_column(df):
    candidates = ["region", "sales_region", "market_region"]
    for col in candidates:
        if col in df.columns:
            return col
    for col in df.columns:
        if "region" in col.lower():
            return col
    return None

def find_state_column(df):
    candidates = ["state", "province", "shipping_state", "customer_state"]
    for col in candidates:
        if col in df.columns:
            return col
    for col in df.columns:
        low = col.lower()
        if "state" in low or "province" in low:
            return col
    return None

def find_year_column(df):
    if "year" in df.columns:
        return "year"
    for col in df.columns:
        if col.lower() == "year":
            return col
    return None

# -----------------------------
# Prepare data
# -----------------------------
df = load_data()

sales_col = find_sales_column(df)
qty_col = find_quantity_column(df)
category_col = find_category_column(df)
product_col = find_product_column(df)
region_col = find_region_column(df)
state_col = find_state_column(df)
year_col = find_year_column(df)

filtered_df = df.copy()

# -----------------------------
# Header
# -----------------------------
st.markdown(
    f"""
    <h1 style='color:{PURPLE}; font-size:42px; font-weight:800; margin-bottom:0.2rem;'>
    SunnyX E-Commerce Sales Performance Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='font-size:18px; color:#5E5E74; margin-top:0;'>
    A business intelligence dashboard for analyzing sales trends, category performance,
    geographic patterns, and order behavior.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

st.markdown(
    """
    <div class="dashboard-card">
        <div class="section-title">Business Problem / Decision Context</div>
        <div class="small-note">
            E-commerce businesses need a clear way to monitor revenue trends, category performance,
            and order activity so they can make better decisions about product strategy, promotions,
            inventory planning, and geographic targeting. This dashboard transforms raw sales data
            into business insights by showing where revenue comes from, how sales behave over time,
            and which categories, regions, and states contribute most to performance.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Dashboard Filters")

if category_col:
    categories = sorted(filtered_df[category_col].dropna().astype(str).unique())
    selected_categories = st.sidebar.multiselect(
        "Select Category",
        categories,
        default=categories
    )
    if selected_categories:
        filtered_df = filtered_df[filtered_df[category_col].astype(str).isin(selected_categories)]

if region_col:
    regions = sorted(filtered_df[region_col].dropna().astype(str).unique())
    selected_regions = st.sidebar.multiselect(
        "Select Region",
        regions,
        default=regions
    )
    if selected_regions:
        filtered_df = filtered_df[filtered_df[region_col].astype(str).isin(selected_regions)]

if state_col:
    states = sorted(filtered_df[state_col].dropna().astype(str).unique())
    selected_states = st.sidebar.multiselect(
        "Select State",
        states,
        default=states
    )
    if selected_states:
        filtered_df = filtered_df[filtered_df[state_col].astype(str).isin(selected_states)]

if year_col:
    year_values = sorted(filtered_df[year_col].dropna().astype(int).unique())
    selected_years = st.sidebar.multiselect(
        "Select Year",
        year_values,
        default=year_values
    )
    if selected_years:
        filtered_df = filtered_df[filtered_df[year_col].astype("Int64").isin(selected_years)]

if "sales_segment" in filtered_df.columns:
    segments = sorted(filtered_df["sales_segment"].dropna().astype(str).unique())
    selected_segments = st.sidebar.multiselect(
        "Select Sales Segment",
        segments,
        default=segments
    )
    if selected_segments:
        filtered_df = filtered_df[filtered_df["sales_segment"].astype(str).isin(selected_segments)]

# -----------------------------
# KPI calculations
# -----------------------------
total_sales = filtered_df[sales_col].sum() if sales_col else None
total_qty = filtered_df[qty_col].sum() if qty_col else None
total_orders = len(filtered_df)
avg_order_value = filtered_df[sales_col].mean() if sales_col else None
num_categories = filtered_df[category_col].nunique() if category_col else None
exchange_rate = get_exchange_rate()

yoy_growth_text = "N/A"
if sales_col and year_col:
    yoy_sales = (
        filtered_df.groupby(year_col, as_index=False)[sales_col]
        .sum()
        .sort_values(year_col)
    )
    if len(yoy_sales) >= 2:
        prev_value = yoy_sales[sales_col].iloc[-2]
        curr_value = yoy_sales[sales_col].iloc[-1]
        if prev_value != 0:
            growth = ((curr_value - prev_value) / prev_value) * 100
            yoy_growth_text = f"{growth:,.1f}%"

# -----------------------------
# Executive summary banner
# -----------------------------
banner_sales = f"{total_sales:,.2f}" if total_sales is not None else "N/A"
banner_orders = f"{total_orders:,}"
banner_growth = yoy_growth_text

st.markdown(
    f"""
    <div class="summary-banner">
        <div class="summary-title">Executive Summary</div>
        <div class="summary-text">
            Total Sales: <b>{banner_sales}</b> &nbsp;&nbsp;|&nbsp;&nbsp;
            Total Orders: <b>{banner_orders}</b> &nbsp;&nbsp;|&nbsp;&nbsp;
            YoY Growth: <b>{banner_growth}</b>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Dataset preview
# -----------------------------
st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(10), width="stretch")

# -----------------------------
# KPI section
# -----------------------------
st.subheader("Key Performance Indicators")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Sales", f"{total_sales:,.2f}" if total_sales is not None else "N/A")
col2.metric("Total Quantity", f"{total_qty:,.0f}" if total_qty is not None else "N/A")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Avg Order Value", f"{avg_order_value:,.2f}" if avg_order_value is not None else "N/A")
col5.metric("Categories", f"{num_categories}" if num_categories is not None else "N/A")
col6.metric("USD to PHP", f"{exchange_rate:.2f}" if exchange_rate else "Unavailable")

# -----------------------------
# Chart colors
# -----------------------------
color_sequence = [PURPLE, YELLOW, DARK_PURPLE, "#A66CFF", "#FFD95A"]

# -----------------------------
# Charts row 1
# -----------------------------
chart_col1, chart_col2 = st.columns(2)

if sales_col and "month_name" in filtered_df.columns:
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    monthly_sales = filtered_df.groupby("month_name", as_index=False)[sales_col].sum()
    monthly_sales["month_name"] = pd.Categorical(
        monthly_sales["month_name"],
        categories=month_order,
        ordered=True
    )
    monthly_sales = monthly_sales.sort_values("month_name")

    fig1 = px.bar(
        monthly_sales,
        x="month_name",
        y=sales_col,
        title="Monthly Sales Trend",
        color_discrete_sequence=[PURPLE]
    )
    fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    chart_col1.plotly_chart(fig1, width="stretch")

if sales_col and category_col:
    category_sales = filtered_df.groupby(category_col, as_index=False)[sales_col].sum()
    category_sales = category_sales.sort_values(sales_col, ascending=False)

    fig2 = px.bar(
        category_sales,
        x=category_col,
        y=sales_col,
        title="Sales by Category",
        color=category_col,
        color_discrete_sequence=color_sequence
    )
    fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    chart_col2.plotly_chart(fig2, width="stretch")

# -----------------------------
# Charts row 2
# -----------------------------
chart_col3, chart_col4 = st.columns(2)

if sales_col and "sales_segment" in filtered_df.columns:
    segment_sales = filtered_df.groupby("sales_segment", as_index=False)[sales_col].sum()

    fig3 = px.pie(
        segment_sales,
        names="sales_segment",
        values=sales_col,
        title="Sales by Segment",
        color_discrete_sequence=color_sequence
    )
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    chart_col3.plotly_chart(fig3, width="stretch")

if sales_col and qty_col:
    fig4 = px.scatter(
        filtered_df,
        x=qty_col,
        y=sales_col,
        title="Quantity vs Sales",
        color_discrete_sequence=[YELLOW]
    )
    fig4.update_traces(marker=dict(size=9, line=dict(width=1, color=DARK_PURPLE)))
    fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    chart_col4.plotly_chart(fig4, width="stretch")

# -----------------------------
# Charts row 3
# -----------------------------
chart_col5, chart_col6 = st.columns(2)

if sales_col:
    fig5 = px.histogram(
        filtered_df,
        x=sales_col,
        nbins=30,
        title="Sales Distribution",
        color_discrete_sequence=[PURPLE]
    )
    fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    chart_col5.plotly_chart(fig5, width="stretch")

if product_col and sales_col:
    top_products = (
        filtered_df.groupby(product_col, as_index=False)[sales_col]
        .sum()
        .sort_values(sales_col, ascending=False)
        .head(10)
    )

    fig6 = px.bar(
        top_products,
        x=sales_col,
        y=product_col,
        orientation="h",
        title="Top 10 Products by Sales",
        color_discrete_sequence=[YELLOW]
    )
    fig6.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis={"categoryorder": "total ascending"}
    )
    chart_col6.plotly_chart(fig6, width="stretch")

# -----------------------------
# Geographic charts
# -----------------------------
geo_col1, geo_col2 = st.columns(2)

if sales_col and region_col:
    region_sales = (
        filtered_df.groupby(region_col, as_index=False)[sales_col]
        .sum()
        .sort_values(sales_col, ascending=False)
    )

    fig7 = px.bar(
        region_sales,
        x=region_col,
        y=sales_col,
        title="Sales by Region",
        color=region_col,
        color_discrete_sequence=color_sequence
    )
    fig7.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    geo_col1.plotly_chart(fig7, width="stretch")

if sales_col and state_col:
    state_sales = (
        filtered_df.groupby(state_col, as_index=False)[sales_col]
        .sum()
        .sort_values(sales_col, ascending=False)
        .head(10)
    )

    fig8 = px.bar(
        state_sales,
        x=sales_col,
        y=state_col,
        orientation="h",
        title="Top 10 States by Sales",
        color_discrete_sequence=[PURPLE]
    )
    fig8.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis={"categoryorder": "total ascending"}
    )
    geo_col2.plotly_chart(fig8, width="stretch")

# -----------------------------
# Year over year chart
# -----------------------------
if sales_col and year_col:
    st.subheader("Historical Performance Year over Year")

    yoy_sales = (
        filtered_df.groupby(year_col, as_index=False)[sales_col]
        .sum()
        .sort_values(year_col)
    )

    fig9 = px.line(
        yoy_sales,
        x=year_col,
        y=sales_col,
        markers=True,
        title="Year-over-Year Sales Performance",
        color_discrete_sequence=[DARK_PURPLE]
    )
    fig9.update_traces(line=dict(width=4), marker=dict(size=10, color=YELLOW))
    fig9.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig9, width="stretch")

# -----------------------------
# Insight summary
# -----------------------------
st.subheader("Dashboard Insight Summary")

insight_text = """
This dashboard highlights how sales performance is distributed across categories, time periods,
sales segments, and geographic areas. Decision-makers can use these insights to identify strong-performing
product lines, monitor changes in demand, compare regions and states, and support planning for marketing,
inventory, and business growth.
"""

st.markdown(
    f"""
    <div class="dashboard-card">
        <div class="small-note">{insight_text}</div>
    </div>
    """,
    unsafe_allow_html=True
)