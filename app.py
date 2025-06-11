# app.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# CONFIGURATION
API_KEY = st.secrets["TORNSTATS_API_KEY"]
API_URL = f"https://api.tornstats.com/api/v1/stocks?key={API_KEY}"

# GET DATA
@st.cache_data(ttl=1800)  # Cache for 30 mins
def get_stock_data():
    r = requests.get(API_URL)
    data = r.json()
    rows = []
    for sid, d in data["stocks"].items():
        rows.append({
            "Stock ID": sid,
            "Name": d["name"],
            "Ticker": d["ticker"],
            "Price": d["price"],
            "Change 24h": d.get("change24h", 0),
            "Last Updated": d.get("updated")
        })
    return pd.DataFrame(rows)

# UI
st.title("📈 Torn City Stock Price Analyzer")
st.caption("Live from TornStats API")
df = get_stock_data()
df["Change 24h"] = df["Change 24h"].round(2)

# TREND DETECTION
df["Trend"] = df["Change 24h"].apply(
    lambda x: "📈 Uptrend" if x > 1 else "📉 Downtrend" if x < -1 else "➡️ Sideways"
)

# DISPLAY
st.dataframe(df.sort_values("Change 24h", ascending=False), use_container_width=True)
st.bar_chart(df.set_index("Ticker")["Change 24h"])

# SIGNALS
st.subheader("🟢 Buy Signals")
st.dataframe(df[df["Trend"] == "📈 Uptrend"][["Name", "Ticker", "Price", "Change 24h"]])

st.subheader("🔴 Sell Signals")
st.dataframe(df[df["Trend"] == "📉 Downtrend"][["Name", "Ticker", "Price", "Change 24h"]])
