
"""DoWhy causal estimation and refutation checks for EconoCausal."""

import pandas as pd
from dowhy import CausalModel

DATA_PATH = "data/econocausal_synthetic_customers.csv"

TREATMENT = "discount_percent"
OUTCOME = "purchased"

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


def run_refutation_checks(data_path=DATA_PATH, discount_from=5, discount_to=20):
    df = pd.read_csv(data_path)

    required = FEATURE_COLUMNS + [TREATMENT, OUTCOME]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Required data contains missing values.")

    if not df[OUTCOME].isin([0, 1]).all():
        raise ValueError("purchased must contain only 0 and 1.")

    if df[TREATMENT].nunique() < 2:
        raise ValueError("At least two discount levels are required.")

    if discount_from == discount_to:
        raise ValueError("Choose two different discount levels.")

    if min(discount_from, discount_to) < df[TREATMENT].min():
        raise ValueError("Discount value is below the observed data range.")

    if max(discount_from, discount_to) > df[TREATMENT].max():
        raise ValueError("Discount value is above the observed data range.")

    # Encode categorical customer features for the causal model.
    encoded_features = pd.get_dummies(
        df[FEATURE_COLUMNS],
        columns=["customer_segment", "region", "season"],
        drop_first=True,
        dtype=float,
    )

    causal_data = pd.concat(
        [
            df[[TREATMENT, OUTCOME]].reset_index(drop=True),
            encoded_features.reset_index(drop=True),
        ],
        axis=1,
    )

    common_causes = list(encoded_features.columns)

    causal_model = CausalModel(
        data=causal_data,
        treatment=TREATMENT,
        outcome=OUTCOME,
        common_causes=common_causes,
    )

    estimand = causal_model.identify_effect(
        proceed_when_unidentifiable=True
    )

    # This is an independent linear-regression estimate for
    # DoWhy validation, not the existing EconML LinearDML estimate.
    estimate = causal_model.estimate_effect(
        estimand,
        method_name="backdoor.linear_regression",
        control_value=discount_from,
        treatment_value=discount_to,
    )

    print(f"DoWhy estimate: {estimate.value:.6f}")
    print(f"Discount comparison: {discount_from} vs {discount_to}")

    results = {}

    # Refutation 1: add a randomly generated common cause.
    results["random_common_cause"] = causal_model.refute_estimate(
        estimand,
        estimate,
        method_name="random_common_cause",
        random_seed=42,
        num_simulations=10,
    )

    # Refutation 2: rerun estimation on random subsets.
    results["data_subset_refuter"] = causal_model.refute_estimate(
        estimand,
        estimate,
        method_name="data_subset_refuter",
        random_seed=42,
        subset_fraction=0.8,
        num_simulations=10,
    )

    for name, result in results.items():
        print(f"\n{name}:")
        print(result)

    return {
        "estimate": estimate,
        "estimand": estimand,
        "refutation_results": results,
    }


if __name__ == "__main__":
    run_refutation_checks()
