
"""
Treatment Balance Diagnostics

Run:
python -m backend.advanced_causal.diagnostics --data path/to/csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


FEATURES = [
    "age",
    "annual_income_inr",
    "past_purchases_12m",
    "days_since_last_purchase",
    "website_visits_30d",
    "email_engagement_score",
]

TREATMENT = "discount_percent"
LEVELS = [0, 5, 10, 20]


def standardized_mean_difference(a, b):
    a = pd.to_numeric(a, errors="coerce").dropna()
    b = pd.to_numeric(b, errors="coerce").dropna()

    if len(a) < 2 or len(b) < 2:
        return np.nan

    pooled_sd = np.sqrt(
        (a.var(ddof=1) + b.var(ddof=1)) / 2
    )

    if pooled_sd == 0 or np.isnan(pooled_sd):
        return np.nan

    return (a.mean() - b.mean()) / pooled_sd


def run_diagnostics(data_path):
    df = pd.read_csv(data_path)

    required = FEATURES + [TREATMENT]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required].copy()
    df[TREATMENT] = pd.to_numeric(df[TREATMENT], errors="coerce")
    df = df.dropna(subset=[TREATMENT])
    df = df[df[TREATMENT].isin(LEVELS)]

    reference = df[df[TREATMENT] == 0]

    if reference.empty:
        raise ValueError("No 0% discount control group found.")

    rows = []

    for level in LEVELS[1:]:
        treatment_group = df[df[TREATMENT] == level]

        for feature in FEATURES:
            smd = standardized_mean_difference(
                treatment_group[feature],
                reference[feature],
            )

            rows.append({
                "discount_level": level,
                "control_level": 0,
                "feature": feature,
                "smd": smd,
                "absolute_smd": abs(smd) if pd.notna(smd) else np.nan,
            })

    result = pd.DataFrame(rows)

    result["balance_status"] = np.where(
        result["absolute_smd"] < 0.10,
        "Balanced",
        "Potential imbalance",
    )

    output = Path("advanced_causal_results")
    output.mkdir(exist_ok=True)

    result.to_csv(
        output / "treatment_balance.csv",
        index=False,
    )

    print("\nTREATMENT BALANCE DIAGNOSTICS")
    print(result.to_string(index=False))
    print("\nSaved treatment_balance.csv")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    run_diagnostics(args.data)
