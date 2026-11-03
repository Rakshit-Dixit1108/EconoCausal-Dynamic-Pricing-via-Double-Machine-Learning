
"""FastAPI application for the EconoCausal project."""

from pathlib import Path
import shutil
import tempfile

import pandas as pd

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware

from data_service import load_data, get_data_summary
from optimization import analyze_discount_levels, recommend_discount
from customer_effects import estimate_segment_effects
from spending_clustering import run_spending_clustering


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="EconoCausal API",
    description=(
        "API for customer data validation, exploratory discount "
        "optimization, customer segment effects, and spending clusters."
    ),
    version="1.3.0",
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

IMPORTED_DATA_PATH = DATA_DIR / "imported_customers.csv"

DEFAULT_DATA_PATH = (
    DATA_DIR / "econocausal_synthetic_customers.csv"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

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


# ============================================================
# ACTIVE DATASET
# ============================================================

def load_current_data():
    """Load imported data when available; otherwise use default."""

    selected_path = (
        IMPORTED_DATA_PATH
        if IMPORTED_DATA_PATH.exists()
        else DEFAULT_DATA_PATH
    )

    return load_data(file_path=selected_path)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    """Return basic API information."""

    return {
        "project": "EconoCausal",
        "message": "EconoCausal API is running.",
        "version": "1.3.0",
        "docs": "/docs",
        "endpoints": [
            "/health",
            "/data-summary",
            "/upload-csv",
            "/optimization",
            "/segment-effects",
            "/spending-clusters",
        ],
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():
    """Check API availability."""

    return {
        "status": "healthy",
        "service": "EconoCausal API",
    }


# ============================================================
# CSV UPLOAD ENDPOINT
# ============================================================

@app.post("/upload-csv")
def upload_csv(file: UploadFile = File(...)):
    """Validate a customer CSV and make it the active dataset."""

    if not file.filename or Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Please upload a file with the .csv extension.",
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temporary_path = None

    try:
        # Save uploaded file temporarily.
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".csv",
            dir=DATA_DIR,
            delete=False,
        ) as temp_file:

            temporary_path = Path(temp_file.name)

            shutil.copyfileobj(file.file, temp_file)

        # Validate before replacing the active dataset.
        df = load_data(file_path=temporary_path)

        # Activate uploaded dataset after successful validation.
        temporary_path.replace(IMPORTED_DATA_PATH)
        temporary_path = None

        summary = get_data_summary(df)

        return {
            "status": "success",
            "message": "Dataset imported and validated successfully.",
            "filename": Path(file.filename).name,
            "active_dataset": IMPORTED_DATA_PATH.name,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
            "summary": summary,
        }

    except (ValueError, pd.errors.ParserError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Dataset validation failed: {exc}",
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to import the dataset.",
        ) from exc

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

        file.file.close()


# ============================================================
# DATA SUMMARY ENDPOINT
# ============================================================

@app.get("/data-summary")
def data_summary():
    """Return summary statistics for the active dataset."""

    try:
        df = load_current_data()

        return {
            "status": "success",
            "data": get_data_summary(df),
        }

    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate dataset summary.",
        ) from exc


# ============================================================
# DISCOUNT OPTIMIZATION ENDPOINT
# ============================================================

