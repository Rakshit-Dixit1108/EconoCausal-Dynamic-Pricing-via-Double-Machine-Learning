import pandas as pd
from causal_service import validate_causal_columns

cases = [
    ("valid", [0, 1], [0, 1], True),
    ("invalid treatment", [0, 2], [0, 1], False),
    ("missing outcome", [0, 1], [0, None], False),
    ("one treatment group", [1, 1], [0, 1], False),
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