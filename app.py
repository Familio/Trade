import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📅 TradeZella-Style Calendar")

file = st.file_uploader("Upload Capital.com CSV", type="csv")

if file:
    df = pd.read_csv(file)
    
    # 1. Data Processing
    df['Date'] = pd.to_datetime(df['Modified'], dayfirst=True).dt.date
    trade_df = df[df['Type'] == 'TRADE'].copy()
    
    # 2. Group by Date to get Daily P&L
    daily_stats = trade_df.groupby('Date')['Amount'].sum().reset_index()
    daily_stats['Date'] = pd.to_datetime(daily_stats['Date'])
    daily_stats['Week'] = daily_stats['Date'].dt.isocalendar().week
    daily_stats['Day'] = daily_stats['Date'].dt.day_name()
    
    # 3. Create the Calendar Grid
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    calendar_grid = daily_stats.pivot(index='Week', columns='Day', values='Amount')
    
    # Ensure all days are present and in order
    for day in days_order:
        if day not in calendar_grid.columns:
            calendar_grid[day] = np.nan
    calendar_grid = calendar_grid[days_order]

    # 4. Professional Styling (The "TradeZella" look)
    def style_pnl(val):
        if pd.isna(val):
            return 'background-color: #1e1e1e; color: #1e1e1e' # Dark for empty days
        color = '#2ecc71' if val > 0 else '#e74c3c' # Green or Red
        return f'background-color: {color}; color: white; font-weight: bold; border: 1px solid #2c3e50'

    st.subheader("Monthly Performance Grid")
    styled_calendar = calendar_grid.style.applymap(style_pnl).format("€{:,.2f}", na_rep="-")
    
    # Display the calendar
    st.table(styled_calendar)

    # 5. Bottom Stats
    st.divider()
    col1, col2, col3 = st.columns(3)
    total = trade_df['Amount'].sum()
    col1.metric("Net P&L", f"€{total:,.2f}", delta=f"{total:,.2f}")
    col2.metric("Winning Days", len(daily_stats[daily_stats['Amount'] > 0]))
    col3.metric("Losing Days", len(daily_stats[daily_stats['Amount'] < 0]))

else:
    st.info("Drop your CSV above to generate your calendar.")