@app.get("/optimization")
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
):
    """Compare observed discount levels; this is not causal."""

    try:
        df = load_current_data()

        summary = analyze_discount_levels(df)

        target_customers = (
            customers
            if customers is not None
            else len(df)
        )

        best, candidates = recommend_discount(
            summary,
            target_customers=target_customers,
            budget_inr=budget_inr,
        )

        # ----------------------------------------------------
        # DISCOUNT LEVELS
        # ----------------------------------------------------

        discount_levels = []

        for _, row in summary.iterrows():

            discount_levels.append({
                "discount_percent": float(
                    row["discount_percent"]
                ),
                "customers": int(
                    row["customers"]
                ),
                "purchase_rate_percent": round(
                    float(row["purchase_rate_percent"]),
                    2,
                ),
                "avg_discount_cost_inr": round(
                    float(row["avg_discount_cost_inr"]),
                    2,
                ),
                "avg_net_revenue_inr": round(
                    float(row["avg_net_revenue_inr"]),
                    2,
                ),
            })

        # ----------------------------------------------------
        # RECOMMENDATION
        # ----------------------------------------------------

        recommendation = None

        if best is not None:

            recommendation = {
                "discount_percent": float(
                    best["discount_percent"]
                ),
                "avg_net_revenue_inr": round(
                    float(best["avg_net_revenue_inr"]),
                    2,
                ),
                "estimated_total_discount_cost_inr": round(
                    float(
                        best[
                            "estimated_total_discount_cost_inr"
                        ]
                    ),
                    2,
                ),
                "customers_evaluated": target_customers,
            }

        # ----------------------------------------------------
        # API RESPONSE
        # ----------------------------------------------------

        return {
            "status": "success",
            "analysis_type": "exploratory_observed_comparison",
            "customers_evaluated": target_customers,
            "budget_inr": budget_inr,
            "discount_levels": discount_levels,
            "eligible_discount_levels": [
                float(row["discount_percent"])
                for _, row in candidates.iterrows()
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
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate discount analysis.",
        ) from exc


# ============================================================
# CUSTOMER SEGMENT EFFECTS ENDPOINT
# ============================================================

@app.get("/segment-effects")
def segment_effects():
    """Estimate group-level discount effects using active data."""

    try:
        df = load_current_data()

        gate_model = estimate_segment_effects(df)

        intervals = gate_model.confint(level=0.95)

        segments = []

        for group, row in intervals.iterrows():

            effect = float(row["effect"])
            lower = float(row["2.5 %"])
            upper = float(row["97.5 %"])

            segments.append({
                "segment": str(group).replace("Group_", ""),
                "effect": round(effect, 6),
                "effect_percentage_points": round(
                    effect * 100,
                    2,
                ),
                "confidence_interval_95": {
                    "lower": round(lower, 6),
                    "upper": round(upper, 6),
                },
                "confidence_interval_percentage_points": {
                    "lower": round(lower * 100, 2),
                    "upper": round(upper * 100, 2),
                },
            })

        return {
            "status": "success",
            "analysis_type": "group_average_treatment_effect",
            "outcome": "purchase_probability",
            "treatment": "discount_received",
            "segments": segments,
            "limitations": [
                (
                    "Results are group-level estimates, not individual "
                    "customer effects."
                ),
                "Causal interpretation depends on identification assumptions.",
                "A confidence interval containing zero indicates uncertainty.",
            ],
        }

    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to estimate customer segment effects.",
        ) from exc


# ============================================================
# SPENDING CLUSTERS ENDPOINT
# ============================================================

@app.get("/spending-clusters")
def spending_clusters():
    """Return K-Means clusters based on income and spending."""

    try:
        df = load_current_data()

        result = run_spending_clustering(df)

        profile = result["profile"]

        cluster_profiles = []

        for cluster_id, row in profile.iterrows():

            cluster_profiles.append({
                "cluster_id": int(cluster_id),
                "customer_count": int(
                    row["customer_count"]
                ),
                "average_income_inr": float(
                    row["average_income"]
                ),
                "average_basket_value_inr": float(
                    row["average_basket_value"]
                ),
                "average_purchases_12m": float(
                    row["average_purchases_12m"]
                ),
            })

        return {
            "status": "success",
            "algorithm": "K-Means",
            "features": [
                "annual_income_inr",
                "basket_value_inr",
                "past_purchases_12m",
            ],
            "selected_cluster_count": int(
                result["best_k"]
            ),
            "silhouette_scores": {
                str(k): float(score)
                for k, score in result[
                    "silhouette_scores"
                ].items()
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
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate spending clusters.",
        ) from exc
