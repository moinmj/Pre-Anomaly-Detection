# imports
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import joblib

from src.models.risk_scoring import compute_risk_score
import json


# 🔥 ADD RULE ENGINE HERE
def rule_engine(row, risk_score):
    score = 0

    if row["velocity_6h"] > 5:
        score += 1

    if row["device_fraud_count"] > 0:
        score += 2

    if row["email_is_free"] == 1:
        score += 1

    if row["phone_home_valid"] == 0:
        score += 1

    if risk_score > 0.7:
        score += 2

    return score


# 🔥 MAIN TRAINING FUNCTION
def train_models(X, y):

# 🔥 Save feature columns
    with open("models/feature_columns.json", "w") as f:
        json.dump(X.columns.tolist(), f)

    print("[INFO] Feature columns saved!")
    print("[INFO] Splitting data...")

    # 🔹 Sampling
    X_sample = X.sample(n=200000, random_state=42)
    y_sample = y.loc[X_sample.index]

    X_train, X_test, y_train, y_test = train_test_split(
        X_sample, y_sample, test_size=0.2, random_state=42, stratify=y_sample
    )

    #  SMOTE (balance dataset)
    print("[INFO] Applying SMOTE...")
    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    #  Isolation Forest
    print("Training Isolation Forest...")
    iso_model = IsolationForest(contamination=0.01, random_state=42)
    iso_model.fit(X_train)

    #  XGBoost
    print("[INFO] Training XGBoost...")
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)

    # 🔥 LightGBM
    print("[INFO] Training LightGBM...")
    lgb_model = LGBMClassifier(
        n_estimators=200,
        class_weight='balanced',
        random_state=42
    )
    lgb_model.fit(X_train, y_train)

    # 🔍 Ensemble Predictions
    print("[ Evaluating Ensemble Model...")

    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    lgb_probs = lgb_model.predict_proba(X_test)[:, 1]

    # 🔥 Combine models
    final_probs = 0.5 * xgb_probs + 0.5 * lgb_probs

    # 🔥 Threshold tuning
    for t in [0.3, 0.5, 0.7]:
        y_pred = (final_probs > t).astype(int)
        print(f"\n[INFO] Threshold: {t}")
        print(classification_report(y_test, y_pred))

    # 🔥 Risk Scoring
    print("\n[INFO] Computing risk scores...")
    risk_scores = compute_risk_score(xgb_model, iso_model, X_test)

    print("\n[INFO] Sample Risk Scores:")
    print(risk_scores[:10])

    # 🔥 Alert Logic
    print("\n[INFO] Smart Alerts:")

    for i in range(100):
        row = X_test.iloc[i]
        risk = risk_scores[i]

        rule_score = rule_engine(row, risk)

        if rule_score >= 3:
            print(f"[ALERT] Account {i}")
            print(f"  Risk Score: {risk:.2f}")
            print(f"  Rule Score: {rule_score}")

    # 💾 Save models
    joblib.dump(xgb_model, "models/xgb_model.pkl")
    joblib.dump(lgb_model, "models/lgb_model.pkl")
    joblib.dump(iso_model, "models/iso_model.pkl")

    print("\n[INFO] Models saved successfully")

    return xgb_model, lgb_model, iso_model