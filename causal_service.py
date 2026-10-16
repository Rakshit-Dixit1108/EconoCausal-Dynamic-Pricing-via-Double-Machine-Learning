
"""Causal ML engine for comparing customer discount levels."""

import numpy as np
import pandas as pd

from econml.dml import LinearDML
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import mean_squared_error, r2_score

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

TREATMENT_COLUMN = "discount_percent"
OUTCOME_COLUMN = "purchased"


def validate_causal_columns(df, treatment_col, outcome_col):
    """Validate continuous discount treatment and binary purchase outcome."""

    if df.empty:
        raise ValueError("The dataset contains no rows.")

    required = [treatment_col, outcome_col]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Treatment or outcome contains missing values.")

    treatment = pd.to_numeric(df[treatment_col], errors="coerce")
    outcome = pd.to_numeric(df[outcome_col], errors="coerce")

    if not np.isfinite(treatment.to_numpy(dtype=float)).all():
        raise ValueError("Treatment must contain finite numeric values.")

    if not np.isfinite(outcome.to_numpy(dtype=float)).all():
        raise ValueError("Outcome must contain finite numeric values.")

    if not outcome.isin([0, 1]).all():
        raise ValueError("The purchase outcome must contain only 0 and 1.")

    if treatment.nunique() < 2:
        raise ValueError("At least two distinct discount levels are required.")

    if (treatment < 0).any():
        raise ValueError("Discount values cannot be negative.")

    return {
        "rows": len(df),
        "treatment_column": treatment_col,
        "outcome_column": outcome_col,
        "observed_discount_levels": sorted(
            treatment.unique().astype(float).tolist()
        ),
        "status": "validated",
    }


def calculate_nuisance_diagnostics(X, T, Y):
    """Evaluate nuisance-model predictions using cross-validation."""

    cv = KFold(n_splits=3, shuffle=True, random_state=42)

    model_y = RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )

    model_t = RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )

    # Out-of-fold predictions: each row is predicted without
    # training the prediction model on that row.
    predicted_y = cross_val_predict(model_y, X, Y, cv=cv)
    predicted_t = cross_val_predict(model_t, X, T, cv=cv)

    residual_y = Y - predicted_y
    residual_t = T - predicted_t

    return {
        "outcome_model": {
            "r2": float(r2_score(Y, predicted_y)),
            "rmse": float(np.sqrt(mean_squared_error(Y, predicted_y))),
            "residual_mean": float(np.mean(residual_y)),
            "residual_std": float(np.std(residual_y)),
        },
        "treatment_model": {
            "r2": float(r2_score(T, predicted_t)),
            "rmse": float(np.sqrt(mean_squared_error(T, predicted_t))),
            "residual_mean": float(np.mean(residual_t)),
            "residual_std": float(np.std(residual_t)),
        },
    }

def estimate_treatment_effects(
    data_path,
    discount_from=0,
    discount_to=None,
):
    """
    Estimate the purchase-probability difference between two discount levels.

    discount_from and discount_to must use the same units as discount_percent.
    """

    df = pd.read_csv(data_path)

    required = FEATURE_COLUMNS + [TREATMENT_COLUMN, OUTCOME_COLUMN]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Features, treatment, or outcome contain missing values.")

    # Validate the treatment and outcome.
    validation = validate_causal_columns(
        df, TREATMENT_COLUMN, OUTCOME_COLUMN
    )

    T = pd.to_numeric(df[TREATMENT_COLUMN], errors="raise").to_numpy(
        dtype=float
    )
    Y = pd.to_numeric(df[OUTCOME_COLUMN], errors="raise").to_numpy(
        dtype=float
    )

    observed_min = float(np.min(T))
    observed_max = float(np.max(T))

    if discount_to is None:
        discount_to = observed_max

    try:
        discount_from = float(discount_from)
        discount_to = float(discount_to)
    except (TypeError, ValueError):
        raise ValueError("Both discount values must be numeric.") from None

    if not np.isfinite([discount_from, discount_to]).all():
        raise ValueError("Discount values must be finite numbers.")

    if discount_from < 0 or discount_to < 0:
        raise ValueError("Discount values cannot be negative.")

    if discount_from == discount_to:
        raise ValueError("Choose two different discount values.")

    if min(discount_from, discount_to) < observed_min or max(
        discount_from, discount_to
    ) > observed_max:
        raise ValueError(
            f"Choose discount values within the observed data range "
            f"({observed_min:g} to {observed_max:g}). "
            "Values outside this range require extrapolation."
        )

    # Encode categorical customer features.
    categorical_features = ["customer_segment", "region", "season"]
    numeric_features = [
        col for col in FEATURE_COLUMNS
        if col not in categorical_features
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    drop="first",
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_features,
            ),
            ("numeric", "passthrough", numeric_features),
        ],
        verbose_feature_names_out=False,
    )

    X = preprocessor.fit_transform(df[FEATURE_COLUMNS])
    nuisance_diagnostics = calculate_nuisance_diagnostics(
        X, T, Y
    )

    print("\n=== NUISANCE MODEL DIAGNOSTICS ===")
    print("Outcome model:", nuisance_diagnostics["outcome_model"])
    print("Treatment model:", nuisance_diagnostics["treatment_model"])

    # Continuous treatment: use a regressor for both nuisance models.
    model = LinearDML(
        model_y=RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
        model_t=RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
        discrete_treatment=False,
        cv=3,
        random_state=42,
    )

    model.fit(Y, T, X=X)

    # Compare the two requested discount levels for each customer.
    effects = model.effect(
        X,
        T0=discount_from,
        T1=discount_to,
    )

    average_effect = float(np.mean(effects))

    ate_inference = model.ate_inference(
        X,
        T0=discount_from,
        T1=discount_to,
    )

    ate_interval = model.ate_interval(
        X,
        T0=discount_from,
        T1=discount_to,
        alpha=0.05,
    )

    return {
        "rows": len(df),
        "treatment": TREATMENT_COLUMN,
        "outcome": OUTCOME_COLUMN,
        "discount_from": discount_from,
        "discount_to": discount_to,
        "observed_discount_levels": validation[
            "observed_discount_levels"
        ],
        "average_treatment_effect": average_effect,
        "average_effect_percentage_points": average_effect * 100,
        "individual_effects": effects,
        "model": model,
        "ate_confidence_interval": tuple(
            float(value) for value in ate_interval
        ),
        "ate_confidence_interval_percentage_points": tuple(
            float(value) * 100 for value in ate_interval
        ),
        "ate_inference": ate_inference,
        "nuisance_diagnostics": nuisance_diagnostics,
        "validation": validation,

    }
