import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Capital.com Dashboard", layout="wide")

st.title("📊 My Capital.com Performance")

file = st.file_uploader("Upload your CSV", type="csv")

if file:
    df = pd.read_csv(file)
    
    # 1. Clean Data based on your specific screenshot
    # We use 'Modified' for the date and 'Amount' for the P&L
    df['Date'] = pd.to_datetime(df['Modified'], dayfirst=True).dt.date
    df['Day'] = pd.to_datetime(df['Date']).dt.day_name()
    df['Week'] = pd.to_datetime(df['Date']).dt.isocalendar().week
    
    # 2. Filter: Only look at 'TRADE' rows (ignore Deposits/Withdrawals)
    trade_df = df[df['Type'] == 'TRADE'].copy()
    
    # 3. Create Pivot Table for Heatmap
    pivot = trade_df.groupby(['Week', 'Day'])['Amount'].sum().reset_index()
    
    # Sort days correctly
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # 4. Visual Heatmap
    fig = px.density_heatmap(
        pivot, x="Day", y="Week", z="Amount",
        color_continuous_scale="RdYlGn", 
        category_orders={"Day": days},
        text_auto=True,
        labels={'Amount': 'Profit/Loss (€)', 'Week': 'Week Number'},
        title="Weekly Profit/Loss Heatmap"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Summary Metrics
    c1, c2, c3 = st.columns(3)
    total_pl = trade_df['Amount'].sum()
    win_rate = (trade_df['Amount'] > 0).mean() * 100
    
    c1.metric("Total Trading P&L", f"€{total_pl:,.2f}")
    c2.metric("Win Rate", f"{win_rate:.1f}%")
    c3.metric("Total Trades", len(trade_df))

else:
    st.info("Awaiting CSV upload...")
