
"""Support diagnostics for continuous discount treatment."""

import pandas as pd

DATA_PATH = "data/econocausal_synthetic_customers.csv"
TREATMENT = "discount_percent"

NUMERIC_FEATURES = [
    "age",
    "annual_income_inr",
    "past_purchases_12m",
    "days_since_last_purchase",
    "website_visits_30d",
    "email_engagement_score",
]

CATEGORICAL_FEATURES = [
    "customer_segment",
    "region",
    "season",
]


def run_overlap_diagnostics(data_path=DATA_PATH):
    df = pd.read_csv(data_path)

    required = [TREATMENT] + NUMERIC_FEATURES + CATEGORICAL_FEATURES
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Missing values found in diagnostic columns.")

    df[TREATMENT] = pd.to_numeric(df[TREATMENT], errors="coerce")

    if df[TREATMENT].isna().any():
        raise ValueError("Discount treatment must be numeric.")

    if (df[TREATMENT] < 0).any():
        raise ValueError("Discount values cannot be negative.")

    print("\n=== DISCOUNT SUPPORT ===")
    print("Rows:", len(df))
    print("Observed discount levels:", sorted(df[TREATMENT].unique()))

    print("\n=== NUMERIC FEATURE RANGE BY DISCOUNT ===")
    summary = df.groupby(TREATMENT)[NUMERIC_FEATURES].agg(["min", "max"])
    print(summary.to_string())

    print("\n=== CATEGORICAL SUPPORT ===")
    for feature in CATEGORICAL_FEATURES:
        table = pd.crosstab(
            df[feature],
            df[TREATMENT],
            normalize="columns",
        )
        print(f"\n{feature}:")
        print(table.round(3).to_string())

    print("\n=== DIAGNOSTIC NOTES ===")
    print(
        "These tables describe observed customer support at each discount level."
    )
    print(
        "They do not prove causal validity or establish continuous-treatment "
        "overlap by themselves."
    )
    print(
        "Check whether important customer groups have very few or no "
        "observations at particular discount levels."
    )

    return {
        "rows": len(df),
        "discount_counts": df[TREATMENT].value_counts().sort_index().to_dict(),
        "numeric_ranges": summary,
    }


if __name__ == "__main__":
    run_overlap_diagnostics()
