"""DoWhy refutation: binary discount_received primary; optional discount_percent contrast."""
import pandas as pd
from dowhy import CausalModel

DATA_PATH = "data/econocausal_synthetic_customers.csv"
OUTCOME = "purchased"
FEATURE_COLUMNS = ["age", "annual_income_inr", "past_purchases_12m",
    "days_since_last_purchase", "website_visits_30d", "email_engagement_score",
    "customer_segment", "region", "season"]

def run_refutation_checks(data_path=DATA_PATH, discount_from=None, discount_to=None):
    df = pd.read_csv(data_path)
    missing = [c for c in FEATURE_COLUMNS + [OUTCOME] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df[FEATURE_COLUMNS + [OUTCOME]].isna().any().any():
        raise ValueError("Required features or outcome contain missing values.")
    if not df[OUTCOME].isin([0, 1]).all():
        raise ValueError("purchased must contain only 0 and 1.")
    legacy = discount_from is not None or discount_to is not None
    if legacy and (discount_from is None or discount_to is None):
        raise ValueError("Supply both discount_from and discount_to for optional contrast.")
    treatment = "discount_percent" if legacy else "discount_received"
    if treatment not in df.columns or df[treatment].isna().any():
        raise ValueError(f"Missing or null treatment column: {treatment}")
    observed = pd.to_numeric(df[treatment], errors="coerce")
    if observed.isna().any() or observed.nunique() < 2:
        raise ValueError("Treatment must contain at least two numeric values.")
    if legacy:
        c, t = float(discount_from), float(discount_to)
        if c == t or min(c,t) < observed.min() or max(c,t) > observed.max():
            raise ValueError("Invalid discount contrast for observed range.")
        if c not in set(observed) or t not in set(observed):
            raise ValueError("Requested discount values must occur in the data.")
    else:
        if not set(observed.unique()).issubset({0,1}) or set(observed.unique()) != {0,1}:
            raise ValueError("discount_received must contain both 0 and 1 only.")
        c, t = 0, 1
    encoded = pd.get_dummies(df[FEATURE_COLUMNS],
        columns=["customer_segment","region","season"], drop_first=True, dtype=float)
    causal_data = pd.concat([observed.rename(treatment).reset_index(drop=True),
        df[OUTCOME].reset_index(drop=True), encoded.reset_index(drop=True)], axis=1)
    model = CausalModel(data=causal_data, treatment=treatment, outcome=OUTCOME,
        common_causes=list(encoded.columns))
    estimand = model.identify_effect(proceed_when_unidentifiable=True)
    estimate = model.estimate_effect(estimand, method_name="backdoor.linear_regression",
        control_value=c, treatment_value=t)
    refs = {
        "random_common_cause": model.refute_estimate(estimand, estimate,
            method_name="random_common_cause", random_seed=42, num_simulations=10),
        "data_subset_refuter": model.refute_estimate(estimand, estimate,
            method_name="data_subset_refuter", random_seed=42,
            subset_fraction=.8, num_simulations=10)}
    return {"estimate": estimate, "estimand": estimand, "refutation_results": refs,
        "analysis_mode": "discount_percent_contrast" if legacy else "binary_discount_received",
        "treatment": treatment, "outcome": OUTCOME, "control_value": c, "treatment_value": t,
        "identification_note": "DoWhy estimate is independent of EconML DML. Refutation tests do not prove absence of unmeasured confounding."}

if __name__ == "__main__":
    r = run_refutation_checks()
    print("Analysis:", r["analysis_mode"], "DoWhy estimate:", r["estimate"].value)
    for name, result in r["refutation_results"].items():
        print(f"\n{name}:\n{result}")
