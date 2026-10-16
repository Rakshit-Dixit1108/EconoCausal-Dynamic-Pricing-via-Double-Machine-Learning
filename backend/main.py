"""FastAPI application for the EconoCausal project."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_service import load_data, get_data_summary
from optimization import (
    analyze_discount_levels,
    recommend_discount,
)


app = FastAPI(
    title="EconoCausal API",
    description=(
        "API for customer data validation and exploratory "
        "discount optimization."
    ),
    version="1.0.0",
)

# Permit requests from the local Vite frontend and admin frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Return basic API information."""
    return {
        "project": "EconoCausal",
        "message": "EconoCausal API is running.",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Check API availability."""
    return {
        "status": "healthy",
        "service": "EconoCausal API",
    }


@app.get("/data-summary")
def data_summary():
    """Return dataset validation and summary statistics."""
    try:
        df = load_data()
        summary = get_data_summary(df)

        return {
            "status": "success",
            "data": summary,
        }
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate dataset summary.",
        ) from exc


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
    """Compare observed discount levels and return a recommendation.

    This is an exploratory comparison of observed data, not an
    estimate of personalized causal effects or business profit.
    """
    try:
        df = load_data()
        summary = analyze_discount_levels(df)

        target_customers = customers or len(df)

        best, candidates = recommend_discount(
            summary,
            target_customers=target_customers,
            budget_inr=budget_inr,
        )

        # Convert pandas/numpy values to ordinary JSON-compatible values.
        discount_levels = []
        for _, row in summary.iterrows():
            discount_levels.append({
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
            })

        recommendation = None
        if best is not None:
            recommendation = {
                "discount_percent": float(
                    best["discount_percent"]
                ),
                "avg_net_revenue_inr": round(
                    float(best["avg_net_revenue_inr"]), 2
                ),
                "estimated_total_discount_cost_inr": round(
                    float(
                        best["estimated_total_discount_cost_inr"]
                    ),
                    2,
                ),
                "customers_evaluated": target_customers,
            }

        eligible_levels = [
            float(row["discount_percent"])
            for _, row in candidates.iterrows()
        ]

        return {
            "status": "success",
            "analysis_type": "exploratory_observed_comparison",
            "customers_evaluated": target_customers,
            "budget_inr": budget_inr,
            "discount_levels": discount_levels,
            "eligible_discount_levels": eligible_levels,
            "recommendation": recommendation,
            "limitations": [
                "Observed comparisons do not establish causation.",
                "This endpoint does not estimate individual "
                "customer treatment effects.",
                "Net revenue is not profit.",
                "Budget estimates assume observed average discount "
                "costs are representative of the target customers.",
            ],
        }

    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate discount analysis.",
        ) from exc
