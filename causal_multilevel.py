
from pathlib import Path

import numpy as np
import pandas as pd

from econml.dml import LinearDML
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


DATA_PATH = Path("data/econocausal_synthetic_customers.csv")
OUTPUT_PATH = Path("outputs/customer_multilevel_dml_effects.csv")

FEATURES = [
    "age",
    "annual_income_inr",
    "past_purchases_12m",
    "days_since_last_purchase",
    "website_visits_30d",
    "email_engagement_score",
    "customer_segment",
    "region",
    "season",
]

DISCOUNT_LEVELS = [0, 5, 10, 20]


def load_and_validate_data():
    df = pd.read_csv(DATA_PATH)

    required = [
        "customer_id",
        "discount_percent",
        "purchased",
        *FEATURES,
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isnull().any().any():
        raise ValueError("Missing values found in required columns.")

    if df["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs found.")

    observed = sorted(df["discount_percent"].unique().tolist())
    if observed != DISCOUNT_LEVELS:
        raise ValueError(f"Expected {DISCOUNT_LEVELS}; found {observed}")

    if not set(df["purchased"].unique()).issubset({0, 1}):
        raise ValueError("'purchased' must contain only 0 and 1.")

    return df


def build_features(df):
    categorical = ["customer_segment", "region", "season"]
    numeric = [col for col in FEATURES if col not in categorical]

    transformer = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", numeric),
            (
                "categorical",
                OneHotEncoder(
                    drop="first",
                    handle_unknown="ignore"
                ),
                categorical,
            ),
        ]
    )

    return transformer.fit_transform(df[FEATURES])


def main():
    df = load_and_validate_data()
    X = build_features(df)

    # Treatment has four categories: 0%, 5%, 10%, and 20%.
    T = df["discount_percent"].to_numpy()
    Y = df["purchased"].to_numpy()

    cv = StratifiedKFold(
        n_splits=3,
        shuffle=True,
        random_state=42,
    )

    model = LinearDML(
        model_y=RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
        model_t=RandomForestClassifier(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
        discrete_treatment=True,
        categories=DISCOUNT_LEVELS,
        cv=cv,
        random_state=42,
    )
    model.fit(Y, T, X=X)
    results = pd.DataFrame({
        "customer_id": df["customer_id"],
    })

    summary = []

    # Compare every discount level against 0%.
    for level in [5, 10, 20]:
        effect = np.asarray(
            model.effect(X, T0=0, T1=level)
        ).reshape(-1)

        results[f"effect_{level}_vs_0_pp"] = effect * 100

        
        ate = float(np.mean(effect))

        lower, upper = model.ate_interval(
            X=X,
            T0=0,
            T1=level,
            alpha=0.05,
        )

        summary.append({
            "comparison": f"{level}% vs 0%",
            "ate_percentage_points": ate * 100,
            "ci_lower_pp": float(lower) * 100,
            "ci_upper_pp": float(upper) * 100,
        })


    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_PATH, index=False)

    print("Multi-level DML completed.")
    print(f"Customers analyzed: {len(results)}")
    print(f"Customer effects saved to: {OUTPUT_PATH}")
    print("\nEstimated average effects vs 0% discount:")
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
