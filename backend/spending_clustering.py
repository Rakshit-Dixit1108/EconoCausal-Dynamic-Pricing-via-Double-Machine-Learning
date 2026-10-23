
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


def run_spending_clustering():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = FEATURES + ["purchased"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    result = df.copy()
    result["spending_cluster"] = -1

    buyers = result["purchased"] == 1
    X = result.loc[buyers, FEATURES].apply(
        pd.to_numeric, errors="coerce"
    )

    if len(X) < 3:
        raise ValueError("Not enough purchasing customers to cluster.")

    
    X = X.fillna(X.median())

    if X.isna().any().any():
        raise ValueError("One or more clustering features cannot be imputed.")

    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    
    scores = {}
    max_k = min(6, len(X) - 1)

    for k in range(2, max_k + 1):
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )
        labels = model.fit_predict(X_scaled)

        if len(set(labels)) > 1:
            scores[k] = silhouette_score(X_scaled, labels)

    if not scores:
        raise ValueError("Unable to select a valid cluster count.")

    best_k = max(scores, key=scores.get)

    final_model = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=10,
    )
    buyer_labels = final_model.fit_predict(X_scaled)

    result.loc[buyers, "spending_cluster"] = buyer_labels
    result.to_csv(OUTPUT_PATH, index=False)

    
    profile = (
        result.loc[buyers]
        .groupby("spending_cluster")
        .agg(
            customer_count=("spending_cluster", "size"),
            average_income=("annual_income_inr", "mean"),
            average_basket_value=("basket_value_inr", "mean"),
            average_purchases_12m=("past_purchases_12m", "mean"),
        )
        .round(2)
    )

    print("\n--- Income and Spending Clustering ---")
    print(f"Total customers: {len(result)}")
    print(f"Purchasers clustered: {int(buyers.sum())}")
    print(f"Non-purchasers left unclustered: {int((~buyers).sum())}")
    print(f"Selected number of buyer clusters: {best_k}")

    print("\nSilhouette scores:")
    for k, score in scores.items():
        print(f"k={k}: {score:.4f}")

    print("\nBuyer cluster profiles:")
    print(profile.to_string())

    print(f"\nSaved results to: {OUTPUT_PATH}")

    return {
        "best_k": best_k,
        "silhouette_scores": scores,
        "profile": profile,
        "output_path": OUTPUT_PATH,
    }


if __name__ == "__main__":
    run_spending_clustering()
