import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Professional Trading Journal", layout="wide")

st.title("📅 TradeZella-Style Performance Calendar")

file = st.file_uploader("Upload Capital.com CSV", type="csv")

if file:
    # 1. Load and Clean
    df = pd.read_csv(file)
    df['Full_Date'] = pd.to_datetime(df['Modified'], dayfirst=True)
    df['Date'] = df['Full_Date'].dt.date
    
    # Filter for only TRADE types
    trade_df = df[df['Type'] == 'TRADE'].copy()
    
    # 2. Aggregate Data by Date
    daily_stats = trade_df.groupby('Date').agg(
        Daily_PnL=('Amount', 'sum'),
        Trade_Count=('Amount', 'count')
    ).reset_index()
    
    # Convert back to datetime to extract calendar info
    daily_stats['Date_DT'] = pd.to_datetime(daily_stats['Date'])
    daily_stats['Week'] = daily_stats['Date_DT'].dt.isocalendar().week
    daily_stats['Day_Name'] = daily_stats['Date_DT'].dt.day_name()
    daily_stats['Day_Month'] = daily_stats['Date_DT'].dt.strftime('%b %d') # e.g., "Mar 24"

    # 3. Prepare the Grid
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Create a mapping for PnL, Count, and the Date Label
    pnl_map = daily_stats.set_index(['Week', 'Day_Name'])['Daily_PnL'].to_dict()
    count_map = daily_stats.set_index(['Week', 'Day_Name'])['Trade_Count'].to_dict()
    date_label_map = daily_stats.set_index(['Week', 'Day_Name'])['Day_Month'].to_dict()

    # Get unique weeks in the data
    weeks = sorted(daily_stats['Week'].unique())
    
    # Build the display DataFrame
    calendar_data = []
    for week in weeks:
        row = {}
        for day in days_order:
            key = (week, day)
            if key in pnl_map:
                label = date_label_map[key]
                pnl = pnl_map[key]
                count = count_map[key]
                row[day] = f"{label}\n\n€{pnl:,.2f}\n({int(count)} trades)"
            else:
                row[day] = "-"
        calendar_data.append(row)

    display_grid = pd.DataFrame(calendar_data, index=weeks)

    # 4. Styling Logic
    def style_cells(val):
        if "€" not in str(val):
            return 'background-color: #1e1e1e; color: #444; text-align: center;'
        
        # Check if profit or loss for color
        # We look for the minus sign in the string
        color = '#e74c3c' if "-" in val.split('\n\n')[1] else '#2ecc71'
        
        return f'''
            background-color: {color}; 
            color: white; 
            font-weight: bold; 
            border: 2px solid #111; 
            height: 100px; 
            white-space: pre; 
            text-align: center;
            vertical-align: middle;
        '''

    st.subheader("Monthly Performance & Volume")
    styled_table = display_grid.style.applymap(style_cells)
    st.table(styled_table)

    # 5. Professional Metrics Footer
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    total_pnl = trade_df['Amount'].sum()
    total_trades = len(trade_df)
    win_rate = (trade_df['Amount'] > 0).mean() * 100
    avg_trades = len(trade_df) / len(daily_stats) if len(daily_stats) > 0 else 0

    col1.metric("Total Net P&L", f"€{total_pnl:,.2f}")
    col2.metric("Total Trades", total_trades)
    col3.metric("Avg Trades / Day", f"{avg_trades:.1f}")
    col4.metric("Win Rate", f"{win_rate:.1f}%")

else:
    st.info("Drop your Capital.com Activity CSV here to see your calendar.")
