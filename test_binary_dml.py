from pathlib import Path
import pandas as pd
from causal_service import estimate_treatment_effects
from causal_refutation import run_refutation_checks

DATA_PATH = Path("data/econocausal_synthetic_customers.csv")

def test_binary_dml_primary_analysis_and_export(tmp_path):
    output = tmp_path / "customer_effects.csv"
    result = estimate_treatment_effects(str(DATA_PATH), export_path=str(output))
    assert result["analysis_mode"] == "binary_discount_received"
    assert result["treatment"] == "discount_received"
    assert result["outcome"] == "purchased"
    assert result["discount_from"] == 0 and result["discount_to"] == 1
    assert result["treatment_group_counts"] == {"0.0": 2290, "1.0": 2710}
    assert len(result["individual_effects"]) == result["rows"]
    assert output.exists()
    data = pd.read_csv(output)
    assert len(data) == result["rows"]
    assert "individual_treatment_effect" in data.columns
    overlap = result["nuisance_diagnostics"]["overlap"]
    assert 0 <= overlap["propensity_min"] <= overlap["propensity_max"] <= 1

def test_binary_dowhy_refutation_checks():
    result = run_refutation_checks(data_path=str(DATA_PATH))
    assert result["analysis_mode"] == "binary_discount_received"
    assert result["treatment"] == "discount_received"
    assert result["estimate"] is not None
    assert {"random_common_cause", "data_subset_refuter"} <= set(result["refutation_results"])
    assert all(v is not None for v in result["refutation_results"].values())
