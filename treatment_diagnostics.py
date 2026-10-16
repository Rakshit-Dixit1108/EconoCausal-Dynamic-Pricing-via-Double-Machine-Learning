
"""Basic overlap and covariate-balance diagnostics."""

import numpy as np
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


def standardized_mean_difference(group, comparison):
    """Calculate standardized mean difference for a numeric feature."""
    pooled_sd = np.sqrt(
        (group.var(ddof=1) + comparison.var(ddof=1)) / 2
    )

    if not np.isfinite(pooled_sd) or pooled_sd == 0:
        return np.nan

    return float((group.mean() - comparison.mean()) / pooled_sd)


def run_diagnostics(data_path=DATA_PATH):
    df = pd.read_csv(data_path)

    required = (
        [TREATMENT]
        + NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Diagnostic columns contain missing values.")

    treatment = pd.to_numeric(df[TREATMENT], errors="coerce")

    if treatment.isna().any() or not np.isfinite(treatment).all():
        raise ValueError("Discount treatment must be finite numeric data.")

    if (treatment < 0).any():
        raise ValueError("Discount values cannot be negative.")

    df = df.copy()
    df[TREATMENT] = treatment

    levels = sorted(df[TREATMENT].unique())

    print("DATASET")
    print(f"Rows: {len(df)}")
    print(f"Observed discount levels: {levels}")

    print("\nDISCOUNT LEVEL COUNTS")
    print(df[TREATMENT].value_counts().sort_index().to_string())

    print("\nNUMERIC FEATURE MEANS BY DISCOUNT LEVEL")
    print(
        df.groupby(TREATMENT)[NUMERIC_FEATURES]
        .mean()
        .round(2)
        .to_string()
    )

    print("\nNUMERIC FEATURE BALANCE")
    print("SMD compares each discount level against all other rows.")
    print("Large absolute SMD values indicate observed feature imbalance.")

    rows = []

    for level in levels:
        group = df.loc[df[TREATMENT] == level]
        comparison = df.loc[df[TREATMENT] != level]

        for feature in NUMERIC_FEATURES:
            smd = standardized_mean_difference(
                group[feature], comparison[feature]
            )

            rows.append({
                "discount_level": level,
                "feature": feature,
                "smd_vs_all_other_levels": smd,
                "absolute_smd": abs(smd) if np.isfinite(smd) else np.nan,
            })

    balance = pd.DataFrame(rows)
    print(balance.round(3).to_string(index=False))

    print("\nCATEGORICAL FEATURE DISTRIBUTIONS")
    for feature in CATEGORICAL_FEATURES:
        print(f"\n{feature}:")
        proportions = pd.crosstab(
            df[TREATMENT], df[feature], normalize="index"
        )
        print(proportions.round(3).to_string())

    print(
        "\nInterpretation: these are descriptive balance checks, "
        "not proof of causal validity or a complete overlap test."
    )

    return {
        "discount_counts": df[TREATMENT].value_counts().sort_index(),
        "numeric_balance": balance,
    }


if __name__ == "__main__":
    run_diagnostics()
