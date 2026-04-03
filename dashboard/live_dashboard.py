import streamlit as st
import pandas as pd
import time
import json
import os

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")

st.title("🚨 Real-Time Fraud Monitoring Dashboard")

LOG_PATH = "logs/fraud_logs.json"


def load_data():
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame()

    data = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue

    return pd.DataFrame(data)


# 🔄 Auto-refresh
while True:
    df = load_data()

    if df.empty:
        st.warning("No transactions yet...")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # 🔥 Latest transactions
        st.subheader("📊 Recent Transactions")
        st.dataframe(df.tail(10), use_container_width=True)

        # 🔥 Risk Distribution
        st.subheader("📈 Risk Score Distribution")
        st.bar_chart(df["risk_score"])

        # 🔥 High Risk Alerts
        high_risk = df[df["risk_score"] > 0.6]

        st.subheader("🚨 High Risk Transactions")
        if high_risk.empty:
            st.success("No high risk detected")
        else:
            st.error(f"{len(high_risk)} High Risk Transactions Detected")
            st.dataframe(high_risk, use_container_width=True)

    time.sleep(3)
    st.rerun()