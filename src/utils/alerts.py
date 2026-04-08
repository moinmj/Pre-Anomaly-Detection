import smtplib
from email.mime.text import MIMEText
import datetime
import os
import json


def _load_env_file(env_path=".env"):
    """Load key-value pairs from .env into environment variables if missing."""
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

# 🔥 Log file path (ONLY ONE)
LOG_PATH = os.path.join("logs", "fraud_logs.json")


# 🚨 EMAIL ALERT
def send_email_alert(risk_score, data):
    sender = os.getenv("EMAIL_SENDER", "moinmj7@gmail.com")
    password = os.getenv("EMAIL_PASSWORD")  # 🔒 use env variable in production
    receiver = os.getenv("EMAIL_RECEIVER", "moin.jan.mj@gmail.com")

    subject = "🚨 Fraud Alert Detected"
    body = f"""
    High Risk Transaction Detected!

    Risk Score: {risk_score}

    Transaction Data:
    {data}
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    if not password:
        print("[WARN] EMAIL_PASSWORD is not set. Skipping email alert.")
        return

    if not sender or not receiver:
        print("[WARN] EMAIL_SENDER or EMAIL_RECEIVER is not set. Skipping email alert.")
        return

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("[ALERT] Email sent successfully")
    except smtplib.SMTPAuthenticationError as e:
        print("[ERROR] Email authentication failed. Check EMAIL_SENDER and EMAIL_PASSWORD.", str(e))
    except Exception as e:
        print("[ERROR] Email failed:", e)


def log_transaction(risk_score, data):
    print("🔥 JSON LOGGER ACTIVE")

    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "risk_score": float(risk_score),
        "account_id": data.get("account_id", "unknown"),
        "data": data
    }