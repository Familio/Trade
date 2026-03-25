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
    
    # 2. Advanced Aggregation
    # We calculate PnL, Total Trades, Wins, and Losses per day
    daily_stats = trade_df.groupby('Date').agg(
        Daily_PnL=('Amount', 'sum'),
        Total_Trades=('Amount', 'count'),
        Wins=('Amount', lambda x: (x > 0).sum()),
        Losses=('Amount', lambda x: (x <= 0).sum())
    ).reset_index()
    
    daily_stats['Date_DT'] = pd.to_datetime(daily_stats['Date'])
    daily_stats['Week'] = daily_stats['Date_DT'].dt.isocalendar().week
    daily_stats['Day_Name'] = daily_stats['Date_DT'].dt.day_name()
    daily_stats['Day_Month'] = daily_stats['Date_DT'].dt.strftime('%b %d')

    # 3. Build the Display Grid
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    weeks = sorted(daily_stats['Week'].unique())
    
    calendar_data = []
    for week in weeks:
        row = {}
        for day in days_order:
            day_data = daily_stats[(daily_stats['Week'] == week) & (daily_stats['Day_Name'] == day)]
            
            if not day_data.empty:
                d = day_data.iloc[0]
                # Format: Date | PnL | Total/Win/Loss
                cell_text = (
                    f"{d['Day_Month']}\n\n"
                    f"€{d['Daily_PnL']:,.2f}\n"
                    f"{int(d['Total_Trades'])} / {int(d['Wins'])}W / {int(d['Losses'])}L"
                )
                row[day] = cell_text
            else:
                row[day] = "-"
        calendar_data.append(row)

    display_grid = pd.DataFrame(calendar_data, index=weeks)

    # 4. Professional Styling
    def style_cells(val):
        if "€" not in str(val):
            return 'background-color: #1e1e1e; color: #444; text-align: center;'
        
        # Color based on PnL (look for the minus sign in the second line)
        pnl_line = val.split('\n\n')[1].split('\n')[0]
        color = '#e74c3c' if "-" in pnl_line else '#2ecc71'
        
        return f'''
            background-color: {color}; 
            color: white; 
            font-weight: bold; 
            border: 2px solid #111; 
            height: 120px; 
            white-space: pre; 
            text-align: center;
            vertical-align: middle;
        '''

    st.subheader("Monthly Performance & Win/Loss Ratio")
    st.table(display_grid.style.applymap(style_cells))

    # 5. Global Stats Footer
    st.divider()
    m1, m2, m3, m4, m5 = st.columns(5)
    
    total_pnl = trade_df['Amount'].sum()
    total_trades = len(trade_df)
    total_wins = (trade_df['Amount'] > 0).sum()
    total_losses = (trade_df['Amount'] <= 0).sum()
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0

    m1.metric("Total Net P&L", f"€{total_pnl:,.2f}")
    m2.metric("Total Trades", total_trades)
    m3.metric("Total Wins ✅", total_wins)
    m4.metric("Total Losses ❌", total_losses)
    m5.metric("Win Rate %", f"{win_rate:.1f}%")

else:
    st.info("Upload your CSV to generate your trading calendar.")
