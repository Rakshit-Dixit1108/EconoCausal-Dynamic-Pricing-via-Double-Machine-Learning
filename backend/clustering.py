
"""Customer clustering module for EconoCausal."""

from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = (
    PROJECT_ROOT / "data" / "econocausal_synthetic_customers.csv"
)
OUTPUT_PATH = PROJECT_ROOT / "data" / "customer_clusters.csv"

# Behavioral features used to discover customer groups.
# We deliberately exclude purchased, discount_received,
# customer_segment, and revenue columns from clustering.
FEATURES = [
    "age",
    "annual_income_inr",
    "past_purchases_12m",
    "days_since_last_purchase",
    "website_visits_30d",
    "email_engagement_score",
]


def run_clustering():
    """Cluster customers and save their assigned cluster labels."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    missing = [col for col in FEATURES if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert features to numeric and handle missing values.
    X = df[FEATURES].apply(pd.to_numeric, errors="coerce")
    X = X.fillna(X.median())

    # K-Means is distance-based, so scale features first.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Compare candidate cluster counts using silhouette score.
    scores = {}
    max_k = min(6, len(df) - 1)

    for k in range(2, max_k + 1):
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )
        labels = model.fit_predict(X_scaled)

        # Silhouette score requires at least two clusters.
        if len(set(labels)) > 1:
            scores[k] = silhouette_score(X_scaled, labels)

    if not scores:
        raise ValueError("Unable to select a valid cluster count.")

    best_k = max(scores, key=scores.get)

    # Fit the final model using the best candidate k.
    final_model = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=10,
    )
    df["cluster_id"] = final_model.fit_predict(X_scaled)

    # Save a separate file; the original dataset stays unchanged.
    df.to_csv(OUTPUT_PATH, index=False)

    # Summarize the behavioral profile of each cluster.
    profile = df.groupby("cluster_id")[FEATURES].mean().round(2)
    profile.insert(
        0,
        "customer_count",
        df.groupby("cluster_id").size(),
    )

    print("\n--- EconoCausal Customer Clustering ---")
    print(f"Customers analyzed: {len(df)}")
    print(f"Selected number of clusters: {best_k}")
    print("\nSilhouette scores by candidate k:")
    for k, score in scores.items():
        print(f"k={k}: {score:.4f}")

    print("\nCluster profiles:")
    print(profile.to_string())

    print(f"\nClustered dataset saved to: {OUTPUT_PATH}")

    return {
        "best_k": best_k,
        "silhouette_scores": scores,
        "profile": profile,
    }


if __name__ == "__main__":
    run_clustering()
