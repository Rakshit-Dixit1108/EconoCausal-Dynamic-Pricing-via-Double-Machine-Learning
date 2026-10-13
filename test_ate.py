
from pathlib import Path

from causal_service import estimate_treatment_effects

DATA_PATH = Path("data/econocausal_synthetic_customers.csv")

def test_ate_confidence_interval():
    result = estimate_treatment_effects(DATA_PATH)

    ate = result["average_treatment_effect"]
    lower, upper = result["ate_confidence_interval"]

    assert result["rows"] > 0
    assert -1 <= ate <= 1, f"Unexpected ATE: {ate}"
    assert lower <= upper, "Confidence interval bounds are reversed"
    assert lower <= ate <= upper, (
        f"ATE {ate} is outside confidence interval ({lower}, {upper})"
    )

    print("PASS: ATE confidence interval")
    print(f"ATE: {ate:.4f}")
    print(f"95% CI: ({lower:.4f}, {upper:.4f})")


if __name__ == "__main__":
    test_ate_confidence_interval()
