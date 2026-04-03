import pandas as pd
import numpy as np

def preprocess_data(df: pd.DataFrame):
    print("[INFO] Starting preprocessing...")

    # 🔹 Clean data
    df = df.drop_duplicates()
    df = df.fillna(0)

    target = "fraud_bool"

    y = df[target]
    X = df.drop(columns=[target])

    # 🔥 Ensure required columns exist (SAFETY)
    required_cols = [
        "velocity_6h", "velocity_24h",
        "proposed_credit_limit", "income",
        "current_address_months_count", "prev_address_months_count"
    ]

    for col in required_cols:
        if col not in X.columns:
            X[col] = 0

    # 🔥 FEATURE ENGINEERING (SAFE)
# 🔥 FEATURE ENGINEERING
    X["velocity_ratio"] = X["velocity_6h"] / (X["velocity_24h"] + 1)
    X["credit_utilization"] = X["proposed_credit_limit"] / (X["income"] + 1)
    X["address_stability"] = X["current_address_months_count"] / (
        X["prev_address_months_count"] + 1
)

# 🔥 CRITICAL FIX (ADD THIS)
    X = X.replace([np.inf, -np.inf], 0)
    X = X.fillna(0)

    # 🔹 Categorical encoding
    categorical_cols = [
        "payment_type",
        "employment_status",
        "housing_status",
        "source",
        "device_os"
    ]

    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

    print("[INFO] Preprocessing completed")
    print(f"[INFO] Features shape: {X.shape}")

    return X, y