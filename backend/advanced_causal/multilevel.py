
"""
Multilevel Discount Causal Analysis
EconoCausal + Kanya branch integration

Run:
python -m backend.advanced_causal.multilevel --data path/to/csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from econml.dml import LinearDML


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

TREATMENT = "discount_percent"
OUTCOME = "purchased"
DISCOUNT_LEVELS = [0, 5, 10, 20]


def load_data(data_path):
    df = pd.read_csv(data_path)

    required = FEATURES + [TREATMENT, OUTCOME]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing dataset columns: {missing}")

    df = df[required].copy()

    df[TREATMENT] = pd.to_numeric(df[TREATMENT], errors="coerce")
    df[OUTCOME] = pd.to_numeric(df[OUTCOME], errors="coerce")

    df = df.dropna(subset=[TREATMENT, OUTCOME])
    df = df[df[TREATMENT].isin(DISCOUNT_LEVELS)]
    df = df[df[OUTCOME].isin([0, 1])]

    return df


def run_multilevel_analysis(data_path):
    df = load_data(data_path)

    X = df[FEATURES]
    T = df[TREATMENT].astype(int)
    Y = df[OUTCOME].astype(int)

    numeric_features = X.select_dtypes(include="number").columns.tolist()
    categorical_features = [
        c for c in FEATURES if c not in numeric_features
    ]

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                numeric_features,
            ),
            (
                "categorical",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]),
                categorical_features,
            ),
        ]
    )

    X_processed = preprocessing.fit_transform(X)

    model_y = RandomForestClassifier(
        n_estimators=150,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )

    model_t = RandomForestClassifier(
        n_estimators=150,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )

    estimator = LinearDML(
        model_y=model_y,
        model_t=model_t,
        discrete_outcome=True,
        discrete_treatment=True,
        categories=DISCOUNT_LEVELS,
        cv=3,
        random_state=42,
    )

    estimator.fit(Y, T, X=X_processed)

    results = []

    # Compare each discount level with 0% discount.
    for discount in DISCOUNT_LEVELS[1:]:
        effects = estimator.effect(
            X_processed,
            T0=0,
            T1=discount,
        )

        ate = float(np.mean(effects))

        results.append({
            "discount_percent": discount,
            "control_discount": 0,
            "estimated_purchase_effect": ate,
            "effect_percentage_points": ate * 100,
        })

    result_df = pd.DataFrame(results)

    output_path = Path("advanced_causal_results")
    output_path.mkdir(exist_ok=True)

    result_df.to_csv(
        output_path / "multilevel_effects.csv",
        index=False,
    )

    print("\nMULTILEVEL DISCOUNT EFFECTS")
    print(result_df.to_string(index=False))
    print("\nSaved:", output_path / "multilevel_effects.csv")

    return result_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    run_multilevel_analysis(args.data)
