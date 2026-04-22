import requests
import time
import random

API_URL = "http://api:8000/predict"

def send_transaction(payload):
    while True:
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            print("Sent:", payload)
            print("Response:", response.json())
            break
        except Exception as e:
            print("⏳ waiting for API response (LLM maybe slow)...", e)
            time.sleep(5)


while True:
    data = {
        "account_id": f"user{random.randint(1,5)}",
        "mode": "hybrid",
        "velocity_6h": random.randint(1, 50),
        "velocity_24h": random.randint(1, 50),
        "device_fraud_count": random.randint(0, 3),
        "foreign_request": random.choice([0, 1])
    }

    send_transaction(data)   # ✅ IMPORTANT FIX

    time.sleep(3)