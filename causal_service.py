
"""Initial input validation for the EconoCausal causal ML engine."""


def validate_causal_columns(df, treatment_col, outcome_col):
    """Check that the treatment and outcome columns exist."""

    if df.empty:
        raise ValueError("The dataset contains no rows.")

    required = [treatment_col, outcome_col]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Treatment or outcome contains missing values.")

    for col in required:
        if not df[col].isin([0, 1]).all():
            raise ValueError(f"{col} must contain only 0 and 1.")

    if df[treatment_col].nunique() < 2:
        raise ValueError("Both treatment groups (0 and 1) are required.")

    return {
        "rows": len(df),
        "treatment_column": treatment_col,
        "outcome_column": outcome_col,
        "status": "validated",
    }






# Baseline Causal ML Engine using EconML LinearDML

import pandas as pd
from econml.dml import LinearDML
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
FEATURE_COLUMNS = [
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

TREATMENT_COLUMN = "discount_received"
OUTCOME_COLUMN = "purchased"


def estimate_treatment_effects(data_path):
    """Estimate the effect of receiving a discount on purchase outcomes."""

    df = pd.read_csv(data_path)

    validate_causal_columns(df, TREATMENT_COLUMN, OUTCOME_COLUMN)

    required = FEATURE_COLUMNS + [TREATMENT_COLUMN, OUTCOME_COLUMN]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Features, treatment, or outcome contain missing values.")

    if df[TREATMENT_COLUMN].nunique() != 2:
        raise ValueError("Both discount treatment groups are required.")

    # Encode categorical customer features.
    categorical_features = ["customer_segment", "region", "season"]
    numeric_features = [
        col for col in FEATURE_COLUMNS
        if col not in categorical_features
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical",
             OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False),
             categorical_features),
            ("numeric", "passthrough", numeric_features),
        ],
        verbose_feature_names_out=False,
    )

    X = preprocessor.fit_transform(df[FEATURE_COLUMNS])
    T = df[TREATMENT_COLUMN].astype(int).to_numpy()
    Y = df[OUTCOME_COLUMN].astype(float).to_numpy()

    # Estimate outcome and treatment models using cross-fitting.
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
        cv=3,
        random_state=42,
    )

    model.fit(Y, T, X=X)

    # Individual and average estimated treatment effects.
    effects = model.effect(X, T0=0, T1=1)
    average_effect = float(effects.mean())

    ate_inference = model.ate_inference(X)
    ate_interval = model.ate_interval(X, alpha=0.05)

    return {
        "rows": len(df),
        "treatment": TREATMENT_COLUMN,
        "outcome": OUTCOME_COLUMN,
        "average_treatment_effect": average_effect,
        "average_effect_percentage_points": average_effect * 100,
        "individual_effects": effects,
        "model": model,
        "ate_confidence_interval": tuple(
            float(value) for value in ate_interval
        ),
        "ate_inference": ate_inference,
    }
