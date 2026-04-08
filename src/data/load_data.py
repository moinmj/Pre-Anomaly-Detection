import pandas as pd
import numpy as np
import os


def _generate_synthetic_data():
    """Create a small synthetic dataset for local development when real data is missing."""
    print("[WARN] No data file found; generating synthetic sample data for development.")

    n = 100
    df = pd.DataFrame({
        "income": np.random.randint(20000, 150000, size=n),
        "velocity_6h": np.random.randint(0, 20, size=n),
        "velocity_24h": np.random.randint(0, 50, size=n),
        "velocity_4w": np.random.randint(10, 300, size=n),
        "device_fraud_count": np.random.randint(0, 3, size=n),
        "foreign_request": np.random.randint(0, 2, size=n),
        "email_is_free": np.random.randint(0, 2, size=n),
        "phone_home_valid": np.random.randint(0, 2, size=n),
        "proposed_credit_limit": np.random.randint(500, 20000, size=n),
        "current_address_months_count": np.random.randint(1, 120, size=n),
        "prev_address_months_count": np.random.randint(0, 120, size=n),
        "payment_type": ["credit", "debit", "wire"] * (n // 3) + ["credit"] * (n % 3),
        "employment_status": ["employed", "self-employed", "unemployed"] * (n // 3) + ["employed"] * (n % 3),
        "housing_status": ["rent", "own", "mortgage"] * (n // 3) + ["rent"] * (n % 3),
        "source": ["mobile", "web", "branch"] * (n // 3) + ["mobile"] * (n % 3),
        "device_os": ["android", "ios"] * (n // 2) + ["android"] * (n % 2),
        "fraud_bool": np.random.randint(0, 2, size=n)
    })

    return df


def load_data(DATA_PATH: str = "data/raw/fraud_data.csv"):
    """
    Load dataset from given file path. Falls back to alternative paths or a synthetic dataset.

    Set actual data path via environment variable `DATA_PATH` if desired.
    """

    env_path = os.getenv("DATA_PATH")
    candidate_paths = [env_path, DATA_PATH, "data/raw/fraud_data.csv"]

    # Variants folder fallback (for legacy or existing local copies)
    variants = [
        "data/Variants/Variant I.csv",
        "data/Variants/Variant II.csv",
        "data/Variants/Variant III.csv",
        "data/Variants/Variant IV.csv",
        "data/Variants/Variant V.csv",
    ]

    candidate_paths.extend(variants)

    for path in candidate_paths:
        if path and os.path.exists(path):
            df = pd.read_csv(path)
            print(f"[INFO] Loaded data from: {path}, shape: {df.shape}")
            return df

    # All candidate paths failed: generate a small local sample to keep the pipeline runnable.
    return _generate_synthetic_data()