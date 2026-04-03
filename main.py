from src.data.load_data import load_data
from src.data.preprocess import preprocess_data
from src.models.train_model import train_models

DATA_PATH = "data/raw/fraud_data.csv"


def main():
    print("[INFO] Starting pipeline...")

    # 🔹 Load data
    df = load_data(DATA_PATH)

    print("[INFO] Data loaded successfully")
    print("[INFO] Shape:", df.shape)

    print("\n[INFO] Columns:")
    print(df.columns)

    # 🔹 Preprocess
    X, y = preprocess_data(df)

    print("\n[INFO] Final dataset ready")
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    print("\n[INFO] Fraud distribution:")
    print(y.value_counts())

    # 🔥 DEBUG: Ensure training is called
    print("\n[DEBUG] About to start model training...")

    # 🔹 Train models
    train_models(X, y)

    print("\n[DEBUG] Model training completed!")


if __name__ == "__main__":
    main()