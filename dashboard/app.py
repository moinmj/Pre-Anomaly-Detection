import streamlit as st
import requests
import os

# Page config
st.set_page_config(page_title="Fraud Detection Dashboard", layout="centered")

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}/predict"

# Title
st.title("🚨 Fraud Detection Dashboard")
st.markdown("### 🧾 Enter Transaction Details")
st.markdown("Fill the details below to check fraud risk.")

# -------------------------------
# 🔹 USER INPUTS (WITH EXPLANATION)
# -------------------------------

income = st.number_input(
    "💰 Income",
    help="User's monthly income. Used to detect abnormal transactions.",
    value=50000
)

velocity_6h = st.number_input(
    "⚡ Activity in Last 6 Hours",
    help="Number of transactions in last 6 hours. High value = suspicious behavior.",
    value=10
)

velocity_24h = st.number_input(
    "📊 Activity in Last 24 Hours",
    help="Total transactions in last 24 hours.",
    value=20
)

device_fraud_count = st.number_input(
    "📱 Device Fraud History",
    help="Number of previous frauds linked to this device. 0 = safe, >0 = risky.",
    value=1
)

foreign_request = st.selectbox(
    "🌍 Foreign Transaction",
    [0, 1],
    format_func=lambda x: "Yes 🌐" if x == 1 else "No 🏠",
    help="Is the transaction coming from a foreign location?"
)

email_is_free = st.selectbox(
    "📧 Free Email Used",
    [0, 1],
    format_func=lambda x: "Yes (Gmail/Yahoo)" if x == 1 else "No (Corporate Email)",
    help="Free emails are easier to create and often used in fraud."
)

phone_home_valid = st.selectbox(
    "📞 Valid Phone Number",
    [0, 1],
    format_func=lambda x: "Valid ✅" if x == 1 else "Invalid ❌",
    help="Whether the user's phone number is verified."
)

# -------------------------------
# ℹ️ INFO BOX
# -------------------------------

st.info("""
ℹ️ **How Risk is Calculated**

- High activity (velocity) → suspicious  
- Fraud history (device) → very risky  
- Foreign transactions → higher risk  
- Free email & invalid phone → moderate risk  

👉 The system combines Machine Learning + Rule Engine to calculate risk score.
""")

# -------------------------------
# 🔹 DATA FOR API
# -------------------------------

data = {
    "income": income,
    "name_email_similarity": 0.8,
    "prev_address_months_count": 12,
    "current_address_months_count": 6,
    "customer_age": 30,
    "days_since_request": 2,
    "intended_balcon_amount": 1000,
    "payment_type": "credit",
    "zip_count_4w": 2,
    "velocity_6h": velocity_6h,
    "velocity_24h": velocity_24h,
    "velocity_4w": 50,
    "bank_branch_count_8w": 1,
    "date_of_birth_distinct_emails_4w": 1,
    "employment_status": "employed",
    "credit_risk_score": 300,
    "email_is_free": email_is_free,
    "housing_status": "rent",
    "phone_home_valid": phone_home_valid,
    "phone_mobile_valid": 1,
    "bank_months_count": 12,
    "has_other_cards": 1,
    "proposed_credit_limit": 5000,
    "foreign_request": foreign_request,
    "source": "mobile",
    "session_length_in_minutes": 5,
    "device_os": "android",
    "keep_alive_session": 0,
    "device_distinct_emails_8w": 2,
    "device_fraud_count": device_fraud_count,
    "month": 5
}

# -------------------------------
# 🔘 BUTTON
# -------------------------------

if st.button("🔍 Check Fraud Risk"):

    try:
        response = requests.post(API_URL, json=data)

        if response.status_code == 200:
            result = response.json()

            st.subheader("🔍 Result")

            # Risk Score
            st.metric("Risk Score", f"{result['risk_score']:.2f}")

            # Decision
            decision = result["decision"]

            if decision == "HIGH RISK":
                st.error("🚨 HIGH RISK TRANSACTION!\nImmediate action required.")
            elif decision == "MEDIUM RISK":
                st.warning("⚠️ Medium Risk.\nMonitor this transaction carefully.")
            else:
                st.success("✅ Safe Transaction.")

        else:
            st.error("❌ API Error. Please check backend.")

    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")