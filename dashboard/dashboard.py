import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")

st.title("🚨 AI Fraud Detection Dashboard")

# -------------------------------
# 🔹 SIDEBAR INPUT
# -------------------------------
st.sidebar.header("🔍 Test Transaction")

account_id = st.sidebar.text_input("Account ID", "user123")

mode = st.sidebar.selectbox("Mode", ["ml", "genai", "hybrid"])

velocity_6h = st.sidebar.slider("Velocity 6h", 0, 100, 10)
velocity_24h = st.sidebar.slider("Velocity 24h", 0, 100, 10)
device_fraud_count = st.sidebar.slider("Device Fraud Count", 0, 10, 0)
foreign_request = st.sidebar.selectbox("Foreign Request", [0, 1])

# -------------------------------
# 🔹 SESSION STATE STORAGE
# -------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------
# 🔹 PREDICT BUTTON
# -------------------------------
if st.sidebar.button("🚀 Predict"):

    payload = {
        "account_id": account_id,
        "mode": mode,
        "velocity_6h": velocity_6h,
        "velocity_24h": velocity_24h,
        "device_fraud_count": device_fraud_count,
        "foreign_request": foreign_request
    }

    response = requests.post(f"{API_URL}/predict", json=payload)

    if response.status_code == 200:
        result = response.json()

        # Save history
        st.session_state.history.append({
            "account_id": account_id,
            "risk_score": result["risk_score"],
            "decision": result["decision"]
        })

        st.success("Prediction Complete")

        # -------------------------------
        # 🔹 RESULT DISPLAY
        # -------------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Risk Score", round(result["risk_score"], 2))

        with col2:
            st.metric("Decision", result["decision"])

        st.subheader("📌 Reasons")
        for r in result["reasons"]:
            st.write(f"• {r}")

        # -------------------------------
        # 🔥 ACTION BUTTONS
        # -------------------------------
        if "HIGH RISK" in result["decision"]:
            st.subheader("⚠️ Manager Action Required")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Approve"):
                    requests.get(f"{API_URL}/approve?account_id={account_id}")
                    st.success("Approved → Customer notified")

            with col2:
                if st.button("❌ Disapprove"):
                    requests.get(f"{API_URL}/disapprove?account_id={account_id}")
                    st.warning("Marked safe")

    else:
        st.error("API Error")

# -------------------------------
# 📊 ANALYTICS SECTION
# -------------------------------
st.header("📊 Fraud Analytics")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)

    col1, col2 = st.columns(2)

    # Risk Score Trend
    with col1:
        fig = px.line(df, y="risk_score", title="Risk Score Trend")
        st.plotly_chart(fig, use_container_width=True)

    # Decision Distribution
    with col2:
        fig2 = px.pie(df, names="decision", title="Decision Distribution")
        st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# 📋 TRANSACTION TABLE
# -------------------------------
st.header("📋 Transaction History")

if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

# -------------------------------
# 🚨 HIGH RISK ALERTS PANEL
# -------------------------------
st.header("🚨 High Risk Alerts")

if st.session_state.history:
    high_risk_df = pd.DataFrame(st.session_state.history)
    high_risk_df = high_risk_df[
        high_risk_df["decision"].str.contains("HIGH RISK")
    ]

    if not high_risk_df.empty:
        st.error("⚠️ High Risk Accounts Detected")
        st.dataframe(high_risk_df, use_container_width=True)
    else:
        st.success("No high-risk accounts")

# -------------------------------
# 👤 ACCOUNT VIEW
# -------------------------------
st.header("👤 Account Monitor")

selected_account = st.text_input("Enter Account ID to view history")

if selected_account:
    df = pd.DataFrame(st.session_state.history)
    acc_df = df[df["account_id"] == selected_account]

    if not acc_df.empty:
        st.dataframe(acc_df)

        fig = px.line(acc_df, y="risk_score", title="Account Risk Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for this account")