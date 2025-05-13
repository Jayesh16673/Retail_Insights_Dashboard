import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Retail Analytics", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")

    # Clean and convert currency columns
    money_columns = ['Cost Price', 'Retail Price', 'Profit Margin', 'Sub Total', 'Discount $', 'Order Total', 'Shipping Cost', 'Total']
    for col in money_columns:
        df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)

    df['Order Quantity'] = pd.to_numeric(df['Order Quantity'], errors='coerce')
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

    return df.dropna(subset=['Order Date'])

df = load_data()

# --- Sidebar Controls ---
st.sidebar.title("🔎 Filter & Controls")

chart_type = st.sidebar.selectbox("Choose Visualization", ["Pivot Table", "Bar Chart", "Line Chart", "Pie Chart", "Raw Data"])

groupby_cols = st.sidebar.multiselect("Group by", options=df.columns.tolist(), default=["State"])
value_col = st.sidebar.selectbox("Values (for analysis)", options=['Order Total', 'Profit Margin', 'Sub Total', 'Shipping Cost', 'Total'])

agg_func = st.sidebar.selectbox("Aggregation", options=["sum", "mean", "count"])

# --- Main View ---
st.title("📊 Retail Performance Dashboard")

# --- PIVOT TABLE ---
if chart_type == "Pivot Table":
    if groupby_cols:
        pivot_df = df.pivot_table(index=groupby_cols, values=value_col, aggfunc=agg_func)
        st.subheader("🧮 Pivot Table")
        st.dataframe(pivot_df.style.background_gradient(cmap='YlGnBu', axis=0))
    else:
        st.warning("Please select at least one 'Group by' column.")

# --- BAR CHART ---
elif chart_type == "Bar Chart":
    if groupby_cols:
        chart_df = df.groupby(groupby_cols)[value_col].agg(agg_func).reset_index()
        fig = px.bar(chart_df, x=groupby_cols[0], y=value_col, color=groupby_cols[1] if len(groupby_cols) > 1 else None,
                     title=f"{agg_func.capitalize()} of {value_col}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one 'Group by' column.")

# --- LINE CHART ---
elif chart_type == "Line Chart":
    df_sorted = df.sort_values("Order Date")
    time_group = st.sidebar.selectbox("Time Granularity", ["Monthly", "Quarterly", "Yearly"])
    
    if time_group == "Monthly":
        df_sorted['Period'] = df_sorted['Order Date'].dt.to_period("M").astype(str)
    elif time_group == "Quarterly":
        df_sorted['Period'] = df_sorted['Order Date'].dt.to_period("Q").astype(str)
    else:
        df_sorted['Period'] = df_sorted['Order Date'].dt.year

    line_df = df_sorted.groupby('Period')[value_col].agg(agg_func).reset_index()
    fig = px.line(line_df, x='Period', y=value_col, markers=True, title=f"{agg_func.capitalize()} of {value_col} over Time")
    st.plotly_chart(fig, use_container_width=True)

# --- PIE CHART ---
elif chart_type == "Pie Chart":
    if groupby_cols:
        pie_df = df.groupby(groupby_cols[0])[value_col].agg(agg_func).reset_index()
        fig = px.pie(pie_df, names=groupby_cols[0], values=value_col, title=f"{agg_func.capitalize()} of {value_col} by {groupby_cols[0]}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one 'Group by' column.")

# --- RAW DATA ---
elif chart_type == "Raw Data":
    st.subheader("📁 Raw Dataset")
    st.dataframe(df)

# --- Footer ---
st.markdown("---")
st.caption("Retail Dashboard by Streamlit ✨")
