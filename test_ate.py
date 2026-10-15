
from pathlib import Path

from causal_service import estimate_treatment_effects

DATA_PATH = Path("data/econocausal_synthetic_customers.csv")


def test_ate_confidence_interval():
    discount_from = 5
    discount_to = 20

    result = estimate_treatment_effects(
        DATA_PATH,
        discount_from=discount_from,
        discount_to=discount_to,
    )

    ate = result["average_treatment_effect"]
    lower, upper = result["ate_confidence_interval"]

    assert result["rows"] > 0
    assert result["discount_from"] == discount_from
    assert result["discount_to"] == discount_to
    assert -1 <= ate <= 1, f"Unexpected ATE: {ate}"
    assert lower <= upper, "Confidence interval bounds are reversed"
    assert lower <= ate <= upper, (
        f"ATE {ate} is outside confidence interval ({lower}, {upper})"
    )

    assert len(result["individual_effects"]) == result["rows"]

    print("PASS: Continuous-treatment ATE confidence interval")
    print(f"Discount comparison: {discount_from} vs {discount_to}")
    print(f"ATE: {ate:.4f}")
    print(
        "ATE in percentage points: "
        f"{result['average_effect_percentage_points']:.2f}"
    )
    print(
        "95% CI in percentage points: "
        f"{result['ate_confidence_interval_percentage_points']}"
    )


if __name__ == "__main__":
    test_ate_confidence_interval()
