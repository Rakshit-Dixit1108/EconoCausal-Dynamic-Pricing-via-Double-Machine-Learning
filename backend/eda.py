"""FastAPI application for the EconoCausal project."""

from pathlib import Path
import shutil
import tempfile

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.data_service import load_data, get_data_summary
from backend.optimization import analyze_discount_levels, recommend_discount
from backend.customer_effects import estimate_segment_effects
from backend.spending_clustering import run_spending_clustering


# ---------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------
app = FastAPI(
    title="EconoCausal API",
    description=(
        "API for customer data validation, exploratory discount "
        "optimization, customer segment effects, spending clusters, "
        "and advanced causal analysis."
    ),
    version="1.4.0",
)

# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
IMPORTED_DATA_PATH = DATA_DIR / "imported_customers.csv"
DEFAULT_DATA_PATH = DATA_DIR / "econocausal_synthetic_customers.csv"
ADVANCED_RESULTS_DIR = PROJECT_ROOT / "advanced_causal_results"


# ---------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# Dataset helper
# ---------------------------------------------------------------------
def load_current_data():
    """Load imported data if present; otherwise load the default dataset."""
    selected_path = (
        IMPORTED_DATA_PATH if IMPORTED_DATA_PATH.exists() else DEFAULT_DATA_PATH
    )
    if not selected_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {selected_path}. "
            "Place the default CSV in the project's data folder or upload one."
        )
    return load_data(file_path=selected_path)


# ---------------------------------------------------------------------
# Root and health
# ---------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "project": "EconoCausal",
        "message": "EconoCausal API is running.",
        "version": "1.4.0",
        "docs": "/docs",
        "endpoints": [
            "/health",
            "/data-summary",
            "/dashboard-data",
            "/upload-csv",
            "/optimization",
            "/segment-effects",
            "/spending-clusters",
            "/advanced-causal/multilevel",
            "/advanced-causal/propensity",
            "/advanced-causal/diagnostics",
            "/advanced-causal/refutation",
        ],
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "EconoCausal API"}


# ---------------------------------------------------------------------
# CSV upload
# ---------------------------------------------------------------------
@app.post("/upload-csv")
def upload_csv(file: UploadFile = File(...)):
    """Validate an uploaded CSV before activating it as the current dataset."""
    if not file.filename or Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Please upload a file with the .csv extension.",
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        # Save to a temporary file first so an invalid upload cannot replace
        # the currently active dataset.
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".csv", dir=DATA_DIR, delete=False
        ) as temp_file:
            temporary_path = Path(temp_file.name)
            shutil.copyfileobj(file.file, temp_file)

        # Validate the temporary CSV using the project's data service.
        df = load_data(file_path=temporary_path)

        # Activate only after validation succeeds.
        temporary_path.replace(IMPORTED_DATA_PATH)
        temporary_path = None

        return {
            "status": "success",
            "message": "Dataset imported and validated successfully.",
            "filename": Path(file.filename).name,
            "active_dataset": IMPORTED_DATA_PATH.name,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
            "summary": get_data_summary(df),
        }

    except (ValueError, pd.errors.ParserError) as exc:
        raise HTTPException(
            status_code=422, detail=f"Dataset validation failed: {exc}"
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Unable to import the dataset: {exc}"
        ) from exc
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        file.file.close()


# ---------------------------------------------------------------------
# Data summary
# ---------------------------------------------------------------------
@app.get("/data-summary")
def data_summary():
    try:
        df = load_current_data()
        return {"status": "success", "data": get_data_summary(df)}
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Unable to generate dataset summary: {exc}"
        ) from exc


