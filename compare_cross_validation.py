
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold

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

# Fixed Random Forest configuration
model = RandomForestClassifier(
    n_estimators=300,
    min_samples_leaf=20,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)

# Compare cross-validation folds
fold_values = [3, 5, 10]
results = []

for folds in fold_values:
    cv = StratifiedKFold(
        n_splits=folds,
        shuffle=True,
        random_state=42
    )

    scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="roc_auc",
        n_jobs=-1
    )

    results.append({
        "folds": folds,
        "roc_auc_mean": scores.mean(),
        "roc_auc_std": scores.std()
    })

# Save results
results_df = pd.DataFrame(results)

results_df.to_csv(
    "outputs/cross_validation_results.csv",
    index=False
)

print("\nExperiment 9 - Cross Validation Comparison")
print(results_df.to_string(index=False))
print("\nResults saved successfully!")
