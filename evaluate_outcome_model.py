
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path("data/econocausal_synthetic_customers.csv")
OUTPUT_PATH = Path("outputs/heldout_predictive_metrics.csv")

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
    "discount_percent",
]


def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = NUMERIC_FEATURES + CATEGORICAL_FEATURES + ["purchased"]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isnull().any().any():
        raise ValueError("Missing values found in required columns.")

    if set(df["purchased"].unique()) != {0, 1}:
        raise ValueError("'purchased' must contain both 0 and 1.")

    return df


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def evaluate_model(name, predictions, probabilities, y_test):
    predicted_labels = (predictions >= 0.5).astype(int)
    probabilities = np.clip(probabilities, 0, 1)

    return {
        "model": name,
        "accuracy": accuracy_score(y_test, predicted_labels),
        "balanced_accuracy": balanced_accuracy_score(
            y_test, predicted_labels
        ),
        "precision": precision_score(
            y_test, predicted_labels, zero_division=0
        ),
        "recall": recall_score(
            y_test, predicted_labels, zero_division=0
        ),
        "f1_score": f1_score(
            y_test, predicted_labels, zero_division=0
        ),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "brier_score": brier_score_loss(y_test, probabilities),
    }


def main():
    df = load_data()

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["purchased"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # Fit preprocessing only on training data.
    preprocessor = build_preprocessor()

    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # Baseline: RandomForestRegressor outcome model.
    baseline_model = RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )

    baseline_model.fit(X_train_transformed, y_train)

    baseline_predictions = baseline_model.predict(X_test_transformed)
    baseline_probabilities = np.clip(
        baseline_predictions, 0, 1
    )

    # Experiment 2: RandomForestClassifier outcome model.
    classifier_model = RandomForestClassifier(
        n_estimators=200,
        min_samples_leaf=10,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )

    classifier_model.fit(X_train_transformed, y_train)

    classifier_probabilities = classifier_model.predict_proba(
        X_test_transformed
    )[:, 1]

    results = [
        evaluate_model(
            "Baseline_RandomForestRegressor",
            baseline_predictions,
            baseline_probabilities,
            y_test,
        ),
        evaluate_model(
            "Classifier_RandomForestClassifier",
            classifier_probabilities,
            classifier_probabilities,
            y_test,
        ),
    ]

    results_df = pd.DataFrame(results)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(OUTPUT_PATH, index=False)

    print("\nHeld-out predictive evaluation completed.")
    print(f"Training customers: {len(X_train)}")
    print(f"Testing customers: {len(X_test)}")
    print(f"Results saved to: {OUTPUT_PATH}")

    print("\nModel comparison:")
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()
