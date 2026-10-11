
from pathlib import Path

import pandas as pd


# 1. Locate the project and dataset
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "econocausal_synthetic_customers.csv"
)


def load_data():
    """Load the customer dataset from the data folder."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        raise ValueError("The customer dataset is empty.")

    return df


def inspect_data(df):
    """Inspect dataset size, types, and data quality."""

    print("\n" + "=" * 60)
    print("1. DATASET OVERVIEW")
    print("=" * 60)

    print(f"Number of customers: {df.shape[0]}")
    print(f"Number of columns: {df.shape[1]}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values per column:")
    print(df.isnull().sum())

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    if "customer_id" in df.columns:
        print(
            "Duplicate customer IDs:",
            df["customer_id"].duplicated().sum()
        )


def analyze_discounts(df):
    """Compare outcomes across discount levels."""

    required_columns = [
        "discount_percent",
        "purchased",
        "basket_value_inr",
        "discount_cost_inr",
        "net_revenue_inr",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Check whether numeric columns contain valid numbers.
    numeric_columns = required_columns

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print("\n" + "=" * 60)
    print("2. DISCOUNT LEVEL ANALYSIS")
    print("=" * 60)

    summary = (
        df.groupby("discount_percent")
        .agg(
            customers=("customer_id", "size"),
            purchase_rate=("purchased", "mean"),
            avg_basket_value=("basket_value_inr", "mean"),
            avg_discount_cost=("discount_cost_inr", "mean"),
            avg_net_revenue=("net_revenue_inr", "mean"),
        )
        .reset_index()
        .sort_values("discount_percent")
    )

    # Convert purchase probability into a percentage.
    summary["purchase_rate"] *= 100

    print(
        summary.to_string(
            index=False,
            formatters={
                "purchase_rate": "{:.2f}%".format,
                "avg_basket_value": "₹{:,.2f}".format,
                "avg_discount_cost": "₹{:,.2f}".format,
                "avg_net_revenue": "₹{:,.2f}".format,
            },
        )
    )

    return summary


def analyze_treatment(df):
    """Compare customers who received discounts with those who did not."""

    print("\n" + "=" * 60)
    print("3. DISCOUNT RECEIVED VS NOT RECEIVED")
    print("=" * 60)

    summary = (
        df.groupby("discount_received")
        .agg(
            customers=("purchased", "size"),
            purchase_rate=("purchased", "mean"),
            avg_net_revenue=("net_revenue_inr", "mean"),
        )
        .reset_index()
    )

    summary["purchase_rate"] *= 100

    print(
        summary.to_string(
            index=False,
            formatters={
                "purchase_rate": "{:.2f}%".format,
                "avg_net_revenue": "₹{:,.2f}".format,
            },
        )
    )


def validate_causal_data(df):
    """Check whether treatment and outcome fields are consistent."""

    print("\n" + "=" * 60)
    print("4. CAUSAL DATA VALIDATION")
    print("=" * 60)

    # Check whether the discount indicator matches the percentage.
    expected_discount = (df["discount_percent"] > 0).astype(int)

    mismatch_count = (
        df["discount_received"] != expected_discount
    ).sum()

    print(
        f"Discount indicator mismatches: {mismatch_count}"
    )

    # Check the expected discount levels.
    valid_levels = {0, 5, 10, 20}

    unexpected_levels = sorted(
        set(df["discount_percent"].dropna()) - valid_levels
    )

    print(f"Unexpected discount levels: {unexpected_levels}")

    # Check the binary outcome.
    valid_purchase_values = {0, 1}

    unexpected_purchase_values = sorted(
        set(df["purchased"].dropna()) - valid_purchase_values
    )

    print(
        f"Unexpected purchase values: {unexpected_purchase_values}"
    )

    # Check financial calculations.
    expected_net_revenue = (
        df["basket_value_inr"] - df["discount_cost_inr"]
    )

    revenue_mismatches = (
        (df["net_revenue_inr"] - expected_net_revenue).abs() > 0.02
    ).sum()

    print(
        f"Net revenue calculation mismatches: {revenue_mismatches}"
    )



def main():
    print("ECONOCAUSAL - EXPLORATORY DATA ANALYSIS")

    df = load_data()

    inspect_data(df)

    summary = analyze_discounts(df)

    analyze_treatment(df)

    validate_causal_data(df)

    print("\n" + "=" * 60)
    print("EDA COMPLETED SUCCESSFULLY")
    print("=" * 60)

    return summary


if __name__ == "__main__":
    main()
