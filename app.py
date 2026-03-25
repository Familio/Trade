import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Trading Journal", layout="wide")

st.title("📅 Persistent Trading Calendar")

# --- DATA PERSISTENCE LOGIC ---
# This block checks if we already have data in memory
if 'trading_data' not in st.session_state:
    st.session_state['trading_data'] = None

# 1. File Uploader
uploaded_file = st.file_uploader("Upload new Capital.com CSV to update", type="csv")

# If a new file is uploaded, update the "Permanent" memory
if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
    # Perform cleaning once and store it
    df_raw['Full_Date'] = pd.to_datetime(df_raw['Modified'], dayfirst=True)
    df_raw['Date'] = df_raw['Full_Date'].dt.date
    st.session_state['trading_data'] = df_raw[df_raw['Type'] == 'TRADE'].copy()
    st.success("New data loaded into memory!")

# --- DISPLAY LOGIC ---
# Only run the dashboard if there is something in memory
if st.session_state['trading_data'] is not None:
    trade_df = st.session_state['trading_data']
    
    # [Rest of your calendar logic here...]
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

    st.table(pd.DataFrame(calendar_data, index=weeks).style.applymap(lambda x: 'background-color: #2ecc71;' if '€' in str(x) and '-' not in str(x) else ('background-color: #e74c3c;' if '€' in str(x) else '')))

    # Bottom Metrics
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total P&L", f"€{trade_df['Amount'].sum():,.2f}")
    m2.metric("Total Trades", len(trade_df))
    m3.metric("Win Rate", f"{(trade_df['Amount'] > 0).mean()*100:.1f}%")

else:
    st.info("Your dashboard is currently empty. Please upload a CSV to begin.")
