
from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_PATH = Path("outputs/customer_multilevel_dml_effects.csv")
EXPECTED_ROWS = 5000

EFFECT_COLUMNS = [
    "effect_5_vs_0_pp",
    "effect_10_vs_0_pp",
    "effect_20_vs_0_pp",
]


def test_multilevel_output_exists():
    assert OUTPUT_PATH.exists(), "Multi-level output CSV not found."


def test_output_shape_and_columns():
    df = pd.read_csv(OUTPUT_PATH)

    assert len(df) == EXPECTED_ROWS
    assert "customer_id" in df.columns
    assert all(col in df.columns for col in EFFECT_COLUMNS)


def test_customer_ids_are_unique():
    df = pd.read_csv(OUTPUT_PATH)

    assert df["customer_id"].is_unique


def test_no_missing_values():
    df = pd.read_csv(OUTPUT_PATH)

    assert df[["customer_id", *EFFECT_COLUMNS]].notna().all().all()


def test_effects_are_finite():
    df = pd.read_csv(OUTPUT_PATH)

    effects = df[EFFECT_COLUMNS].to_numpy(dtype=float)
    assert np.isfinite(effects).all()
