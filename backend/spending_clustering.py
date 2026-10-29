
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "econocausal_synthetic_customers.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "customer_spending_clusters.csv"

FEATURES = [
    "annual_income_inr",
    "basket_value_inr",
    "past_purchases_12m",
]


def run_spending_clustering(df=None):
    """
    Cluster purchasing customers by income, basket value,
    and purchase history.

    If df is provided, use that dataset.
    Otherwise, load the default synthetic dataset.
    """

    # 1. Load the dataset
    if df is None:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

        df = pd.read_csv(DATA_PATH)
    else:
        df = df.copy()

    # 2. Validate required columns
    required = FEATURES + ["purchased"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # 3. Prepare clustering output
    result = df.copy()
    result["spending_cluster"] = -1

    # 4. Select purchasing customers only
    purchased = pd.to_numeric(result["purchased"], errors="coerce")

    if purchased.isna().any() or not purchased.isin([0, 1]).all():
        raise ValueError("'purchased' must contain only 0 and 1.")

    buyers = purchased == 1

    X = result.loc[buyers, FEATURES].apply(
        pd.to_numeric,
        errors="coerce",
    )

    if len(X) < 3:
        raise ValueError("Not enough purchasing customers to cluster.")

    # 5. Handle missing feature values
    X = X.fillna(X.median())

    if X.isna().any().any():
        raise ValueError(
            "One or more clustering features cannot be imputed."
        )

    # 6. Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 7. Select the number of clusters using silhouette score
    scores = {}
    max_k = min(6, len(X) - 1)

    for k in range(2, max_k + 1):
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        labels = model.fit_predict(X_scaled)

        # Silhouette score requires at least two distinct clusters
        # and fewer clusters than samples.
        if 1 < len(set(labels)) < len(X):
            scores[k] = silhouette_score(X_scaled, labels)

    if not scores:
        raise ValueError("Unable to select a valid cluster count.")

    best_k = max(scores, key=scores.get)

    # 8. Train the final K-Means clustering model
    final_model = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=10,
    )

    buyer_labels = final_model.fit_predict(X_scaled)

    result.loc[buyers, "spending_cluster"] = buyer_labels

    # 9. Save the clustered dataset
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False)

    # 10. Generate cluster profiles
    buyer_results = result.loc[buyers].copy()

    profile = (
        buyer_results
        .groupby("spending_cluster")
        .agg(
            customer_count=("spending_cluster", "size"),
            average_income=("annual_income_inr", "mean"),
            average_basket_value=("basket_value_inr", "mean"),
            average_purchases_12m=("past_purchases_12m", "mean"),
        )
        .round(2)
    )

    # 11. Print results
    print("\n--- Income and Spending Clustering ---")
    print(f"Total customers: {len(result)}")
    print(f"Purchasers clustered: {int(buyers.sum())}")
    print(
        "Non-purchasers left unclustered: "
        f"{int((~buyers).sum())}"
    )
    print(f"Selected number of buyer clusters: {best_k}")

    print("\nSilhouette scores:")

    for k, score in scores.items():
        print(f"k={k}: {score:.4f}")

    print("\nBuyer cluster profiles:")
    print(profile.to_string())

    print(f"\nSaved results to: {OUTPUT_PATH}")

    # 12. Return results for the FastAPI endpoint
    return {
        "best_k": best_k,
        "silhouette_scores": scores,
        "profile": profile,
        "output_path": OUTPUT_PATH,
    }


if __name__ == "__main__":
    run_spending_clustering()
