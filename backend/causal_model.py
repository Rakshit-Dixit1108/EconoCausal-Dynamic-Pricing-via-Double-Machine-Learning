
from pathlib import Path

import pandas as pd
import doubleml as dml

from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "econocausal_synthetic_customers.csv"
)


# ============================================================
# FEATURES
# ============================================================

# Features measured before treatment.
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


# ============================================================
# DATA LOADING AND VALIDATION
# ============================================================

def load_data():
    """Load and validate the data needed for causal estimation."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required = FEATURES + [
        "discount_received",
        "purchased",
    ]

    missing = sorted(set(required) - set(df.columns))

    if missing:
        raise ValueError(
            f"Required columns are missing: {missing}"
        )

    if df[required].isnull().any().any():
        raise ValueError(
            "Missing values exist in the modeling columns."
        )

    # Validate numeric features.
    for column in NUMERIC_FEATURES:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise"
        )

    # Validate treatment variable.
    if set(df["discount_received"].unique()) != {0, 1}:
        raise ValueError(
            "discount_received must contain both 0 and 1."
        )

    # Validate outcome variable.
    if set(df["purchased"].unique()) - {0, 1}:
        raise ValueError(
            "purchased must be a binary outcome: 0 or 1."
        )

    return df


# ============================================================
# DOUBLE MACHINE LEARNING MODEL
# ============================================================

def estimate_discount_effect(df):
    """Estimate the average effect of receiving any discount."""

    print("\n" + "=" * 60)
    print("DOUBLE MACHINE LEARNING")
    print("=" * 60)

    print(f"Customers: {len(df)}")

    print(
        "Received a discount:",
        int(df["discount_received"].sum())
    )

    print(
        "Received no discount:",
        int((df["discount_received"] == 0).sum())
    )

    # --------------------------------------------------------
    # STEP 1: SELECT MODELING VARIABLES
    # --------------------------------------------------------

    model_data = df[
        FEATURES + ["discount_received", "purchased"]
    ].copy()

    # --------------------------------------------------------
    # STEP 2: ENCODE CATEGORICAL VARIABLES
    # --------------------------------------------------------

    model_data = pd.get_dummies(
        model_data,
        columns=CATEGORICAL_FEATURES,
        drop_first=False,
        dtype=int,
    )

    # Identify encoded feature columns.
    encoded_features = [
        col
        for col in model_data.columns
        if col not in [
            "discount_received",
            "purchased",
        ]
    ]

    # --------------------------------------------------------
    # STEP 3: PREPARE DOUBLEML DATA
    # --------------------------------------------------------

    data = dml.DoubleMLData(
        model_data,
        y_col="purchased",
        d_cols="discount_received",
        x_cols=encoded_features,
    )

    # --------------------------------------------------------
    # STEP 4: OUTCOME MODEL
    # --------------------------------------------------------

    # Predict purchase probability using customer features.
    outcome_model = Pipeline(
        steps=[
            (
                "model",
                RandomForestClassifier(
                    n_estimators=200,
                    min_samples_leaf=20,
                    max_features="sqrt",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    # --------------------------------------------------------
    # STEP 5: PROPENSITY SCORE MODEL
    # --------------------------------------------------------

    # Predict probability of receiving a discount.
    propensity_model = Pipeline(
        steps=[
            (
                "model",
                RandomForestClassifier(
                    n_estimators=200,
                    min_samples_leaf=20,
                    max_features="sqrt",
                    random_state=123,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    # --------------------------------------------------------
    # STEP 6: DOUBLEML IRM
    # --------------------------------------------------------

    estimator = dml.DoubleMLIRM(
        data,
        ml_g=clone(outcome_model),
        ml_m=clone(propensity_model),
        n_folds=5,
        n_rep=1,
        score="ATE",
        trimming_rule="truncate",
        trimming_threshold=0.01,
    )

    # --------------------------------------------------------
    # STEP 7: TRAIN MODEL
    # --------------------------------------------------------

    print("\nTraining the cross-fitted DML model...")
    estimator.fit()

    # --------------------------------------------------------
    # STEP 8: DISPLAY ESTIMATION RESULTS
    # --------------------------------------------------------

    print("\n--- ESTIMATION RESULTS ---")
    print(estimator.summary)

    estimate = float(estimator.coef[0])
    standard_error = float(estimator.se[0])

    confidence_interval = estimator.confint(level=0.95)

    lower = float(confidence_interval.iloc[0, 0])
    upper = float(confidence_interval.iloc[0, 1])

    # --------------------------------------------------------
    # STEP 9: INTERPRETATION
    # --------------------------------------------------------

    print("\n--- INTERPRETATION ---")

    print(
        "Estimated purchase-probability effect:",
        f"{estimate * 100:.2f} percentage points",
    )

    print(
        "Standard error:",
        f"{standard_error:.4f}",
    )

    print(
        "95% confidence interval:",
        f"[{lower * 100:.2f}, {upper * 100:.2f}]",
        "percentage points",
    )

    print(
        "\nNote: This estimate is causal only under the "
        "required identification assumptions."
    )

    return estimator


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    df = load_data()
    estimate_discount_effect(df)


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()
