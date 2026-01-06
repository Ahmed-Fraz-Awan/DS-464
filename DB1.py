import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Retail Business Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">📊 Retail Business Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
This dashboard provides comprehensive insights into retail performance, customer behavior, and sales trends.
Use the filters in the sidebar to customize your view.
""")

# Load data function with caching
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cleaned_data.csv')
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("❌ cleaned_data.csv not found! Please run the data generator first.")
        st.stop()

# Load the data
df = load_data()

# Sidebar - Filters
st.sidebar.header("🔍 Filter Controls")

# Date range filter
if 'date' in df.columns:
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# Category filter
categories = sorted(df['category'].unique())
selected_categories = st.sidebar.multiselect(
    "🏷️ Categories",
    options=categories,
    default=categories
)

# Region filter
regions = sorted(df['region'].unique())
selected_regions = st.sidebar.multiselect(
    "🌍 Regions",
    options=regions,
    default=regions
)

# Channel filter
channels = sorted(df['channel'].unique())
selected_channels = st.sidebar.multiselect(
    "📱 Channels",
    options=channels,
    default=channels
)

# Apply filters
filtered_df = df[
    (df['category'].isin(selected_categories)) &
    (df['region'].isin(selected_regions)) &
    (df['channel'].isin(selected_channels))
]

# Display dataset info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dataset Info")
st.sidebar.info(f"""
**Records:** {len(filtered_df):,}

**Date Range:**  
{filtered_df['date'].min().strftime('%b %d, %Y')} - {filtered_df['date'].max().strftime('%b %d, %Y')}

