\# EconoCausal — Model Experiment Log



\## Experiment 1: Baseline Multi-Level DML



\*\*Objective:\*\* Estimate the causal effect of different discount levels on customer purchase probability.



\*\*Dataset:\*\* `data/econocausal\_synthetic\_customers.csv`



\*\*Dataset size:\*\* 5,000 customers



\*\*Treatment:\*\* `discount\_percent` — 0%, 5%, 10%, 20%



\*\*Outcome:\*\* `purchased` — binary outcome (0 or 1)



\*\*Baseline configuration:\*\*

\- Estimator: LinearDML

\- Outcome model: RandomForestRegressor

\- Treatment model: RandomForestClassifier

\- Number of trees: 100

\- Minimum samples per leaf: 10

\- Cross-validation folds: 3

\- Random seed: 42



\## Baseline Results



| Comparison | Estimated effect (percentage points) |

|---|---:|

| 5% vs 0% discount | 0.9004 |

| 10% vs 0% discount | 6.2310 |

| 20% vs 0% discount | 10.0965 |



\## Validation Status



\- Customers analyzed: 5,000

\- Existing automated tests: 11 passed

\- Baseline results recorded for future comparison.



\## Next Experiment



Compare the baseline with a classifier-based outcome model appropriate for the binary purchase outcome. Record configuration, runtime, effect estimates, and validation results before deciding whether the change improves the model.

\## Experiment 2: Classifier-Based Outcome Model



\*\*Changes from baseline\*\*

\- Outcome model changed from RandomForestRegressor to RandomForestClassifier.

\- Treatment model remains RandomForestClassifier.

\- Number of trees increased from 100 to 200.

\- `max\_features="sqrt"` added.

\- `discrete\_outcome=True` enabled.



\*\*Results\*\*



| Comparison | Estimated ATE (percentage points) |

|---|---:|

| 5% vs 0% | 0.953803 |

| 10% vs 0% | 6.272289 |

| 20% vs 0% | 10.287294 |



\*\*Validation\*\*

\- Model completed for 5,000 customers.

\- Automated tests: 11 passed.

\- Runtime for test suite: 25.72 seconds.



\*\*Interpretation\*\*



The estimated effects changed slightly relative to the baseline. This does not establish better predictive accuracy or more reliable causal estimates. Further predictive evaluation and causal robustness checks are needed before selecting the final configuration.

## Experiment 3: Held-Out Predictive Evaluation

**Objective:** Compare baseline and classifier-based outcome models on unseen customer data.

**Dataset:** 5,000 customers

**Data split:**
- Training samples: 4,000 (80%)
- Testing samples: 1,000 (20%)
- Random state: 42
- Stratified split based on purchase outcome.

**Results:**

| Metric | Baseline Regressor | Classifier |
|---|---:|---:|
| Accuracy | 0.617000 | 0.608000 |
| Balanced Accuracy | 0.611228 | 0.600388 |
| Precision | 0.623333 | 0.610493 |
| Recall | 0.704331 | 0.723164 |
| F1-score | 0.661362 | 0.662069 |
| ROC-AUC | 0.650986 | 0.649424 |
| Brier Score | 0.233042 | 0.233186 |

**Interpretation:**

The baseline model performed slightly better in accuracy, balanced accuracy, precision, ROC-AUC, and Brier score. The classifier achieved slightly higher recall and F1-score.

The classifier did not demonstrate consistent overall predictive improvement.

**Output:** `outputs/heldout_predictive_metrics.csv`

**Status:** Evaluation completed successfully.

## Experiment 4: Treatment Distribution Analysis

**Objective:** Analyze customer distribution and purchase rates across discount levels.

**Dataset size:** 5,000 customers

| Discount | Customers | Customer Percentage | Purchase Rate |
|---|---:|---:|---:|
| 0% | 2290 | 45.80% | 50.92% |
| 5% | 913 | 18.26% | 50.38% |
| 10% | 1242 | 24.84% | 55.39% |
| 20% | 555 | 11.10% | 61.44% |

**Observations:**
- The 0% discount group contains the most customers.
- The 20% discount group contains the fewest customers.
- The 20% discount group has the highest observed purchase rate.
- Treatment group sizes are unequal.

**Interpretation:**

The distribution analysis identifies differences in customer counts across treatment levels. Unequal group sizes should be considered during propensity overlap and causal diagnostics. These descriptive purchase rates do not establish causal effects.

**Output:** outputs/treatment_distribution.csv




