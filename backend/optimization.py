"""Exploratory discount analysis for the EconoCausal project.

This script compares observed outcomes at each discount level.
It does NOT estimate individual causal effects or true profit.
"""

from pathlib import Path
import argparse

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "econocausal_synthetic_customers.csv"
)

REQUIRED_COLUMNS = [
    "customer_id",
    "discount_percent",
    "purchased",
    "discount_cost_inr",
    "net_revenue_inr",
]


def load_data():
    """Load the dataset and validate the fields used in this analysis."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        raise ValueError("The dataset contains no rows.")

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    if df["customer_id"].isna().any():
        raise ValueError("Customer IDs contain missing values.")

    if df["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs were found.")

    numeric_columns = [
        "discount_percent",
        "purchased",
        "discount_cost_inr",
        "net_revenue_inr",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise",
        )

        if df[column].isna().any():
            raise ValueError(
                f"Missing values in column: {column}"
            )

    if not df["purchased"].isin([0, 1]).all():
        raise ValueError(
            "purchased must contain only 0 or 1."
        )

    if (df["discount_cost_inr"] < 0).any():
        raise ValueError(
            "Discount costs cannot be negative."
        )

    if (df["discount_percent"] < 0).any():
        raise ValueError(
            "Discount percentages cannot be negative."
        )

    return df


def analyze_discount_levels(df):
    """Summarize observed outcomes at each discount level."""

    summary = (
        df.groupby("discount_percent")
        .agg(
            customers=("customer_id", "count"),
            purchase_rate=("purchased", "mean"),
            avg_discount_cost_inr=("discount_cost_inr", "mean"),
            avg_net_revenue_inr=("net_revenue_inr", "mean"),
        )
        .reset_index()
        .sort_values("discount_percent")
    )

    summary["purchase_rate_percent"] = (
        summary["purchase_rate"] * 100
    )

    return summary


def recommend_discount(
    summary,
    target_customers,
    budget_inr=None,
):
    """Choose the best observed net-revenue option within budget.

    The budget check uses average observed discount cost per customer.
    This is an exploratory comparison, not a causal recommendation.
    """

    candidates = summary.copy()

    candidates["estimated_total_discount_cost_inr"] = (
        candidates["avg_discount_cost_inr"]
        * target_customers
    )

    if budget_inr is not None:
        candidates = candidates[
            candidates["estimated_total_discount_cost_inr"]
            <= budget_inr
        ]

    if candidates.empty:
        return None, candidates

    # Compare average net revenue per customer, not total revenue
    # from discount groups of different sizes.
    best_index = candidates["avg_net_revenue_inr"].idxmax()
    best = candidates.loc[best_index]

    return best, candidates


def main():
    parser = argparse.ArgumentParser(
        description="Explore discount levels in EconoCausal."
    )

    parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Optional total discount budget in INR.",
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=None,
        help="Number of customers to evaluate. Defaults to dataset size.",
    )

    args = parser.parse_args()

    if args.budget is not None and args.budget < 0:
        parser.error("--budget cannot be negative.")

    if args.customers is not None and args.customers <= 0:
        parser.error("--customers must be greater than zero.")

    df = load_data()
    target_customers = args.customers or len(df)

    summary = analyze_discount_levels(df)

    print("\n" + "=" * 72)
    print("ECONOCAUSAL — EXPLORATORY DISCOUNT ANALYSIS")
    print("=" * 72)

    display_columns = [
        "discount_percent",
        "customers",
        "purchase_rate_percent",
        "avg_discount_cost_inr",
        "avg_net_revenue_inr",
    ]

    print(
        summary[display_columns].to_string(
            index=False,
            formatters={
                "discount_percent": "{:.0f}%".format,
                "purchase_rate_percent": "{:.2f}%".format,
                "avg_discount_cost_inr": "₹{:,.2f}".format,
                "avg_net_revenue_inr": "₹{:,.2f}".format,
            },
        )
    )

    best, candidates = recommend_discount(
        summary,
        target_customers,
        args.budget,
    )

    print("\n" + "-" * 72)
    print("EXPLORATORY RECOMMENDATION")
    print("-" * 72)

    if best is None:
        print(
            "No discount level fits the specified budget "
            "using the observed average costs."
        )
    else:
        print(
            f"Observed best discount level: "
            f"{best['discount_percent']:.0f}%"
        )
        print(
            f"Observed average net revenue per customer: "
            f"₹{best['avg_net_revenue_inr']:,.2f}"
        )
        print(
            f"Estimated discount cost for "
            f"{target_customers:,} customers: "
            f"₹{best['estimated_total_discount_cost_inr']:,.2f}"
        )

    print("\nIMPORTANT LIMITATIONS")
    print(
        "- These are observed group averages, not causal effects."
    )
    print(
        "- The results do not identify which individual customers "
        "need a discount."
    )
    print(
        "- Net revenue is not profit because product and operating "
        "costs are not accounted for here."
    )
    print(
        "- Budget estimates assume observed average discount costs "
        "remain representative for the target customers."
    )


if __name__ == "__main__":
    main()
