
from pathlib import Path

import pandas as pd


# Locate the project directory independently of the terminal's current folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = (
    PROJECT_ROOT / "data" / "econocausal_synthetic_customers.csv"
)

# Columns required for our first causal model.
REQUIRED_COLUMNS = [
    "customer_id",
    "age",
    "annual_income_inr",
    "past_purchases_12m",
    "days_since_last_purchase",
    "website_visits_30d",
    "email_engagement_score",
    "customer_segment",
    "region",
    "season",
    "discount_received",
    "purchased",
]

# Numeric customer features used to adjust for observed differences.
NUMERIC_FEATURES = [
    "age",
    "annual_income_inr",
    "past_purchases_12m",
    "days_since_last_purchase",
    "website_visits_30d",
    "email_engagement_score",
]

# Text-based customer features; these will be encoded for ML later.
CATEGORICAL_FEATURES = [
    "customer_segment",
    "region",
    "season",
]

TREATMENT_COLUMN = "discount_received"
OUTCOME_COLUMN = "purchased"


def load_data(file_path=DEFAULT_DATA_PATH):
    """Load the CSV and validate its structure and core model variables."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("The dataset contains no rows.")

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df["customer_id"].isna().any():
        raise ValueError("Some customer IDs are missing.")

    if df["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs were found.")

    # Model variables and numeric features must contain valid values.
    numeric_columns = NUMERIC_FEATURES + [
        TREATMENT_COLUMN,
        OUTCOME_COLUMN,
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

        if df[column].isna().any():
            raise ValueError(
                f"Missing values found in required column: {column}"
            )

    if df[NUMERIC_FEATURES].isna().any().any():
        raise ValueError("Numeric customer features contain missing values.")

    if not df[TREATMENT_COLUMN].isin([0, 1]).all():
        raise ValueError(
            "discount_received must contain only 0 or 1."
        )

    if set(df[TREATMENT_COLUMN].unique()) != {0, 1}:
        raise ValueError(
            "Both discount groups are required: 0 and 1."
        )

    if not df[OUTCOME_COLUMN].isin([0, 1]).all():
        raise ValueError("purchased must contain only 0 or 1.")

    for column in CATEGORICAL_FEATURES:
        if df[column].isna().any():
            raise ValueError(
                f"Missing values found in categorical column: {column}"
            )

        if df[column].astype(str).str.strip().eq("").any():
            raise ValueError(
                f"Blank values found in categorical column: {column}"
            )

    return df


def get_data_summary(df):
    """Return a compact data-quality and treatment summary."""

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_customer_ids": int(
            df["customer_id"].duplicated().sum()
        ),
        "missing_values": {
            column: int(count)
            for column, count in df.isna().sum().items()
        },
        "discount_groups": {
            str(int(group)): int(count)
            for group, count in (
                df[TREATMENT_COLUMN].value_counts().sort_index().items()
            )
        },
        "purchase_rate_by_discount": {
            str(int(group)): round(float(rate), 4)
            for group, rate in (
                df.groupby(TREATMENT_COLUMN)[OUTCOME_COLUMN]
                .mean()
                .items()
            )
        },
    }


if __name__ == "__main__":
    try:
        data = load_data()
        summary = get_data_summary(data)

        print("Dataset loaded and validated successfully.")
        print(f"Rows: {summary['rows']}")
        print(f"Columns: {summary['columns']}")
        print(f"Duplicate customer IDs: {summary['duplicate_customer_ids']}")

        print("\nDiscount group counts:")
        for group, count in summary["discount_groups"].items():
            print(f"  Discount received = {group}: {count} customers")

        print("\nPurchase rate by discount group:")
        for group, rate in summary["purchase_rate_by_discount"].items():
            print(f"  Discount received = {group}: {rate:.2%}")

        print("\nMissing values:")
        for column, count in summary["missing_values"].items():
            if count > 0:
                print(f"  {column}: {count}")

        print("\nData validation completed.")

    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        print(f"DATA VALIDATION FAILED: {error}")
        raise
