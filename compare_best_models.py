
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
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

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Compare selected configurations
configurations = [
    {"name": "Baseline", "trees": 200, "leaf": 10, "features": "sqrt"},
    {"name": "Experiment 6", "trees": 300, "leaf": 20, "features": "sqrt"},
    {"name": "Experiment 7", "trees": 300, "leaf": 30, "features": "sqrt"},
    {"name": "Experiment 8", "trees": 300, "leaf": 20, "features": "log2"}
]

cv = StratifiedKFold(
    n_splits=3, shuffle=True, random_state=42
)

results = []

for config in configurations:
    model = RandomForestClassifier(
        n_estimators=config["trees"],
        min_samples_leaf=config["leaf"],
        max_features=config["features"],
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    cv_scores = cross_val_score(
        model, X_train, y_train,
        cv=cv, scoring="roc_auc", n_jobs=-1
    )

    results.append({
        "configuration": config["name"],
        "trees": config["trees"],
        "min_leaf": config["leaf"],
        "max_features": config["features"],
        "roc_auc": roc_auc_score(y_test, probabilities),
        "f1_score": f1_score(y_test, predictions),
        "brier_score": brier_score_loss(y_test, probabilities),
        "cv_roc_auc_mean": cv_scores.mean(),
        "cv_roc_auc_std": cv_scores.std()
    })

# Save results
results_df = pd.DataFrame(results)

results_df.to_csv(
    "outputs/combined_model_comparison.csv",
    index=False
)

print("\nExperiment 10 - Combined Model Comparison")
print(results_df.to_string(index=False))
print("\nResults saved successfully!")
