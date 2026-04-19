import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Fraud Intelligence Dashboard", layout="wide")

st.title("🏦 AI Fraud Detection System")
st.markdown("### 🚨 Real-Time Transaction + Account Monitoring")

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


# 🔄 Refresh Button
if st.button("🔄 Refresh Data"):
    st.rerun()

df = load_data()

# =========================
# ❗ NO DATA CASE
# =========================
if df.empty:
    st.warning("⚠️ No transactions yet. Hit the API first.")
    st.stop()

# =========================
# 🔄 PREPROCESS
# =========================
df["timestamp"] = pd.to_datetime(df["timestamp"])

# =========================
# 📊 SECTION 1: TRANSACTIONS
# =========================
st.subheader("📊 Recent Transactions")
st.dataframe(df.tail(10), use_container_width=True)

# =========================
# 📈 SECTION 2: RISK GRAPH
# =========================
st.subheader("📈 Risk Score Trend")
st.line_chart(df.set_index("timestamp")["risk_score"])

# =========================
# 🚨 SECTION 3: HIGH RISK
# =========================
st.subheader("🚨 High Risk Transactions")

high_risk = df[df["risk_score"] > 0.6]

if high_risk.empty:
    st.success("No high risk transactions")
else:
    st.error(f"{len(high_risk)} High Risk Transactions Detected")
    st.dataframe(high_risk, use_container_width=True)

# =========================
# 👤 SECTION 4: ACCOUNT ANALYSIS (NEW 🔥)
# =========================
st.subheader("👤 Account Intelligence")

if "account_id" not in df.columns:
    st.warning("⚠️ account_id not found in logs. Add it to logging.")
else:
    account_summary = df.groupby("account_id").agg(
        total_transactions=("risk_score", "count"),
        avg_risk=("risk_score", "mean"),
        max_risk=("risk_score", "max")
    ).reset_index()

    # 🚨 Flag suspicious accounts
    account_summary["mule_flag"] = account_summary.apply(
        lambda row: "🚨 YES" if (row["total_transactions"] >= 3 and row["avg_risk"] > 0.5) else "NO",
        axis=1
    )

    st.dataframe(account_summary, use_container_width=True)

# =========================
# 🧠 SECTION 5: TOP SUSPICIOUS USERS
# =========================
st.subheader("🔥 Top Suspicious Accounts")

top_accounts = (
    df.groupby("account_id")["risk_score"]
    .mean()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.dataframe(top_accounts, use_container_width=True)

# =========================
# 📦 SECTION 6: RAW DATA
# =========================
with st.expander("📦 View Raw Data"):
    st.dataframe(df, use_container_width=True)