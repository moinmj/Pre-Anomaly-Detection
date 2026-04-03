import pandas as pd
import os

def load_data(DATA_PATH: str):
    """
    Load dataset from given file path
    """

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"File not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print(f"[INFO] Loaded data with shape: {df.shape}")

    return df