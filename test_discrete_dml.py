
import pandas as pd
from econml.dml import LinearDML
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import StratifiedKFold

DATA_PATH = "data/econocausal_synthetic_customers.csv"

df = pd.read_csv(DATA_PATH)

features = [
    "age",
    "annual_income_inr",
    "past_purchases_12m",
    "days_since_last_purchase",
    "website_visits_30d",
    "email_engagement_score",
    "customer_segment",
    "region",
    "season",
]

X = pd.get_dummies(df[features], drop_first=True, dtype=float)
T = df["discount_percent"].astype(int).to_numpy()
Y = df["purchased"].astype(float).to_numpy()

print("Treatment levels:", sorted(set(T)))
print("Treatment counts:")
print(pd.Series(T).value_counts().sort_index())

model = LinearDML(
    model_y=RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    ),
    model_t=RandomForestClassifier(
        n_estimators=100,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    ),
    discrete_treatment=True,
    cv=StratifiedKFold(
        n_splits=3,
        shuffle=True,
        random_state=42,
    ),
    random_state=42,
)

model.fit(Y, T, X=X)

# Compare 20% discount with 5% discount.
effects = model.effect(X, T0=5, T1=20)
lower, upper = model.ate_interval(
    X,
    T0=5,
    T1=20,
    alpha=0.05
)

print("\n95% Confidence Interval:")
print("Lower:", round(float(lower) * 100, 2), "percentage points")
print("Upper:", round(float(upper) * 100, 2), "percentage points")

print("\nDiscrete-treatment DML test")
print("Customers evaluated:", len(effects))
print("Mean estimated effect:", round(float(effects.mean()), 4))
print(
    "Mean effect in percentage points:",
    round(float(effects.mean() * 100), 2),
)
print("PASS: discrete-treatment model fitted and effects calculated")
