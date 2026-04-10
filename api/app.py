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
from src.utils.alerts import (send_manager_alert,send_customer_draft,send_customer_email,log_transaction)
from src.utils.account_monitor import (update_account,detect_mule_account,increment_fraud,is_account_blocked,increment_approval,get_approval_count,account_data)
from src.utils.feature_builder import build_features
from src.models.genai_engine import analyze_with_llm
from fastapi import Query
from src.models.customer_email_generator import generate_customer_email
import src.utils.account_monitor
print("USING FILE:", src.utils.account_monitor.__file__)
import src.utils.alerts
print("USING ALERTS FILE:", src.utils.alerts.__file__)
from src.utils.account_monitor import account_data

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
    account_id = data.get("account_id", "default_user")

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
    decision = None  # only set by GenAI or Hybrid
    # 🔥 Encoding
    df = pd.get_dummies(df)

    # 🔥 Align features
    df = df.reindex(columns=model_features, fill_value=0)
    print("DEBUG FEATURES:", df.iloc[0].to_dict())
    def run_ml(df):
        score = compute_risk_score(xgb_model, iso_model, df)[0]
        return float(np.nan_to_num(score))
    def run_genai_score(data):
        print("🚀 CALLING GENAI...")

        result = analyze_with_llm(data)

        print("GENAI RESULT:", result)

        if result["success"]:
            llm_data = result["parsed"]

            llm_score = float(llm_data["risk_score"])

            return llm_score, llm_data

        else:
            return None, None

    # def run_genai(data):

    
    #     print("🚀 CALLING GENAI...")
    #     result = analyze_with_llm(data)
    #     print("GENAI RESULT:", result)
    #     return result
    print("Entering prediction logic...")
    # 🔥 Prediction
    try:
        if mode == "ml":
            risk_score = run_ml(df)

        elif mode == "genai":
            llm_score, llm_data = run_genai_score(data)

            if llm_score is not None:
                risk_score = llm_score
                decision = llm_data["decision"]
                reasons = llm_data["reasons"]
            else:
                print("⚠️ GENAI FAILED → FALLBACK TO ML")
                risk_score = run_ml(df)
                reasons = ["GenAI failed, fallback to ML"]
        elif mode == "hybrid":
            print("🔥 HYBRID MODE STARTED")

            ml_score = run_ml(df)
            llm_score, llm_data = run_genai_score(data)

            print("ML SCORE:", ml_score)
            print("LLM SCORE:", llm_score)

            if llm_score is not None:
                # 🔥 AGREEMENT
                if abs(ml_score - llm_score) < 0.2:
                    print("✅ ML + LLM AGREEMENT")

                    risk_score = (ml_score + llm_score) / 2
                    reasons = llm_data["reasons"]
                    decision = llm_data["decision"]

                # 🔥 DISAGREEMENT
                else:
                    print("⚠️ ML + LLM DISAGREE → INVESTIGATION MODE")

                    risk_score = max(ml_score, llm_score)

                    reasons = [
                        "ML and GenAI disagreement detected",
                        f"ML Score: {ml_score}",
                        f"LLM Score: {llm_score}"
                    ] + llm_data["reasons"]

                    decision = "HIGH RISK"

            else:
                print("⚠️ GENAI FAILED → ML ONLY")

                risk_score = ml_score
                reasons = ["GenAI unavailable, used ML only"]
    except Exception as e:
        print("❌ ERROR IN GENAI/PIPELINE:", str(e))
        risk_score = run_ml(df)
        reasons = ["System fallback to ML"]

        
    # 🔥 Explainability
    if not reasons:
        reasons = explain_risk(df.iloc[0])

    if not reasons:
        reasons = ["No strong fraud signals detected"]

    # 🔥 Account ID
    account_id = data.get("account_id", "default_user")

    # 🔥 Update history
    update_account(account_id, data)

    # 🔥 Check if blocked
    if is_account_blocked(account_id):
        return {
            "risk_score": 1.0,
            "decision": "ACCOUNT BLOCKED 🚫",
            "reasons": ["Account blocked due to repeated fraudulent activity"]
        }

    # 🔥 Mule detection
    is_mule = detect_mule_account(account_id)

    # 🔥 Decision logic
    if is_mule:
        decision = "HIGH RISK (MULE ACCOUNT DETECTED)"

    elif decision is None:
        if risk_score > 0.6:
            decision = "HIGH RISK"
        elif risk_score > 0.4:
            decision = "MEDIUM RISK"
        else:
            decision = "SAFE"

    # 🔥 Log transaction
    log_transaction(risk_score, df.iloc[0].to_dict())

    approval_count = get_approval_count(account_id)

    if "HIGH RISK" in decision:

        # 🔥 AUTO MODE (after 2 approvals)
        if approval_count >= 2:
            print("⚡ AUTO MODE ACTIVATED")

            # ✅ Generate customer email (FIX ISSUE 4)
            customer_email = generate_customer_email(
                df.iloc[0].to_dict(),
                decision,
                reasons
            )

            # print("📨 EMAIL DATA:", {
            #     **df.iloc[0].to_dict(),
            #         "account_id": account_id
            #         })

            # ✅ Send proper customer email
            print("📧 GENERATING CUSTOMER EMAIL")

            customer_email = generate_customer_email(
                df.iloc[0].to_dict(),
                decision,
                reasons
            )

            # 🔥 Store for approval
            account_data[account_id]["pending_email"] = customer_email

            # 🔥 SEND 2 SEPARATE EMAILS
            send_manager_alert(
                risk_score,
                decision,
                reasons,
                account_id,
                df.iloc[0].to_dict()
            )

            send_customer_draft(customer_email)
            # ✅ Increment fraud count
            increment_fraud(account_id)

            # ✅ FORCE BLOCK CHECK (FIX ISSUE 5)
            if is_account_blocked(account_id):
                decision = "ACCOUNT BLOCKED 🚫"

        else:
            print("📧 GENERATING CUSTOMER EMAIL")

            customer_email = generate_customer_email(
                df.iloc[0].to_dict(),
                decision,
                reasons
            )

            # 🔥 Store temporarily (simple memory)
            account_data[account_id]["pending_email"] = customer_email

            # 🔥 Send 2 emails
            send_manager_alert(
                risk_score,
                decision,
                reasons,
                account_id,
                df.iloc[0].to_dict()
            )

            send_customer_draft(customer_email)
    # 🔥 Response
    return {
        "risk_score": risk_score,
        "decision": decision,
        "reasons": reasons
    }


@app.get("/approve")
def approve(account_id: str):

    print(f"✅ APPROVED: {account_id}")

    # 🔥 Get stored email
    customer_email = account_data[account_id].get("pending_email")

    if not customer_email:
        return {"error": "No pending email found"}

    # 🔥 Send to customer
    send_customer_email(customer_email)

    increment_approval(account_id)
    increment_fraud(account_id)

    return {
        "message": "Customer email sent successfully",
        "account_id": account_id
    }

@app.get("/disapprove")
def disapprove(account_id: str = Query(...)):
    return {
        "message": "Transaction marked safe by manager"
    }
from src.utils.account_monitor import account_data

@app.get("/accounts")
def get_accounts():
    return account_data