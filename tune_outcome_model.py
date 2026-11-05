
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
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

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Hyperparameter configurations
configurations = [
    {"trees": 100, "min_leaf": 5},
    {"trees": 200, "min_leaf": 10},
    {"trees": 300, "min_leaf": 20}
]

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

results = []

for config in configurations:
    model = RandomForestClassifier(
        n_estimators=config["trees"],
        min_samples_leaf=config["min_leaf"],
        max_features="sqrt",
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
        "trees": config["trees"],
        "min_leaf": config["min_leaf"],
        "roc_auc": roc_auc_score(y_test, probabilities),
        "f1_score": f1_score(y_test, predictions),
        "brier_score": brier_score_loss(y_test, probabilities),
        "cv_roc_auc_mean": cv_scores.mean(),
        "cv_roc_auc_std": cv_scores.std()
    })

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv("outputs/hyperparameter_results.csv", index=False)

print("\nHyperparameter Tuning Results")
print(results_df.to_string(index=False))
print("\nResults saved successfully!")
