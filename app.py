import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Professional Trading Journal", layout="wide")

st.title("📅 Persistent Performance Calendar")
st.markdown("Your data will stay visible until you close the browser tab or upload a new file.")

# --- DATA PERSISTENCE ---
if 'trading_data' not in st.session_state:
    st.session_state['trading_data'] = None

# 1. File Uploader
uploaded_file = st.file_uploader("Upload Capital.com CSV to Update", type="csv")

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
    df_raw['Full_Date'] = pd.to_datetime(df_raw['Modified'], dayfirst=True)
    df_raw['Date'] = df_raw['Full_Date'].dt.date
    # Store only Trade data in memory
    st.session_state['trading_data'] = df_raw[df_raw['Type'] == 'TRADE'].copy()
    st.success("Data updated successfully!")

# --- DISPLAY LOGIC ---
if st.session_state['trading_data'] is not None:
    trade_df = st.session_state['trading_data']
    
    # 2. Daily Aggregation
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

    # 3. Create the Calendar Grid
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    weeks = sorted(daily_stats['Week'].unique())
    
    calendar_data = []
    for week in weeks:
        row = {}
        for day in days_order:
            day_data = daily_stats[(daily_stats['Week'] == week) & (daily_stats['Day_Name'] == day)]
            if not day_data.empty:
                d = day_data.iloc[0]
                row[day] = f"{d['Day_Month']}\n\n€{d['Daily_PnL']:,.2f}\n{int(d['Total_Trades'])} / {int(d['Wins'])}W / {int(d['Losses'])}L"
            else:
                row[day] = "-"
        calendar_data.append(row)

    display_grid = pd.DataFrame(calendar_data, index=weeks)

    # 4. Styling
    def style_cells(val):
        if "€" not in str(val):
            return 'background-color: #1e1e1e; color: #444; text-align: center;'
        pnl_line = val.split('\n\n')[1].split('\n')[0]
        color = '#e74c3c' if "-" in pnl_line else '#2ecc71'
        return f'background-color: {color}; color: white; font-weight: bold; border: 2px solid #111; height: 120px; white-space: pre; text-align: center; vertical-align: middle;'

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
    st.info("No data in memory. Please upload your Capital.com Activity CSV.")
