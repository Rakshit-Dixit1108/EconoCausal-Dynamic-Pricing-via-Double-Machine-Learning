
"""Estimate discount effects by customer segment using DoubleML GATEs."""

import pandas as pd

from causal_model import load_data, estimate_discount_effect


def estimate_segment_effects(df=None):
    """Estimate group-level discount effects with confidence intervals."""

    # Load the default dataset only when no dataset is supplied.
    if df is None:
        df = load_data()
    else:
        df = df.copy()

    # Validate required column.
    if "customer_segment" not in df.columns:
        raise ValueError(
            "Dataset must contain the 'customer_segment' column."
        )

    # Remove rows with missing segment labels.
    df = df.dropna(subset=["customer_segment"]).copy()

    if df.empty:
        raise ValueError("No valid customer segments found.")

    print("\n" + "=" * 60)
    print("CUSTOMER SEGMENT CAUSAL ANALYSIS")
    print("=" * 60)

    # Fit the existing DoubleML model.
    estimator = estimate_discount_effect(df)

    # Define mutually exclusive customer groups.
    groups = pd.DataFrame({
        "customer_segment": df["customer_segment"].astype(str)
    })

    # Estimate the average treatment effect in each group.
    gate_model = estimator.gate(groups=groups)

    # Obtain segment-level estimates and 95% confidence intervals.
    confidence_intervals = gate_model.confint(level=0.95)

    print("\n--- SEGMENT-LEVEL CAUSAL EFFECTS ---")
    print(confidence_intervals)

    print("\nInterpretation:")
    print(
        "Effects are measured in purchase-probability units. "
        "Multiply by 100 to express them in percentage points."
    )
    print(
        "A positive effect indicates that receiving a discount "
        "increases the estimated purchase probability for that segment."
    )
    print(
        "A confidence interval containing zero means the estimate "
        "does not clearly distinguish the effect from zero at the "
        "conventional 5% significance level."
    )
    print(
        "\nCausal interpretation requires the identification "
        "assumptions to hold, including adequate control of "
        "confounding and treatment overlap."
    )

    return gate_model


def main():
    estimate_segment_effects()


if __name__ == "__main__":
    main()
