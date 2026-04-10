import smtplib
from email.mime.text import MIMEText
import datetime
import os
import json

from src.models.customer_email_generator import generate_customer_email


# 🔥 Load ENV
def _load_env_file(env_path=".env"):
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and os.getenv(key) is None:
                os.environ[key] = value


_load_env_file()

LOG_PATH = os.path.join("logs", "fraud_logs.json")


# 🔥 COMMON MAIL SENDER
def _send_email(subject, body, receiver=None):
    sender = os.getenv("EMAIL_SENDER", "your_email@gmail.com")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = receiver or os.getenv("EMAIL_RECEIVER")

    if not password:
        print("[WARN] EMAIL_PASSWORD missing")
        return

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        print(f"📧 Email sent → {receiver}")

    except Exception as e:
        print("[ERROR] Email failed:", e)


# 🚨 1. MANAGER ALERT EMAIL
def send_manager_alert(risk_score, decision, reasons, account_id, data):
    approval_link = f"http://127.0.0.1:8000/approve?account_id={account_id}"
    disapprove_link = f"http://127.0.0.1:8000/disapprove?account_id={account_id}"

    body = f"""
🚨 FRAUD ALERT 🚨

Risk Level: {decision}
Risk Score: {round(risk_score, 2)}

Reasons:
{chr(10).join(["• " + r for r in reasons])}

-----------------------------
ACTION REQUIRED
-----------------------------

✅ Approve:
{approval_link}

❌ Disapprove:
{disapprove_link}

-----------------------------
Transaction Data:
{data}
"""

    _send_email("🚨 Fraud Alert - Action Required", body)


# 📧 2. CUSTOMER EMAIL DRAFT (TO MANAGER)
def send_customer_draft(customer_email_text):
    body = f"""
📧 CUSTOMER EMAIL PREVIEW

This email will be sent to the customer after approval:

---------------------------------------
{customer_email_text}
---------------------------------------
"""

    _send_email("📧 Customer Email Draft", body)


# 📧 3. FINAL CUSTOMER EMAIL
def send_customer_email(customer_email_text, customer_email_id=None):
    # ⚠️ Replace with real customer email logic later
    receiver = customer_email_id or "customer@example.com"

    _send_email("Important Account Notice", customer_email_text, receiver)


# 🔥 SMART ALERT TEXT (OPTIONAL)
def generate_smart_alert(risk_score, decision, reasons):
    alert = f"""
🚨 FRAUD ALERT 🚨

Risk Level: {decision}
Risk Score: {round(risk_score, 2)}

Reasons:
"""
    for r in reasons:
        alert += f"• {r}\n"

    return alert


# 📝 LOG TRANSACTION
def log_transaction(risk_score, data):
    print("🔥 JSON LOGGER ACTIVE")

    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "risk_score": float(risk_score),
        "account_id": data.get("account_id", "unknown"),
        "data": data
    }

    os.makedirs("logs", exist_ok=True)

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")