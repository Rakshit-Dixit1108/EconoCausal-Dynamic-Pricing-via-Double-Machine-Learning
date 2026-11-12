
"""
Multilevel Discount Propensity Overlap

Run:
python -m backend.advanced_causal.propensity --data path/to/csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict


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
LEVELS = [0, 5, 10, 20]


def run_propensity_analysis(data_path):
    df = pd.read_csv(data_path)

    required = FEATURES + [TREATMENT]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required].copy()
    df[TREATMENT] = pd.to_numeric(df[TREATMENT], errors="coerce")
    df = df.dropna(subset=[TREATMENT])
    df = df[df[TREATMENT].isin(LEVELS)]

    X = df[FEATURES]
    T = df[TREATMENT].astype(int)

    numeric = X.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in FEATURES if c not in numeric]

    preprocessing = ColumnTransformer([
        (
            "numeric",
            SimpleImputer(strategy="median"),
            numeric,
        ),
        (
            "categorical",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]),
            categorical,
        ),
    ])

    model = Pipeline([
        ("preprocessing", preprocessing),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=150,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ])

    # Out-of-fold predictions avoid using in-sample propensity estimates.
    propensity = cross_val_predict(
        model,
        X,
        T,
        cv=3,
        method="predict_proba",
        n_jobs=1,
    )

    classes = np.unique(T)

    propensity_df = pd.DataFrame(
        propensity,
        columns=[f"propensity_{level}" for level in classes],
    )

    propensity_df["actual_discount"] = T.to_numpy()

    # Probability assigned to the customer's actual discount group.
    class_to_col = {
        level: f"propensity_{level}" for level in classes
    }

    propensity_df["actual_group_propensity"] = [
        propensity_df.iloc[i][class_to_col[level]]
        for i, level in enumerate(T.to_numpy())
    ]

    output = Path("advanced_causal_results")
    output.mkdir(exist_ok=True)

    propensity_df.to_csv(
        output / "propensity_scores.csv",
        index=False,
    )

    overlap_summary = (
        propensity_df.groupby("actual_discount")
        ["actual_group_propensity"]
        .agg(["count", "mean", "min", "max"])
        .reset_index()
    )

    overlap_summary.to_csv(
        output / "propensity_summary.csv",
        index=False,
    )

    print("\nPROPENSITY SUMMARY")
    print(overlap_summary.to_string(index=False))

    print("\nSaved propensity_scores.csv")
    print("Saved propensity_summary.csv")

    return propensity_df, overlap_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    run_propensity_analysis(args.data)
