# from turtle import mode

from unittest import result

from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np
import os
import json

# from xgboost import data

from src.models.risk_scoring import compute_risk_score, explain_risk
from src.utils.alerts import send_email_alert, log_transaction
from src.utils.account_monitor import update_account, detect_mule_account
from src.utils.feature_builder import build_features
from src.models.genai_engine import analyze_with_llm

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
    mode = data.get("mode", "ml")
    reasons=[]  # default = ml
    print("MODE:", mode)
    # 🔥 Encoding
    df = pd.get_dummies(df)

    # 🔥 Align features
    df = df.reindex(columns=model_features, fill_value=0)
    print("DEBUG FEATURES:", df.iloc[0].to_dict())
    def run_ml(df):
        score = compute_risk_score(xgb_model, iso_model, df)[0]
        return float(np.nan_to_num(score))


    def run_genai(data):

    
        print("🚀 CALLING GENAI...")
        result = analyze_with_llm(data)
        print("GENAI RESULT:", result)
        return result
    print("Entering prediction logic...")
    # 🔥 Prediction
    try:
        if mode == "ml":
            risk_score = run_ml(df)

        elif mode == "genai":
            result = run_genai(data)

            if result["success"]:
                llm_data = result["parsed"]
                risk_score = float(llm_data["risk_score"])
                decision = llm_data["decision"]
                reasons = llm_data["reasons"]
            else:
                print("GENAI FAILED -> FALLBACK TO ML")
                risk_score = run_ml(df)
        elif mode == "hybrid":
            result = run_genai(data)

            if result["success"]:
                print("HYBRID → GENAI USED")
                llm_output = result["output"]

                #Temporary risk score(can improve later)
                risk_score = 0.7

                #override reason with LLM explanation
                reasons=[llm_output]
            else:
                print("HYBRID → FALLBACK TO ML")
                risk_score = run_ml(df)

    except Exception as e:
        print("ERROR IN GENAI/PIPELINE:", str(e))
        # fallback safety

        risk_score = run_ml(df)

    
    # 🔥 Explainability (only if not set by GenAI)
    if "reasons" not in locals():
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
    elif "decision" not in locals():
        if risk_score > 0.6:
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