# ---------------------------------------------------------------------
# Dashboard data (charts and KPI cards)
# ---------------------------------------------------------------------
@app.get("/dashboard-data")
def dashboard_data():
    """Return chart-ready summaries from the currently active dataset."""
    try:
        df = load_current_data()
        required = {"age", "purchased", "customer_segment", "region", "season"}
        missing = sorted(required.difference(df.columns))
        if missing:
            raise ValueError(
                "Dashboard requires these columns, missing from dataset: "
                + ", ".join(missing)
            )

        total = int(len(df))
        purchased_values = pd.to_numeric(df["purchased"], errors="coerce").fillna(0)
        purchased = int(purchased_values.sum())
        not_purchased = max(total - purchased, 0)

        age = pd.to_numeric(df["age"], errors="coerce")
        age_bins = [0, 20, 30, 40, 50, 60, 70, float("inf")]
        age_labels = ["0–19", "20–29", "30–39", "40–49", "50–59", "60–69", "70+"]
        age_group = pd.cut(age, bins=age_bins, labels=age_labels, right=False)
        age_counts = age_group.value_counts(sort=False).reindex(age_labels, fill_value=0)

        age_purchase = []
        for label in age_labels:
            subset = df.loc[age_group == label]
            count = int(len(subset))
            bought = int(
                pd.to_numeric(subset["purchased"], errors="coerce").fillna(0).sum()
            )
            age_purchase.append(
                {
                    "age_group": label,
                    "customers": count,
                    "purchasers": bought,
                    "purchase_rate_percent": round(bought / count * 100 if count else 0, 2),
                }
            )

        def distribution(column, key):
            counts = df[column].fillna("Unknown").astype(str).value_counts()
            return [
                {key: str(value), "customers": int(count)}
                for value, count in counts.items()
            ]

        return {
            "status": "success",
            "rows": total,
            "total_customers": total,
            "purchasers": purchased,
            "non_purchasers": not_purchased,
            "overall_purchase_rate": round(purchased / total * 100 if total else 0, 2),
            "columns": list(df.columns),
            "age_distribution": [
                {"age_group": str(label), "customers": int(count)}
                for label, count in age_counts.items()
            ],
            "age_vs_purchases": age_purchase,
            "segment_distribution": distribution("customer_segment", "segment"),
            "region_distribution": distribution("region", "region"),
            "season_distribution": distribution("season", "season"),
            "purchase_distribution": [
                {"label": "Purchased", "count": purchased},
                {"label": "Not purchased", "count": not_purchased},
            ],
            "data_summary": get_data_summary(df),
        }
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Unable to generate dashboard data: {exc}"
        ) from exc


# ---------------------------------------------------------------------
# Discount optimization (observational comparison, not causal)
# ---------------------------------------------------------------------
@app.get("/optimization")
def optimization(
    budget_inr: float | None = Query(
        default=None, ge=0, description="Optional total discount budget in INR."
    ),
    customers: int | None = Query(
        default=None, gt=0, description="Number of customers to evaluate."
    ),
):
    try:
        df = load_current_data()
        summary = analyze_discount_levels(df)
        target_customers = customers if customers is not None else len(df)

        best, candidates = recommend_discount(
            summary, target_customers=target_customers, budget_inr=budget_inr
        )

        discount_levels = []
        for _, row in summary.iterrows():
            discount_levels.append(
                {
                    "discount_percent": float(row["discount_percent"]),
                    "customers": int(row["customers"]),
                    "purchase_rate_percent": round(float(row["purchase_rate_percent"]), 2),
                    "avg_discount_cost_inr": round(float(row["avg_discount_cost_inr"]), 2),
                    "avg_net_revenue_inr": round(float(row["avg_net_revenue_inr"]), 2),
                }
            )

        recommendation = None
        if best is not None:
            recommendation = {
                "discount_percent": float(best["discount_percent"]),
                "avg_net_revenue_inr": round(float(best["avg_net_revenue_inr"]), 2),
                "estimated_total_discount_cost_inr": round(
                    float(best["estimated_total_discount_cost_inr"]), 2
                ),
                "customers_evaluated": int(target_customers),
            }

        return {
            "status": "success",
            "analysis_type": "exploratory_observed_comparison",
            "customers_evaluated": int(target_customers),
            "budget_inr": budget_inr,
            "discount_levels": discount_levels,
            "eligible_discount_levels": [
                float(row["discount_percent"]) for _, row in candidates.iterrows()
            ],
            "recommendation": recommendation,
            "limitations": [
                "Observed comparisons do not establish causation.",
                "This endpoint does not estimate individual customer effects.",
                "Net revenue is not profit.",
                (
                    "Budget estimates assume observed average discount costs "
                    "are representative of the target customers."
                ),
            ],
        }
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Unable to generate discount analysis: {exc}"
        ) from exc


