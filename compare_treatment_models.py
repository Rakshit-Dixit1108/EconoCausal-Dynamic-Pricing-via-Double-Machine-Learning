
"""Compare candidate models for predicting discount treatment."""

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = "data/econocausal_synthetic_customers.csv"

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

CATEGORICAL = ["customer_segment", "region", "season"]
NUMERIC = [col for col in FEATURES if col not in CATEGORICAL]


def main():
    df = pd.read_csv(DATA_PATH)

    X_raw = df[FEATURES]
    treatment = pd.to_numeric(
        df["discount_percent"], errors="raise"
    ).to_numpy(dtype=float)

    if X_raw.isna().any().any() or not np.isfinite(treatment).all():
        raise ValueError("Missing or invalid feature/treatment values found.")

    preprocessor = ColumnTransformer([
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            CATEGORICAL,
        ),
        ("numeric", StandardScaler(), NUMERIC),
    ])

    models = {
        "Random Forest leaf=10": RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
        "Random Forest leaf=3": RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
        "Extra Trees leaf=10": ExtraTreesRegressor(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
    }

    cv = KFold(n_splits=3, shuffle=True, random_state=42)
    results = []

    for name, model in models.items():
        pipeline = make_pipeline(preprocessor, model)
        predictions = cross_val_predict(
            pipeline, X_raw, treatment, cv=cv, n_jobs=1
        )

        results.append({
            "model": name,
            "r2": r2_score(treatment, predictions),
            "rmse": np.sqrt(
                mean_squared_error(treatment, predictions)
            ),
            "residual_mean": np.mean(treatment - predictions),
        })

    results_df = pd.DataFrame(results).sort_values(
        "r2", ascending=False
    )

    print("\n=== TREATMENT MODEL COMPARISON ===")
    print(results_df.round(4).to_string(index=False))
    print(
        "\nThese are predictive diagnostics only. The best score "
        "does not prove causal validity."
    )


if __name__ == "__main__":
    main()
