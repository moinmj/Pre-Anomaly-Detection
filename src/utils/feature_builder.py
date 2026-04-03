from collections import defaultdict
from datetime import datetime, timedelta
import profile

# 🔥 Simulated user database (KYC)
user_profiles = {
    "user123": {
        "income": 50000,
        "credit_risk_score": 600,
        "email_is_free": 1,
        "phone_home_valid": 1
    },
    "user456": {
        "income": 80000,
        "credit_risk_score": 700,
        "email_is_free": 0,
        "phone_home_valid": 1
    }
}

# 🔥 Device fraud database
device_fraud_db = {
    "device_999": 1
}

# 🔥 Transaction history (for velocity)
account_transactions = defaultdict(list)


def build_features(data):
    # 🔹 Extract inputs safely
    account_id = str(data.get("account_id", "unknown")).lower()
    device_id = str(data.get("device_id", "unknown"))
    location = str(data.get("location", "India"))
    amount = float(data.get("amount", 1000))

    now = datetime.now()

    # 🔹 Get user profile (safe fallback)
    profile = user_profiles.get(account_id, {
        "income": 40000,
        "credit_risk_score": 500,
        "email_is_free": 1,
        "phone_home_valid": 1
    })

    # 🔹 Store transaction timestamp
    account_transactions[account_id].append(now)

    # 🔹 Compute velocity (time-based)
    last_6h = now - timedelta(hours=6)
    last_24h = now - timedelta(hours=24)
    last_4w = now - timedelta(weeks=4)

    history = account_transactions[account_id]

    velocity_6h = sum(1 for t in history if t >= last_6h)
    velocity_24h = sum(1 for t in history if t >= last_24h)
    velocity_4w = sum(1 for t in history if t >= last_4w)

    # 🔹 Device fraud check
    device_fraud_count = device_fraud_db.get(device_id, 0)

    # 🔹 Foreign transaction flag
    foreign_request = 0 if location.lower() == "india" else 1

    # 🔹 Final feature dictionary (MODEL INPUT FORMAT)
    return {
    # 🔥 CORE FEATURES (your logic)
    "income": profile["income"],
    "velocity_6h": velocity_6h,
    "velocity_24h": velocity_24h,
    "velocity_4w": velocity_4w,
    "device_fraud_count": device_fraud_count,
    "foreign_request": foreign_request,
    "credit_risk_score": profile["credit_risk_score"],
    "email_is_free": profile["email_is_free"],
    "phone_home_valid": profile["phone_home_valid"],
    "proposed_credit_limit": amount,
    "current_address_months_count": 12,
    "prev_address_months_count": 6,

    # 🔥 ADD ALL MISSING FEATURES (CRITICAL)
    "name_email_similarity": 0.5,
    "customer_age": 30,
    "days_since_request": 1,
    "intended_balcon_amount": amount,
    "zip_count_4w": 1,
    "bank_branch_count_8w": 1,
    "date_of_birth_distinct_emails_4w": 1,
    "phone_mobile_valid": 1,
    "bank_months_count": 12,
    "has_other_cards": 1,
    "session_length_in_minutes": 5,
    "keep_alive_session": 1,
    "device_distinct_emails_8w": 1,
    "month": 5
}