# ---------------------------------------------------------------------
# Customer segment effects
# ---------------------------------------------------------------------
@app.get("/segment-effects")
def segment_effects():
    """Estimate group-level discount effects using the active dataset."""
    try:
        df = load_current_data()
        gate_model = estimate_segment_effects(df)
        intervals = gate_model.confint(level=0.95)

        segments = []
        for group, row in intervals.iterrows():
            effect = float(row["effect"])
            lower = float(row["2.5 %"])
            upper = float(row["97.5 %"])
            segments.append(
                {
                    "segment": str(group).replace("Group_", ""),
                    "effect": round(effect, 6),
                    "effect_percentage_points": round(effect * 100, 2),
                    "confidence_interval_95": {
                        "lower": round(lower, 6),
                        "upper": round(upper, 6),
                    },
                    "confidence_interval_percentage_points": {
                        "lower": round(lower * 100, 2),
                        "upper": round(upper * 100, 2),
                    },
                }
            )

        return {
            "status": "success",
            "analysis_type": "group_average_treatment_effect",
            "outcome": "purchase_probability",
            "treatment": "discount_received",
            "segments": segments,
            "limitations": [
                "Results are group-level estimates, not individual customer effects.",
                "Causal interpretation depends on identification assumptions.",
                "A confidence interval containing zero indicates uncertainty.",
            ],
        }
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to estimate customer segment effects: {exc}",
        ) from exc


# ---------------------------------------------------------------------
# Spending clusters
# ---------------------------------------------------------------------
@app.get("/spending-clusters")
def spending_clusters():
    """Return K-Means spending clusters for purchasers in the active dataset."""
    try:
        df = load_current_data()
        result = run_spending_clustering(df)
        profile = result["profile"]

        cluster_profiles = []
        for cluster_id, row in profile.iterrows():
            cluster_profiles.append(
                {
                    "cluster_id": int(cluster_id),
                    "customer_count": int(row["customer_count"]),
                    "average_income_inr": float(row["average_income"]),
                    "average_basket_value_inr": float(row["average_basket_value"]),
                    "average_purchases_12m": float(row["average_purchases_12m"]),
                }
            )

        return {
            "status": "success",
            "algorithm": "K-Means",
            "features": [
                "annual_income_inr",
                "basket_value_inr",
                "past_purchases_12m",
            ],
            "selected_cluster_count": int(result["best_k"]),
            "silhouette_scores": {
                str(k): float(score) for k, score in result["silhouette_scores"].items()
            },
            "cluster_profiles": cluster_profiles,
            "output_file": "data/customer_spending_clusters.csv",
            "limitations": [
                "Clustering is descriptive and does not establish causation.",
                "Only purchasers are assigned to spending clusters.",
                "Silhouette score alone does not establish business usefulness.",
                "Cluster IDs are arbitrary labels.",
            ],
        }
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Unable to generate spending clusters: {exc}"
        ) from exc


# ---------------------------------------------------------------------
# Advanced causal analysis (serves previously generated analysis files)
# ---------------------------------------------------------------------
def _read_advanced_csv(filename: str):
    """Read an advanced-analysis CSV and return records or a clear 404."""
    file_path = ADVANCED_RESULTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Advanced result '{filename}' was not found. "
                "Run the corresponding advanced_causal analysis first."
            ),
        )
    try:
        frame = pd.read_csv(file_path)
        # Convert NaN values to JSON nulls.
        return frame.where(pd.notna(frame), None).to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Could not read {filename}: {exc}"
        ) from exc


@app.get("/advanced-causal/multilevel")
def advanced_multilevel():
    return _read_advanced_csv("multilevel_effects.csv")


@app.get("/advanced-causal/propensity")
def advanced_propensity():
    return _read_advanced_csv("propensity_summary.csv")


@app.get("/advanced-causal/diagnostics")
def advanced_diagnostics():
    # Expected CSV columns: discount_level, feature, smd, absolute_smd,
    # balance_status. If your diagnostics script uses different headers,
    # adapt the frontend mapping to its actual output.
    return _read_advanced_csv("treatment_balance.csv")


@app.get("/advanced-causal/refutation")
def advanced_refutation():
    file_path = ADVANCED_RESULTS_DIR / "refutation_results.txt"
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Refutation results were not found. "
                "Run backend.advanced_causal.refutation first."
            ),
        )
    try:
        return {"results": file_path.read_text(encoding="utf-8")}
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Could not read refutation results: {exc}"
        ) from exc
