# import numpy as np
# def explain_risk(row):
#     reasons = []

#     if row["velocity_6h"] > 5:
#         reasons.append("High transaction activity in short time")

#     if row["device_fraud_count"] > 0:
#         reasons.append("Device previously involved in fraud")

#     if row["foreign_request"] == 1:
#         reasons.append("Transaction from foreign location")

#     if row["email_is_free"] == 1:
#         reasons.append("Using free email provider")

#     if row["phone_home_valid"] == 0:
#         reasons.append("Invalid phone number")

#     return reasons
# # def rule_engine(row):
# #     score = 0

# #     if row["velocity_6h"] > 5:
# #         score += 1

# #     if row["device_fraud_count"] > 0:
# #         score += 2

# #     if row["email_is_free"] == 1:
# #         score += 1

# #     if row["phone_home_valid"] == 0:
# #         score += 1

# #     if row["foreign_request"] == 1:
# #         score += 2

# #     return score
# import numpy as np

# def compute_risk_score(xgb_model, iso_model, X):
#     fraud_prob = xgb_model.predict_proba(X)[:, 1]
#     anomaly_score = iso_model.decision_function(X)

#     fraud_prob = np.nan_to_num(fraud_prob)
#     anomaly_score = np.nan_to_num(anomaly_score)

#     min_val = anomaly_score.min()
#     max_val = anomaly_score.max()

#     if max_val - min_val == 0:
#         anomaly_score = np.zeros_like(anomaly_score)
#     else:
#         anomaly_score = (anomaly_score - min_val) / (max_val - min_val)

#     base_score = 0.6 * fraud_prob + 0.4 * (1 - anomaly_score)

#     # 🔥 APPLY RULE ENGINE
#     rule_scores = np.array([rule_engine(row) for _, row in X.iterrows()])

#     # Normalize rule score
#     rule_scores = rule_scores / (rule_scores.max() + 1)

#     final_score = 0.5 * base_score + 0.5 * rule_scores

#     return np.nan_to_num(final_score)

import numpy as np


# -------------------------------
# 🔍 EXPLAINABILITY FUNCTION
# -------------------------------
def explain_risk(row):
    reasons = []

    # 🔥 High velocity (strong signal)
    if row.get("velocity_6h", 0) > 5:
        reasons.append("Unusual high transaction activity")

    # 🔥 Device fraud (strong signal)
    if row.get("device_fraud_count", 0) > 0:
        reasons.append("Device previously involved in fraud")

    # 🔥 Foreign + high amount (combined signal)
    if row.get("foreign_request", 0) == 1 and row.get("proposed_credit_limit", 0) > 10000:
        reasons.append("High-value foreign transaction")

    # 🔥 Free email + high activity (weak → strong combo)
    if row.get("email_is_free", 0) == 1 and row.get("velocity_6h", 0) > 3:
        reasons.append("Suspicious activity using free email")

    # 🔥 Invalid phone (moderate signal)
    if row.get("phone_home_valid", 1) == 0:
        reasons.append("Invalid or unverifiable phone number")

    # 🔥 Credit utilization anomaly
    if row.get("credit_utilization", 0) > 0.8:
        reasons.append("Unusually high credit usage")

    return reasons

# -------------------------------
# 🔥 RULE ENGINE (REQUIRED)
# -------------------------------
def rule_engine(row):
    score = 0

    if row["velocity_6h"] > 5:
        score += 1

    if row["device_fraud_count"] > 0:
        score += 2

    if row["email_is_free"] == 1:
        score += 1

    if row["phone_home_valid"] == 0:
        score += 1

    if row["foreign_request"] == 1:
        score += 2

    return score


# -------------------------------
# 🎯 FINAL RISK SCORE FUNCTION
# -------------------------------
def compute_risk_score(xgb_model, iso_model, X):

    # ML predictions
    fraud_prob = xgb_model.predict_proba(X)[:, 1]
    anomaly_score = iso_model.decision_function(X)

    # Handle NaN safely
    fraud_prob = np.nan_to_num(fraud_prob)
    anomaly_score = np.nan_to_num(anomaly_score)

    # Normalize anomaly score
    min_val = anomaly_score.min()
    max_val = anomaly_score.max()

    if max_val - min_val == 0:
        anomaly_score = np.zeros_like(anomaly_score)
    else:
        anomaly_score = (anomaly_score - min_val) / (max_val - min_val)

    # Base ML score
    base_score = 0.6 * fraud_prob + 0.4 * (1 - anomaly_score)

    # 🔥 Apply rule engine
    rule_scores = np.array([rule_engine(row) for _, row in X.iterrows()])

    # Normalize rule scores
    if rule_scores.max() > 0:
        rule_scores = rule_scores / (rule_scores.max() + 1)
    else:
        rule_scores = np.zeros_like(rule_scores)

    # Final hybrid score
    final_score = 0.5 * base_score + 0.5 * rule_scores

    return np.nan_to_num(final_score)