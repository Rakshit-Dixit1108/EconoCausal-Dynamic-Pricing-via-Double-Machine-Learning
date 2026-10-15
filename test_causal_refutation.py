
from pathlib import Path

from causal_refutation import run_refutation_checks

DATA_PATH = Path("data/econocausal_synthetic_customers.csv")


def test_dowhy_refutation_checks():
    result = run_refutation_checks(
        data_path=str(DATA_PATH),
        discount_from=5,
        discount_to=20,
    )

    assert result["estimate"] is not None

    refutations = result["refutation_results"]

    assert "random_common_cause" in refutations
    assert "data_subset_refuter" in refutations

    for name, refutation in refutations.items():
        assert refutation is not None, f"{name} returned no result"

    print("PASS: DoWhy refutation checks")
    print(f"Estimate: {result['estimate'].value:.4f}")


if __name__ == "__main__":
    test_dowhy_refutation_checks()
