import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Config ---
st.set_page_config(page_title="Retail Store Dashboard", page_icon="🛍️", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    if os.path.exists('sales_data.csv'):
        return pd.read_csv('sales_data.csv')
    return None

df = load_data()

if df is None:
    st.error("⚠️ sales_data.csv not found! Please run generate_data.py first.")
    st.stop()

# --- Title and Overview ---
st.title("🛍️ Retail Store Sales Dashboard")
st.markdown("Interactive dashboard built to analyze daily store performance, track inventory, and find hidden demographic patterns.")

# Calculate top level metrics
total_revenue = df['total_amount (Rs.)'].sum()
total_items = df['quantity_sold'].sum()
busiest_day = df.groupby('day_of_week')['total_amount (Rs.)'].sum().idxmax()
top_product = df.groupby('product_name')['quantity_sold'].sum().idxmax()

# --- Metrics Row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
col2.metric("Items Sold", f"{total_items}")
col3.metric("Busiest Day", busiest_day)
col4.metric("Top Product", top_product)

st.markdown("---")

# --- Charts Section ---
st.subheader("📊 Visual Analytics")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 1. Day of Week Revenue
    st.markdown("**Revenue by Day of the Week**")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_sales = df.groupby('day_of_week')['total_amount (Rs.)'].sum().reindex(day_order).reset_index()
    fig_day = px.bar(day_sales, x='day_of_week', y='total_amount (Rs.)', 
                     color='total_amount (Rs.)', color_continuous_scale='Blues',
                     labels={'day_of_week': 'Day', 'total_amount (Rs.)': 'Revenue (Rs.)'})
    st.plotly_chart(fig_day, use_container_width=True)

with chart_col2:
    # 2. Size Inventory Health
    st.markdown("**Size Performance (Inventory Health)**")
    size_order = ['XS', 'S', 'M', 'L', 'XL']
    size_sales = df.groupby('size')['quantity_sold'].sum().reindex(size_order).reset_index()
    fig_size = px.funnel(size_sales, x='quantity_sold', y='size', 
                         color='size', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_size, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    # 3. Product Performance
    st.markdown("**Top & Bottom Products**")
    prod_sales = df.groupby('product_name')['quantity_sold'].sum().sort_values().reset_index()
    fig_prod = px.bar(prod_sales, x='quantity_sold', y='product_name', orientation='h',
                      color='quantity_sold', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_prod, use_container_width=True)

with chart_col4:
    # 4. Demographics
    st.markdown("**Who is buying what? (Age vs Category)**")
    demo_sales = df.groupby(['age_group', 'category'])['quantity_sold'].sum().reset_index()
    fig_demo = px.bar(demo_sales, x='age_group', y='quantity_sold', color='category', 
                      barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_demo, use_container_width=True)

st.markdown("---")

# --- AI Report Section ---
st.subheader("🤖 AI Generated Store Report")
st.markdown("The following report was generated dynamically by the LLM based on the data above.")

if os.path.exists('store_report.md'):
    with open('store_report.md', 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    with st.expander("📄 View Full AI Report (English & Hindi)", expanded=True):
        st.markdown(report_content)
else:
    st.warning("store_report.md not found. Run insight_engine.py to generate it.")
