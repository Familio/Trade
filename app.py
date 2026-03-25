import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trading Heatmap", layout="wide")

st.title("📊 My Capital.com Performance")
st.markdown("Upload your **Activity Report** to see your weekly performance.")

# 1. File Uploader
file = st.file_uploader("Choose CSV", type="csv")

if file:
    df = pd.read_csv(file)
    
    # Capital.com columns are usually 'Close time' and 'Profit / Loss'
    # We clean the data to make it readable for the heatmap
    df['Date'] = pd.to_datetime(df['Close time']).dt.date
    df['Day'] = pd.to_datetime(df['Date']).dt.day_name()
    df['Week'] = pd.to_datetime(df['Date']).dt.isocalendar().week
    
    # Calculate P&L by Week and Day
    pivot = df.groupby(['Week', 'Day'])['Profit / Loss'].sum().reset_index()
    
    # Sort days so Monday comes first
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # 2. The Visual Heatmap
    fig = px.density_heatmap(
        pivot, x="Day", y="Week", z="Profit / Loss",
        color_continuous_scale="RdYlGn", 
        category_orders={"Day": days},
        text_auto=True,
        title="Weekly P&L Heatmap"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. Quick Stats
    win_rate = (df['Profit / Loss'] > 0).mean() * 100
    st.metric("Total Profit", f"${df['Profit / Loss'].sum():,.2f}")
    st.metric("Win Rate", f"{win_rate:.1f}%")
