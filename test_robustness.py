
from pathlib import Path
import numpy as np

from causal_service import estimate_treatment_effects

DATA_PATH = Path("data/econocausal_synthetic_customers.csv")


def test_ate_robustness():
    result = estimate_treatment_effects(
        DATA_PATH,
        discount_from=5,
        discount_to=20,
    )

    ate = float(result["average_treatment_effect"])
    ci_low, ci_high = result["ate_confidence_interval"]
    effects = np.asarray(result["individual_effects"], dtype=float)

    # Confidence interval must be finite and ordered
    assert np.isfinite([ate, ci_low, ci_high]).all()
    assert ci_low <= ci_high

    # ATE should lie inside its confidence interval
    assert ci_low <= ate <= ci_high

    # Percentage-point values should match the original values
    pp_low, pp_high = result[
        "ate_confidence_interval_percentage_points"
    ]
    assert np.isclose(pp_low, ci_low * 100)
    assert np.isclose(pp_high, ci_high * 100)

    # Individual estimates should be finite and match row count
    assert len(effects) == result["rows"]
    assert np.isfinite(effects).all()
    assert np.isclose(effects.mean(), ate)

    print("\nPASS: ATE robustness consistency checks")
    print(f"Comparison: {result['discount_from']}% vs "
          f"{result['discount_to']}% discount")
    print(f"ATE: {ate:.4f}")
    print(f"95% CI: ({ci_low:.4f}, {ci_high:.4f})")
    print(f"Customers evaluated: {len(effects)}")


if __name__ == "__main__":
    test_ate_robustness()
