import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import pandas as pd
import plotly.express as px


API_URL = "http://api:8000"

st.set_page_config(page_title="Fraud Dashboard", layout="wide")

# 🔄 Auto refresh every 3 sec
st_autorefresh(interval=3000, key="datarefresh")

st.title("🚨 AI Fraud Detection Dashboard")

# -------------------------------
# 🔹 FETCH LIVE DATA
# -------------------------------
response = requests.get(f"{API_URL}/accounts")

if response.status_code == 200:
    data = response.json()
else:
    st.error("Backend not reachable")
    data = {}

# -------------------------------
# 📋 LIVE TRANSACTIONS TABLE
# -------------------------------
records = []

for acc_id, details in data.items():
    for txn in details["transactions"]:
        records.append({
            "account_id": acc_id,
            "velocity_6h": txn.get("velocity_6h"),
            "velocity_24h": txn.get("velocity_24h"),
            "decision": txn.get("decision", "N/A")
        })

df = pd.DataFrame(records)

st.header("📋 Live Transactions")
st.dataframe(df, use_container_width=True)

# -------------------------------
# 📊 ANALYTICS
# -------------------------------
if not df.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(df, x="decision", title="Decision Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.line(df, y="velocity_24h", title="Velocity Trend")
        st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# 👤 ACCOUNT VIEW
# -------------------------------
st.header("👤 Account Monitor")

accounts = list(data.keys())

selected_account = st.selectbox("Select Account", accounts)

if selected_account:
    acc = data[selected_account]

    st.subheader("📧 Customer Email Draft")
    st.write(acc.get("pending_email", "No email generated"))

    st.subheader("⚙️ Account Status")
    st.write(acc.get("status"))

    st.subheader("📊 Transactions")
    acc_df = pd.DataFrame(acc["transactions"])
    st.dataframe(acc_df)

    # -------------------------------
    # 🚨 ACTION BUTTONS
    # -------------------------------
    st.subheader("⚠️ Manager Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approve"):
            requests.get(f"{API_URL}/approve?account_id={selected_account}")
            st.success("Approved → Customer notified")

    with col2:
        if st.button("❌ Disapprove"):
            requests.get(f"{API_URL}/disapprove?account_id={selected_account}")
            st.warning("Marked safe")