import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Professional Trading Journal", layout="wide")

st.title("📅 TradeZella-Style Performance Calendar")

file = st.file_uploader("Upload Capital.com CSV", type="csv")

if file:
    # 1. Load and Clean
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Modified'], dayfirst=True).dt.date
    
    # Filter for only TRADE types
    trade_df = df[df['Type'] == 'TRADE'].copy()
    
    # 2. Aggregate Data by Date
    # We calculate both the SUM of profit and the COUNT of trades
    daily_stats = trade_df.groupby('Date').agg(
        Daily_PnL=('Amount', 'sum'),
        Trade_Count=('Amount', 'count')
    ).reset_index()
    
    daily_stats['Date'] = pd.to_datetime(daily_stats['Date'])
    daily_stats['Week'] = daily_stats['Date'].dt.isocalendar().week
    daily_stats['Day'] = daily_stats['Date'].dt.day_name()

    # 3. Create two Grids: One for Money, One for Count
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    pnl_grid = daily_stats.pivot(index='Week', columns='Day', values='Daily_PnL')
    count_grid = daily_stats.pivot(index='Week', columns='Day', values='Trade_Count')

    # Ensure all days are present
    for day in days_order:
        if day not in pnl_grid.columns:
            pnl_grid[day] = np.nan
            count_grid[day] = 0
            
    pnl_grid = pnl_grid[days_order]
    count_grid = count_grid[days_order]

    # 4. Combine them into a "Display String" (e.g., "+€182.33 (5 trades)")
    display_grid = pnl_grid.copy().astype(str)
    for week in pnl_grid.index:
        for day in days_order:
            val = pnl_grid.loc[week, day]
            cnt = count_grid.loc[week, day]
            if pd.isna(val):
                display_grid.loc[week, day] = "-"
            else:
                display_grid.loc[week, day] = f"€{val:,.2f} \n ({int(cnt)} trades)"

    # 5. Styling Logic
    def style_cells(val):
        if "€" not in str(val):
            return 'background-color: #1e1e1e; color: #444;'
        # Extract number for coloring logic
        num_part = val.split(' ')[0].replace('€', '').replace(',', '')
        pnl_val = float(num_part)
        color = '#2ecc71' if pnl_val > 0 else '#e74c3c'
        return f'background-color: {color}; color: white; font-weight: bold; border: 2px solid #111; height: 80px;'

    st.subheader("Monthly Performance & Volume")
    styled_table = display_grid.style.applymap(style_cells)
    st.table(styled_table)

    # 6. Professional Metrics Footer
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    total_pnl = trade_df['Amount'].sum()
    total_trades = len(trade_df)
    avg_trades_per_day = daily_stats['Trade_Count'].mean()
    win_rate = (trade_df['Amount'] > 0).mean() * 100

    col1.metric("Total Net P&L", f"€{total_pnl:,.2f}")
    col2.metric("Total Trades", total_trades)
    col3.metric("Avg Trades / Day", f"{avg_trades_per_day:.1f}")
    col4.metric("Trade Win Rate", f"{win_rate:.1f}%")

else:
    st.info("Please upload your Capital.com Activity CSV.")
