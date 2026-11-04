
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path("data/econocausal_synthetic_customers.csv")

OUTPUT_PATH = Path("outputs/propensity_overlap_diagnostics.csv")
SUMMARY_PATH = Path("outputs/propensity_overlap_summary.csv")

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

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

TREATMENT = "discount_percent"
TREATMENT_LEVELS = [0, 5, 10, 20]


def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = ["customer_id", TREATMENT] + FEATURES

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isnull().any().any():
        raise ValueError("Missing values found in required columns.")

    if df["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs found.")

    observed = sorted(df[TREATMENT].unique().tolist())

    if observed != TREATMENT_LEVELS:
        raise ValueError(
            f"Expected treatment levels {TREATMENT_LEVELS}, "
            f"found {observed}"
        )

    return df


def build_model():
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        min_samples_leaf=10,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("classifier", classifier),
        ]
    )


def main():
    df = load_data()

    X = df[FEATURES]
    T = df[TREATMENT]

    cv = StratifiedKFold(
        n_splits=3,
        shuffle=True,
        random_state=42,
    )

    model = build_model()

    # Generate out-of-fold treatment probabilities.
    probabilities = cross_val_predict(
        model,
        X,
        T,
        cv=cv,
        method="predict_proba",
        n_jobs=1,
    )

    results = pd.DataFrame({
        "customer_id": df["customer_id"],
        "actual_discount_percent": T,
    })

    for index, level in enumerate(TREATMENT_LEVELS):
        results[f"propensity_{level}"] = probabilities[:, index]

    propensity_columns = [
        f"propensity_{level}" for level in TREATMENT_LEVELS
    ]

    if not np.isfinite(probabilities).all():
        raise ValueError("Invalid propensity probabilities detected.")

    if not np.allclose(probabilities.sum(axis=1), 1.0):
        raise ValueError("Propensity probabilities do not sum to 1.")

    # Summarize the probability assigned to each customer's
    # actually received treatment.
    actual_propensity = np.array([
        probabilities[row, TREATMENT_LEVELS.index(level)]
        for row, level in enumerate(T)
    ])

    results["actual_treatment_propensity"] = actual_propensity

    summary = []

    for level in TREATMENT_LEVELS:
        group = results[
            results["actual_discount_percent"] == level
        ]

        values = group["actual_treatment_propensity"]

        summary.append({
            "discount_percent": level,
            "customer_count": len(group),
            "mean_propensity": values.mean(),
            "median_propensity": values.median(),
            "minimum_propensity": values.min(),
            "maximum_propensity": values.max(),
            "below_0_05": int((values < 0.05).sum()),
            "below_0_10": int((values < 0.10).sum()),
        })

    summary_df = pd.DataFrame(summary)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(OUTPUT_PATH, index=False)
    summary_df.to_csv(SUMMARY_PATH, index=False)

    print("\nPropensity Score Overlap Analysis Completed.")
    print(f"Customers analyzed: {len(results)}")
    print(f"Detailed results saved to: {OUTPUT_PATH}")
    print(f"Summary saved to: {SUMMARY_PATH}")

    print("\nTreatment propensity summary:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
