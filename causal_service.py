
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