**Categories:** {len(filtered_df['category'].unique())}
**Regions:** {len(filtered_df['region'].unique())}
""")

# Main content area
st.markdown('<h2 class="sub-header">📈 Key Performance Indicators (KPIs)</h2>', unsafe_allow_html=True)

# KPI Metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_df['revenue'].sum()
    st.metric(
        label="Total Revenue",
        value=f"${total_revenue:,.2f}",
        help="Sum of all revenue from filtered transactions"
    )

with col2:
    avg_order_value = filtered_df['revenue'].mean()
    st.metric(
        label="Average Order Value",
        value=f"${avg_order_value:,.2f}",
        help="Average revenue per transaction"
    )

with col3:
    total_profit = filtered_df['profit'].sum()
    st.metric(
        label="Total Profit",
        value=f"${total_profit:,.2f}",
        help="Sum of all profit from filtered transactions"
    )

with col4:
    profit_margin = (filtered_df['profit'].sum() / filtered_df['revenue'].sum()) * 100
    st.metric(
        label="Profit Margin",
        value=f"{profit_margin:.1f}%",
        help="Overall profit margin percentage"
    )

# Transaction Metrics
col5, col6, col7, col8 = st.columns(4)

with col5:
    total_transactions = len(filtered_df)
    st.metric(
        label="Total Transactions",
        value=f"{total_transactions:,}",
        help="Number of transactions"
    )

with col6:
    avg_customer_satisfaction = filtered_df['customer_satisfaction'].mean()
    st.metric(
        label="Avg. Customer Satisfaction",
        value=f"{avg_customer_satisfaction:.1f}/5",
        help="Average customer rating (1-5 scale)"
    )

with col7:
    avg_quantity = filtered_df['quantity'].mean()
    st.metric(
        label="Avg. Quantity per Order",
        value=f"{avg_quantity:.1f}",
        help="Average number of items per transaction"
    )

with col8:
    total_customers = filtered_df['customer_segment'].nunique()
    st.metric(
        label="Customer Segments",
        value=total_customers,
        help="Number of unique customer segments"
    )

# Revenue Trends Over Time
st.markdown('<h2 class="sub-header">📅 Revenue Trends Over Time</h2>', unsafe_allow_html=True)

if 'date' in filtered_df.columns:
    # Daily revenue trend
    daily_revenue = filtered_df.groupby(filtered_df['date'].dt.date)['revenue'].sum().reset_index()
    
    fig1 = px.line(
        daily_revenue,
        x='date',
        y='revenue',
        title='Daily Revenue Trend',
        labels={'date': 'Date', 'revenue': 'Revenue ($)'}
    )
    fig1.update_traces(line_color='#3B82F6', line_width=3)
    fig1.update_layout(hovermode='x unified')
    
    # Monthly revenue trend
    filtered_df['month_year'] = filtered_df['date'].dt.strftime('%b %Y')
    monthly_revenue = filtered_df.groupby('month_year')['revenue'].sum().reset_index()
    
    fig2 = px.bar(
        monthly_revenue,
        x='month_year',
        y='revenue',
        title='Monthly Revenue',
        labels={'month_year': 'Month', 'revenue': 'Revenue ($)'},
        color='revenue',
        color_continuous_scale='Blues'
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

# Category and Region Analysis
st.markdown('<h2 class="sub-header">📊 Performance by Category & Region</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Revenue by category
    category_revenue = filtered_df.groupby('category')['revenue'].sum().sort_values(ascending=False)
    fig3 = px.pie(
        values=category_revenue.values,
        names=category_revenue.index,
        title='Revenue Distribution by Category',
        hole=0.4
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    # Revenue by region
    region_revenue = filtered_df.groupby('region')['revenue'].sum().sort_values(ascending=False)
    fig4 = px.bar(
        x=region_revenue.index,
        y=region_revenue.values,
        title='Revenue by Region',
        labels={'x': 'Region', 'y': 'Revenue ($)'},
        color=region_revenue.values,
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig4, use_container_width=True)

# Customer and Channel Analysis
st.markdown('<h2 class="sub-header">👥 Customer & Channel Insights</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Revenue by customer segment
    segment_revenue = filtered_df.groupby('customer_segment')['revenue'].sum().sort_values(ascending=False)
    fig5 = px.bar(
        x=segment_revenue.index,
        y=segment_revenue.values,
        title='Revenue by Customer Segment',
        labels={'x': 'Customer Segment', 'y': 'Revenue ($)'},
        color=segment_revenue.values,
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    # Revenue by channel
    channel_revenue = filtered_df.groupby('channel')['revenue'].sum().sort_values(ascending=False)
    fig6 = px.pie(
        values=channel_revenue.values,
        names=channel_revenue.index,
        title='Revenue Distribution by Channel',
        hole=0.3
    )
    st.plotly_chart(fig6, use_container_width=True)

# Profit Analysis
st.markdown('<h2 class="sub-header">💰 Profit Margin Analysis</h2>', unsafe_allow_html=True)

if 'profit_margin' in filtered_df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Profit margin by category
        margin_by_category = filtered_df.groupby('category')['profit_margin'].mean().sort_values(ascending=False)
        fig7 = px.bar(
            x=margin_by_category.index,
            y=margin_by_category.values,
            title='Average Profit Margin by Category',
            labels={'x': 'Category', 'y': 'Profit Margin (%)'},
            color=margin_by_category.values,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # Scatter plot: Revenue vs Profit
        fig8 = px.scatter(
            filtered_df,
            x='revenue',
            y='profit',
            color='category',
            title='Revenue vs Profit Relationship',
            labels={'revenue': 'Revenue ($)', 'profit': 'Profit ($)'},
            hover_data=['category', 'region', 'customer_segment']
        )
        st.plotly_chart(fig8, use_container_width=True)

# Payment Methods Analysis
st.markdown('<h2 class="sub-header">💳 Payment Method Analysis</h2>', unsafe_allow_html=True)

payment_analysis = filtered_df.groupby('payment_method').agg({
    'revenue': 'sum',
    'transaction_id': 'count',
    'customer_satisfaction': 'mean'
}).rename(columns={'transaction_id': 'transaction_count'}).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig9 = px.bar(
        payment_analysis,
        x='payment_method',
        y='revenue',
        title='Revenue by Payment Method',
        labels={'payment_method': 'Payment Method', 'revenue': 'Revenue ($)'},
        color='revenue',
        color_continuous_scale='Purples'
    )
    st.plotly_chart(fig9, use_container_width=True)

with col2:
    fig10 = px.scatter(
        payment_analysis,
        x='transaction_count',
        y='customer_satisfaction',
        size='revenue',
        color='payment_method',
        title='Payment Methods: Usage vs Satisfaction',
        labels={
            'transaction_count': 'Number of Transactions',
            'customer_satisfaction': 'Avg. Customer Satisfaction'
        },
        hover_name='payment_method'
    )
    st.plotly_chart(fig10, use_container_width=True)

# Data Table
st.markdown('<h2 class="sub-header">📋 Transaction Data Preview</h2>', unsafe_allow_html=True)

# Show/hide data table
show_data = st.checkbox("Show detailed transaction data")
if show_data:
    # Format columns for display
    display_df = filtered_df.copy()
    numeric_cols = ['unit_price', 'revenue', 'cost', 'profit', 'profit_margin']
    for col in numeric_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "customer_satisfaction": st.column_config.NumberColumn("Satisfaction", format="%.1f")
        }
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_transactions.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 1rem;">
    <p>📊 <strong>Retail Business Analytics Dashboard</strong> | Generated with Python & Streamlit</p>
    <p>Data updated from ETL pipeline | Total records analyzed: {:,}</p>
</div>
""".format(len(filtered_df)), unsafe_allow_html=True)