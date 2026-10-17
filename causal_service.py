"""EconoCausal DML service: binary treatment primary, continuous contrast optional."""
from pathlib import Path
import numpy as np
import pandas as pd
from econml.dml import LinearDML
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, roc_auc_score, brier_score_loss
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict
from sklearn.preprocessing import OneHotEncoder

FEATURE_COLUMNS = ["age", "annual_income_inr", "past_purchases_12m",
    "days_since_last_purchase", "website_visits_30d", "email_engagement_score",
    "customer_segment", "region", "season"]
TREATMENT_COLUMN = "discount_received"
OUTCOME_COLUMN = "purchased"
LEGACY_TREATMENT_COLUMN = "discount_percent"
DEFAULT_DATA_PATH = "data/econocausal_synthetic_customers.csv"
DEFAULT_EXPORT_PATH = "outputs/customer_treatment_effects.csv"

def validate_causal_columns(df, treatment_col, outcome_col):
    if df.empty:
        raise ValueError("The dataset contains no rows.")
    missing = [c for c in [treatment_col, outcome_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df[[treatment_col, outcome_col]].isna().any().any():
        raise ValueError("Treatment or outcome contains missing values.")
    t = pd.to_numeric(df[treatment_col], errors="coerce")
    y = pd.to_numeric(df[outcome_col], errors="coerce")
    if not np.isfinite(t.to_numpy(float)).all() or not np.isfinite(y.to_numpy(float)).all():
        raise ValueError("Treatment and outcome must be finite numeric values.")
    if not y.isin([0, 1]).all():
        raise ValueError("The purchase outcome must contain only 0 and 1.")
    if t.nunique() < 2:
        raise ValueError("At least two treatment values are required.")
    if (t < 0).any():
        raise ValueError("Treatment values cannot be negative.")
    levels = sorted(t.unique().astype(float).tolist())
    return {"rows": int(len(df)), "treatment_column": treatment_col,
        "outcome_column": outcome_col,
        "observed_treatment_values": levels,
        "observed_discount_levels": levels,
        "status": "validated"}

def _preprocessor():
    cats = ["customer_segment", "region", "season"]
    nums = [c for c in FEATURE_COLUMNS if c not in cats]
    return ColumnTransformer([
        ("categorical", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False), cats),
        ("numeric", "passthrough", nums)], verbose_feature_names_out=False)

def calculate_nuisance_diagnostics(X, T, Y, discrete_treatment=True):
    cv_y = KFold(n_splits=3, shuffle=True, random_state=42)
    my = RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1)
    py = cross_val_predict(my, X, Y, cv=cv_y)
    ry = Y - py
    out = {"r2": float(r2_score(Y, py)),
        "rmse": float(np.sqrt(mean_squared_error(Y, py))),
        "residual_mean": float(np.mean(ry)), "residual_std": float(np.std(ry))}
    overlap = {}
    if discrete_treatment:
        cv_t = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        mt = RandomForestClassifier(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1)
        p = cross_val_predict(mt, X, T.astype(int), cv=cv_t, method="predict_proba")[:, 1]
        pred = (p >= .5).astype(int)
        td = {"accuracy": float(np.mean(pred == T)),
            "roc_auc": float(roc_auc_score(T, p)),
            "brier_score": float(brier_score_loss(T, p)),
            "residual_mean": float(np.mean(T-p)), "residual_std": float(np.std(T-p))}
        overlap = {"propensity_min": float(p.min()), "propensity_max": float(p.max()),
            "control_propensity_mean": float(p[T == 0].mean()),
            "treated_propensity_mean": float(p[T == 1].mean()),
            "fraction_in_05_95_range": float(np.mean((p >= .05) & (p <= .95))),
            "fraction_below_05": float(np.mean(p < .05)),
            "fraction_above_95": float(np.mean(p > .95))}
    else:
        cv_t = KFold(n_splits=3, shuffle=True, random_state=42)
        mt = RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1)
        pt = cross_val_predict(mt, X, T, cv=cv_t)
        rt = T-pt
        td = {"r2": float(r2_score(T, pt)), "rmse": float(np.sqrt(mean_squared_error(T, pt))),
            "residual_mean": float(np.mean(rt)), "residual_std": float(np.std(rt))}
    return {"outcome_model": out, "treatment_model": td, "overlap": overlap}

