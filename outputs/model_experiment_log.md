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



