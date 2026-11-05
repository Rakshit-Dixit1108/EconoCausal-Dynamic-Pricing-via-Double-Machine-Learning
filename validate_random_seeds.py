
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score, brier_score_loss

# Load dataset
df = pd.read_csv("data/econocausal_synthetic_customers.csv")

# Prepare features and target
X = df.drop(columns=[
    "customer_id", "purchased", "basket_value_inr",
    "discount_cost_inr", "net_revenue_inr",
    "discount_percent", "discount_received"
])

X = pd.get_dummies(X, drop_first=True)
y = df["purchased"]

# Selected model configuration
seeds = [21, 42, 52, 62, 72]
results = []

for seed in seeds:

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=seed,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=20,
        max_features="sqrt",
        random_state=seed,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    results.append({
        "random_seed": seed,
        "roc_auc": roc_auc_score(y_test, probabilities),
        "f1_score": f1_score(y_test, predictions),
        "brier_score": brier_score_loss(y_test, probabilities)
    })

# Save results
results_df = pd.DataFrame(results)

results_df.to_csv(
    "outputs/random_seed_results.csv",
    index=False
)

print("\nExperiment 11 - Random Seed Validation")
print(results_df.to_string(index=False))

print("\nAverage Performance:")
print(results_df[["roc_auc", "f1_score", "brier_score"]].mean())

print("\nResults saved successfully!")
