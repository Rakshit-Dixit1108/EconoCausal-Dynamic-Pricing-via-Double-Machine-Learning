"""FastAPI application for the EconoCausal project.

Run from the repository root:
    python -m uvicorn backend.main:app --reload
"""

from pathlib import Path
import shutil
import tempfile
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Always use package-qualified imports when starting with
# `python -m uvicorn backend.main:app`.
from backend.data_service import get_data_summary, load_data
from backend.optimization import analyze_discount_levels, recommend_discount
from backend.customer_effects import estimate_segment_effects
from backend.spending_clustering import run_spending_clustering


# ---------------------------------------------------------------------------
# Application configuration
# ---------------------------------------------------------------------------
APP_VERSION = "1.3.1"

app = FastAPI(
    title="EconoCausal API",
    description=(
        "API for dataset validation, discount analysis, customer segment "
        "effects, and spending clusters."
    ),
    version=APP_VERSION,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
IMPORTED_DATA_PATH = DATA_DIR / "imported_customers.csv"
DEFAULT_DATA_PATH = DATA_DIR / "econocausal_synthetic_customers.csv"

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


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def load_current_data() -> pd.DataFrame:
    """Load imported CSV when available; otherwise load the default dataset."""
    selected_path = (
        IMPORTED_DATA_PATH if IMPORTED_DATA_PATH.is_file() else DEFAULT_DATA_PATH
    )
    if not selected_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {selected_path}. "
            "Put the default CSV in the project's data folder or upload a CSV."
        )
    return load_data(file_path=selected_path)


def _raise_data_error(exc: Exception, message: str) -> None:
    """Convert expected data errors to HTTP responses without leaking tracebacks."""
    if isinstance(exc, FileNotFoundError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if isinstance(exc, (ValueError, pd.errors.ParserError)):
        raise HTTPException(status_code=422, detail=f"{message}: {exc}") from exc
    raise HTTPException(status_code=500, detail=f"{message}: {exc}") from exc


# ---------------------------------------------------------------------------
# Root and health
# ---------------------------------------------------------------------------
@app.get("/", tags=["System"])
def root() -> dict[str, Any]:
    return {
        "project": "EconoCausal",
        "message": "EconoCausal API is running.",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/data-summary",
            "/upload-csv",
            "/optimization",
            "/segment-effects",
            "/spending-clusters",
        ],
    }


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "EconoCausal API"}


# ---------------------------------------------------------------------------
# CSV upload
# ---------------------------------------------------------------------------
@app.post("/upload-csv", tags=["Dataset"])
def upload_csv(file: UploadFile = File(...)) -> dict[str, Any]:
    """Validate an uploaded CSV and activate it only after validation succeeds."""
    if not file.filename or Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Please upload a file with the .csv extension.",
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".csv", dir=DATA_DIR, delete=False
        ) as temp_file:
            temporary_path = Path(temp_file.name)
            shutil.copyfileobj(file.file, temp_file)

        # Validation must complete before replacing the active dataset.
        dataframe = load_data(file_path=temporary_path)
        summary = get_data_summary(dataframe)

        temporary_path.replace(IMPORTED_DATA_PATH)
        temporary_path = None

        return {
            "status": "success",
            "message": "Dataset imported and validated successfully.",
            "filename": Path(file.filename).name,
            "active_dataset": IMPORTED_DATA_PATH.name,
            "rows": int(dataframe.shape[0]),
            "columns": int(dataframe.shape[1]),
            "column_names": list(dataframe.columns),
            "summary": summary,
        }
    except HTTPException:
        raise
    except Exception as exc:
        _raise_data_error(exc, "Unable to import dataset")
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        file.file.close()


# ---------------------------------------------------------------------------
# Data summary
# ---------------------------------------------------------------------------
@app.get("/data-summary", tags=["Dataset"])
def data_summary() -> dict[str, Any]:
    try:
        dataframe = load_current_data()
        return {"status": "success", "data": get_data_summary(dataframe)}
    except Exception as exc:
        _raise_data_error(exc, "Unable to generate dataset summary")


# ---------------------------------------------------------------------------
# Discount analysis (observational, not causal)
# ---------------------------------------------------------------------------
@app.get("/optimization", tags=["Analysis"])
def optimization(
    budget_inr: float | None = Query(
        default=None,
        ge=0,
        description="Optional total discount budget in INR.",
    ),
    customers: int | None = Query(
        default=None,
        gt=0,
        description="Number of customers to evaluate.",
    ),
) -> dict[str, Any]:
    try:
        dataframe = load_current_data()
        summary = analyze_discount_levels(dataframe)
        target_customers = int(customers or len(dataframe))

        best, candidates = recommend_discount(
            summary,
            target_customers=target_customers,
            budget_inr=budget_inr,
        )

        discount_levels = []
        for _, row in summary.iterrows():
            discount_levels.append(
                {
                    "discount_percent": float(row["discount_percent"]),
                    "customers": int(row["customers"]),
                    "purchase_rate_percent": round(
                        float(row["purchase_rate_percent"]), 2
                    ),
                    "avg_discount_cost_inr": round(
                        float(row["avg_discount_cost_inr"]), 2
                    ),
                    "avg_net_revenue_inr": round(
                        float(row["avg_net_revenue_inr"]), 2
                    ),
                }
            )

        recommendation = None
        if best is not None:
            recommendation = {
                "discount_percent": float(best["discount_percent"]),
                "avg_net_revenue_inr": round(
                    float(best["avg_net_revenue_inr"]), 2
                ),
                "estimated_total_discount_cost_inr": round(
                    float(best["estimated_total_discount_cost_inr"]), 2
                ),
                "customers_evaluated": target_customers,
            }

        return {
            "status": "success",
            "analysis_type": "exploratory_observed_comparison",
            "customers_evaluated": target_customers,
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
    except Exception as exc:
        _raise_data_error(exc, "Unable to generate discount analysis")


# ---------------------------------------------------------------------------
# Customer segment effects
# ---------------------------------------------------------------------------
@app.get("/segment-effects", tags=["Analysis"])
def segment_effects() -> dict[str, Any]:
    """Return group-level discount-effect estimates and 95% confidence intervals."""
    try:
        dataframe = load_current_data()
        model = estimate_segment_effects(dataframe)
        intervals = model.confint(level=0.95)

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
    except Exception as exc:
        _raise_data_error(exc, "Unable to estimate customer segment effects")


# ---------------------------------------------------------------------------
# Spending clusters
# ---------------------------------------------------------------------------
@app.get("/spending-clusters", tags=["Analysis"])
def spending_clusters() -> dict[str, Any]:
    """Return K-Means spending clusters for purchasers in the active dataset."""
    try:
        dataframe = load_current_data()
        result = run_spending_clustering(dataframe)
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
                str(k): float(score)
                for k, score in result["silhouette_scores"].items()
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
    except Exception as exc:
        _raise_data_error(exc, "Unable to generate spending clusters")
