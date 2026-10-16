
from pathlib import Path
import numpy as np

from causal_service import estimate_treatment_effects

DATA_PATH = Path("data/econocausal_synthetic_customers.csv")


def test_individual_treatment_effects():
    result = estimate_treatment_effects(
        DATA_PATH,
        discount_from=5,
        discount_to=20,
    )

    effects = np.asarray(result["individual_effects"], dtype=float)

    assert len(effects) == result["rows"]
    assert np.isfinite(effects).all()
    assert np.isclose(
        effects.mean(),
        result["average_treatment_effect"],
    )
    assert result["discount_from"] == 5
    assert result["discount_to"] == 20

    print("PASS: Individual treatment effects")
    print(f"Customers evaluated: {len(effects)}")
    print(f"Mean individual effect: {effects.mean():.4f}")
    print(f"Minimum effect: {effects.min():.4f}")
    print(f"Maximum effect: {effects.max():.4f}")
    print(
        "Customers with positive estimated effects:",
        int((effects > 0).sum()),
    )
    print(
        "Customers with negative estimated effects:",
        int((effects < 0).sum()),
    )


if __name__ == "__main__":
    test_individual_treatment_effects()
