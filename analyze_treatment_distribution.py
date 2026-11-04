
from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/econocausal_synthetic_customers.csv")
OUTPUT_PATH = Path("outputs/treatment_distribution.csv")


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = ["discount_percent", "purchased"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isnull().any().any():
        raise ValueError("Missing values found.")

    counts = (
        df.groupby("discount_percent")
        .agg(
            customer_count=("purchased", "size"),
            purchase_count=("purchased", "sum"),
            purchase_rate=("purchased", "mean"),
        )
        .reset_index()
    )

    counts["customer_percentage"] = (
        counts["customer_count"] / len(df) * 100
    )

    counts["purchase_rate_percentage"] = (
        counts["purchase_rate"] * 100
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(OUTPUT_PATH, index=False)

    print("\nTreatment Distribution Analysis")
    print(counts.to_string(index=False))
    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
