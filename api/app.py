from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np
import os
import json

from src.models.risk_scoring import compute_risk_score, explain_risk
from src.utils.alerts import send_email_alert, log_transaction
from src.utils.account_monitor import update_account, detect_mule_account
from src.utils.feature_builder import build_features

import src.utils.alerts
print("USING ALERTS FILE:", src.utils.alerts.__file__)

# 🔥 Load models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

xgb_model = joblib.load(os.path.join(BASE_DIR, "models/xgb_model.pkl"))
iso_model = joblib.load(os.path.join(BASE_DIR, "models/iso_model.pkl"))

# 🔥 Load feature columns
with open(os.path.join(BASE_DIR, "models/feature_columns.json")) as f:
    model_features = json.load(f)

print("MODEL FEATURES:", model_features)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Fraud Detection API Running"}


@app.post("/predict")
def predict(data: dict):


    # df = pd.DataFrame([data])
    features = build_features(data)
    print("Raw features from builder:", features)
    df = pd.DataFrame([features])

    # 🔥 STEP 3: Feature Engineering (ONLY derived ones)
    df["velocity_ratio"] = df["velocity_6h"] / (df["velocity_24h"] + 1)
    df["credit_utilization"] = df["proposed_credit_limit"] / (df["income"] + 1)
    df["address_stability"] = df["current_address_months_count"] / (
        df["prev_address_months_count"] + 1
    )

    # 🔥 Encoding
    df = pd.get_dummies(df)

    # 🔥 Align features
    df = df.reindex(columns=model_features, fill_value=0)
    print("DEBUG FEATURES:", df.iloc[0].to_dict())
    # 🔥 Prediction
    print("CALLING LOG FUNCTION NOW")
    risk_score = compute_risk_score(xgb_model, iso_model, df)[0]
    risk_score = float(np.nan_to_num(risk_score))

    # 🔥 Explainability
    reasons = explain_risk(df.iloc[0])
    if not reasons:
        reasons = ["No strong fraud signals detected"]

    # 🔥 Mule Detection
    account_id = data.get("account_id", "default_user")
    update_account(account_id, data)
    is_mule = detect_mule_account(account_id)

    # 🔥 Decision
    if is_mule:
        decision = "HIGH RISK (MULE ACCOUNT DETECTED)"
    elif risk_score > 0.6:
        decision = "HIGH RISK"
    elif risk_score > 0.4:
        decision = "MEDIUM RISK"
    else:
        decision = "SAFE"

    # 🔥 Log transaction
    log_transaction(risk_score, df.iloc[0].to_dict())

    # 🚨 Alert
    if "HIGH RISK" in decision:
        send_email_alert(risk_score, df.iloc[0].to_dict())

    # 🔥 Response
    return {
        "risk_score": risk_score,
        "decision": decision,
        "reasons": reasons
    }