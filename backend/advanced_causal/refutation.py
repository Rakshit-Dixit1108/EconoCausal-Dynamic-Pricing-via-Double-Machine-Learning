
import argparse
from pathlib import Path

import pandas as pd
from dowhy import CausalModel


FEATURES = [
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

TREATMENT = "discount_received"
OUTCOME = "purchased"


def run_refutation(data_path):
    print("Loading dataset...")

    df = pd.read_csv(data_path)

    required = FEATURES + [TREATMENT, OUTCOME]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required].copy()

    df[TREATMENT] = pd.to_numeric(df[TREATMENT], errors="coerce")
    df[OUTCOME] = pd.to_numeric(df[OUTCOME], errors="coerce")

    df = df.dropna(subset=[TREATMENT, OUTCOME])
    df = df[df[TREATMENT].isin([0, 1])]
    df = df[df[OUTCOME].isin([0, 1])]

    df = pd.get_dummies(
        df,
        columns=["customer_segment", "region", "season"],
        drop_first=True,
        dtype=int,
    )

    confounders = [
        c for c in df.columns
        if c not in [TREATMENT, OUTCOME]
    ]

    print("Building causal model...")

    model = CausalModel(
        data=df,
        treatment=TREATMENT,
        outcome=OUTCOME,
        common_causes=confounders,
    )

    identified = model.identify_effect(
        proceed_when_unidentifiable=True
    )

    estimate = model.estimate_effect(
        identified,
        method_name="backdoor.linear_regression",
    )

    print("\nORIGINAL CAUSAL ESTIMATE")
    print(estimate)

    print("\nRunning random common cause refutation...")

    random_refutation = model.refute_estimate(
        identified,
        estimate,
        method_name="random_common_cause",
        num_simulations=10,
    )

    print(random_refutation)

    print("\nRunning placebo treatment refutation...")

    placebo_refutation = model.refute_estimate(
        identified,
        estimate,
        method_name="placebo_treatment_refuter",
        placebo_type="permute",
        num_simulations=10,
    )

    print(placebo_refutation)

    output = Path("advanced_causal_results")
    output.mkdir(exist_ok=True)

    with open(
        output / "refutation_results.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write("ORIGINAL ESTIMATE\n")
        f.write(str(estimate))
        f.write("\n\nRANDOM COMMON CAUSE\n")
        f.write(str(random_refutation))
        f.write("\n\nPLACEBO TREATMENT\n")
        f.write(str(placebo_refutation))

    print("\nRefutation analysis completed.")
    print("Saved:", output / "refutation_results.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    run_refutation(args.data)