def estimate_treatment_effects(data_path=DEFAULT_DATA_PATH, discount_from=None,
                               discount_to=None, export_path=DEFAULT_EXPORT_PATH):
    """No contrast args: discount_received 0 vs 1. Both args: optional discount_percent contrast."""
    df = pd.read_csv(data_path)
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    if df[FEATURE_COLUMNS].isna().any().any():
        raise ValueError("Features contain missing values.")
    legacy = discount_from is not None or discount_to is not None
    if legacy and (discount_from is None or discount_to is None):
        raise ValueError("Supply both discount_from and discount_to for the optional contrast.")
    tc = LEGACY_TREATMENT_COLUMN if legacy else TREATMENT_COLUMN
    val = validate_causal_columns(df, tc, OUTCOME_COLUMN)
    T = pd.to_numeric(df[tc], errors="raise").to_numpy(float)
    Y = pd.to_numeric(df[OUTCOME_COLUMN], errors="raise").to_numpy(float)
    if legacy:
        t0, t1 = float(discount_from), float(discount_to)
        if not np.isfinite([t0, t1]).all() or t0 == t1:
            raise ValueError("Choose two different finite discount values.")
        if min(t0,t1) < T.min() or max(t0,t1) > T.max():
            raise ValueError("Requested discount values are outside observed range.")
        if t0 not in T or t1 not in T:
            raise ValueError("Requested discount values must occur in the dataset.")
    else:
        if not set(np.unique(T)).issubset({0.,1.}) or set(np.unique(T)) != {0.,1.}:
            raise ValueError("discount_received must contain both 0 and 1 only.")
        t0, t1 = 0., 1.
    discrete = not legacy
    X = _preprocessor().fit_transform(df[FEATURE_COLUMNS])
    diag = calculate_nuisance_diagnostics(X, T, Y, discrete_treatment=discrete)
    my = RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1)
    mt = (RandomForestClassifier(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1)
          if discrete else RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1))
    model = LinearDML(model_y=my, model_t=mt, discrete_treatment=discrete, cv=3, random_state=42)
    model.fit(Y, T, X=X)
    effects = np.asarray(model.effect(X, T0=t0, T1=t1), dtype=float).reshape(-1)
    ci = tuple(float(v) for v in model.ate_interval(X, T0=t0, T1=t1, alpha=.05))
    ids = df["customer_id"] if "customer_id" in df.columns else np.arange(len(df))
    exported = pd.DataFrame({"customer_id": ids, "treatment": tc, "control_value": t0,
        "treatment_value": t1, "individual_treatment_effect": effects,
        "individual_effect_percentage_points": effects*100})
    if export_path:
        p = Path(export_path); p.parent.mkdir(parents=True, exist_ok=True); exported.to_csv(p, index=False)
    counts = {str(k): int(v) for k,v in pd.Series(T).value_counts().sort_index().items()}
    return {"rows": int(len(df)), "analysis_mode": "discount_percent_contrast" if legacy else "binary_discount_received",
        "treatment": tc, "outcome": OUTCOME_COLUMN, "discount_from": t0, "discount_to": t1,
        "observed_discount_levels": val["observed_treatment_values"], "treatment_group_counts": counts,
        "average_treatment_effect": float(np.mean(effects)),
        "average_effect_percentage_points": float(np.mean(effects)*100),
        "individual_effects": effects, "customer_effects": exported,
        "export_path": str(Path(export_path)) if export_path else None, "model": model,
        "ate_confidence_interval": ci,
        "ate_confidence_interval_percentage_points": tuple(v*100 for v in ci),
        "nuisance_diagnostics": diag, "validation": val,
        "identification_note": "Causal interpretation requires consistency, positivity/overlap, and no unmeasured confounding; diagnostics/refutation do not establish these assumptions."}

if __name__ == "__main__":
    r = estimate_treatment_effects()
    print("Analysis:", r["analysis_mode"])
    print("ATE percentage points:", round(r["average_effect_percentage_points"], 3))
    print("95% CI percentage points:", r["ate_confidence_interval_percentage_points"])
    print("Diagnostics:", r["nuisance_diagnostics"])
    print("Customer effects CSV:", r["export_path"])
