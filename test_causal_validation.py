
import pandas as pd
from causal_service import validate_causal_columns

cases = [
    ("valid continuous treatment", [0, 5, 10, 20], [0, 1, 0, 1], True),
    ("negative discount", [0, -5, 10, 20], [0, 1, 0, 1], False),
    ("invalid outcome", [0, 5, 10, 20], [0, 2, 0, 1], False),
    ("missing outcome", [0, 5, 10, 20], [0, None, 0, 1], False),
    ("one discount level", [5, 5, 5, 5], [0, 1, 0, 1], False),
    ("non-numeric treatment", [0, "abc", 10, 20], [0, 1, 0, 1], False),
]

for name, t, y, should_pass in cases:
    df = pd.DataFrame({"T": t, "Y": y})

    try:
        validate_causal_columns(df, "T", "Y")
        assert should_pass, f"{name}: expected rejection"
        print(f"PASS: {name}")
    except ValueError:
        assert not should_pass, f"{name}: valid input was rejected"
        print(f"PASS: rejected {name}")
