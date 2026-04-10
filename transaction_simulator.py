import requests
import time
import random

API_URL = "http://127.0.0.1:8000/predict"

while True:
    data = {
        "account_id": f"user{random.randint(1,5)}",
        "mode": "hybrid",
        "velocity_6h": random.randint(1, 50),
        "velocity_24h": random.randint(1, 50),
        "device_fraud_count": random.randint(0, 3),
        "foreign_request": random.choice([0, 1])
    }

    try:
        res = requests.post(API_URL, json=data)
        print("Sent:", data)
        print("Response:", res.json())
    except Exception as e:
        print("Error:", e)

    time.sleep(3)