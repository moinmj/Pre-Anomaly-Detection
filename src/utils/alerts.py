import smtplib
from email.mime.text import MIMEText
import datetime
import os
import json

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

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("[ALERT] Email sent successfully")
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