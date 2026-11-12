
"""
DoubleML IRM causal effect estimation.
Handles categorical predictors and missing predictor values.
Treatment and outcome are validated and never imputed.
"""

from pathlib import Path

import pandas as pd
import doubleml as dml

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "data" / "econocasual_synthetic_customers.csv"

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

TREATMENT = "discount_received"
OUTCOME = "purchased"


# ============================================================
# LOAD AND VALIDATE DATA
# ============================================================

def load_data(file_path=DATA_PATH):
    """Load dataset and validate treatment/outcome."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    required = FEATURES + [TREATMENT, OUTCOME]

    missing_columns = sorted(
        set(required) - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Dataset is empty.")

    # Treatment and outcome must never be imputed
    for column in [TREATMENT, OUTCOME]:

        if df[column].isna().any():
            raise ValueError(
                f"Missing values exist in '{column}'. "
                "Treatment/outcome cannot be imputed."
            )

        df[column] = pd.to_numeric(
            df[column],
            errors="raise"
        )

        if not df[column].isin([0, 1]).all():
            raise ValueError(
                f"'{column}' must contain only 0 and 1."
            )

        df[column] = df[column].astype(int)

    if set(df[TREATMENT].unique()) != {0, 1}:
        raise ValueError(
            "discount_received must contain both 0 and 1."
        )

    if df[OUTCOME].nunique() != 2:
        raise ValueError(
            "purchased must contain both 0 and 1."
        )

    # Convert numeric predictors
    for column in NUMERIC_FEATURES:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Clean categorical predictors
    for column in CATEGORICAL_FEATURES:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    all_missing = [
        column
        for column in FEATURES
        if df[column].isna().all()
    ]

    if all_missing:
        raise ValueError(
            f"Entire predictor columns are missing: {all_missing}"
        )

    print("\n--- DATA QUALITY ---")

    missing_counts = df[FEATURES].isna().sum()
    missing_counts = missing_counts[missing_counts > 0]

    if missing_counts.empty:
        print("No missing predictor values detected.")
    else:
        print(
            "Missing predictor values will be imputed:"
        )
        print(missing_counts.to_string())

    return df


# ============================================================
# PREPROCESSING
# ============================================================

def build_preprocessor():
    """Build numeric and categorical preprocessing."""

    numeric_pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ])

    categorical_pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoder",
            OneHotEncoder(handle_unknown="ignore")
        )
    ])

    preprocessor = ColumnTransformer([
        (
            "numeric",
            numeric_pipeline,
            NUMERIC_FEATURES
        ),
        (
            "categorical",
            categorical_pipeline,
            CATEGORICAL_FEATURES
        )
    ])

    return preprocessor


def preprocess_features(df):
    """Convert raw predictors into numeric features."""

    X = df[FEATURES].copy()

    preprocessor = build_preprocessor()

    X_processed = preprocessor.fit_transform(X)

    # Convert sparse output to dense array
    if hasattr(X_processed, "toarray"):
        X_processed = X_processed.toarray()

    feature_names = (
        preprocessor.get_feature_names_out()
    )

    X_processed = pd.DataFrame(
        X_processed,
        columns=feature_names,
        index=df.index
    )

    X_processed = X_processed.astype(float)

    return X_processed, preprocessor


# ============================================================
# MACHINE LEARNING MODELS
# ============================================================

def build_outcome_model():
    """Random Forest outcome model."""

    return RandomForestClassifier(
        n_estimators=200,
        min_samples_leaf=20,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1
    )


def build_propensity_model():
    """Random Forest propensity model."""

    return RandomForestClassifier(
        n_estimators=200,
        min_samples_leaf=20,
        max_features="sqrt",
        random_state=123,
        n_jobs=-1
    )


# ============================================================
# DOUBLE MACHINE LEARNING - IRM
# ============================================================

def estimate_discount_effect(df=None):
    """
    Estimate the average treatment effect of receiving a discount.

    Treatment:
        discount_received

    Outcome:
        purchased
    """

    print("\n" + "=" * 60)
    print("DOUBLE MACHINE LEARNING")
    print("=" * 60)

    # Load data if not supplied
    if df is None:
        df = load_data()
    else:
        df = df.copy()

    required = FEATURES + [TREATMENT, OUTCOME]

    missing_columns = sorted(
        set(required) - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    if df.empty:
        raise ValueError(
            "No modeling rows are available."
        )

    # Validate treatment and outcome
    for column in [TREATMENT, OUTCOME]:

        if df[column].isna().any():
            raise ValueError(
                f"{column} contains missing values."
            )

        df[column] = pd.to_numeric(
            df[column],
            errors="raise"
        )

        if not df[column].isin([0, 1]).all():
            raise ValueError(
                f"{column} must contain only 0 or 1."
            )

        df[column] = df[column].astype(int)

    if set(df[TREATMENT].unique()) != {0, 1}:
        raise ValueError(
            "discount_received must contain both 0 and 1."
        )

    if df[OUTCOME].nunique() != 2:
        raise ValueError(
            "purchased must contain both 0 and 1."
        )

    print(f"Customers: {len(df)}")

    print(
        "Received a discount:",
        int(df[TREATMENT].sum())
    )

    print(
        "Received no discount:",
        int((df[TREATMENT] == 0).sum())
    )

    # --------------------------------------------------------
    # PREPROCESS PREDICTORS
    # --------------------------------------------------------

    print("\nPreprocessing predictors...")

    X_processed, preprocessor = preprocess_features(df)

    print(
        f"Original predictors: {len(FEATURES)}"
    )

    print(
        f"Processed predictors: {X_processed.shape[1]}"
    )

    # Combine numeric predictors with treatment/outcome
    model_data = pd.concat(
        [
            X_processed,
            df[[TREATMENT, OUTCOME]]
        ],
        axis=1
    )

    # --------------------------------------------------------
    # DOUBLEML DATA OBJECT
    # --------------------------------------------------------

    data = dml.DoubleMLData(
        model_data,
        y_col=OUTCOME,
        d_cols=TREATMENT,
        x_cols=list(X_processed.columns)
    )

    # --------------------------------------------------------
    # DOUBLEML IRM ESTIMATOR
    # --------------------------------------------------------

    estimator = dml.DoubleMLIRM(
        data,
        ml_g=build_outcome_model(),
        ml_m=build_propensity_model(),
        n_folds=5,
        n_rep=1,
        score="ATE",
        trimming_rule="truncate",
        trimming_threshold=0.01
    )

    # --------------------------------------------------------
    # FIT MODEL
    # --------------------------------------------------------

    print("\nTraining the cross-fitted DML model...")

    estimator.fit()

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print("\n--- ESTIMATION RESULTS ---")

    print(estimator.summary)

    estimate = float(estimator.coef[0])

    standard_error = float(estimator.se[0])

    confidence_interval = estimator.confint(
        level=0.95
    )

    lower = float(
        confidence_interval.iloc[0, 0]
    )

    upper = float(
        confidence_interval.iloc[0, 1]
    )

    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------

    print("\n--- INTERPRETATION ---")

    print(
        "Estimated purchase-probability effect:",
        f"{estimate * 100:.2f} percentage points"
    )

    print(
        "Standard error:",
        f"{standard_error:.4f}"
    )

    print(
        "95% confidence interval:",
        f"[{lower * 100:.2f}, "
        f"{upper * 100:.2f}] percentage points"
    )

    print(
        "\nNote: Causal interpretation requires "
        "identification assumptions to hold."
    )

    return estimator

def main():

    df = load_data()

    estimate_discount_effect(df)


if __name__ == "__main__":
    main()
