

\# Experiment 11 – Random Seed Validation



\## Objective

To evaluate model performance across different random seeds.



\## Model Configuration

\- n\_estimators = 300

\- min\_samples\_leaf = 20

\- max\_features = sqrt



\## Random Seeds Tested

21, 42, 52, 62, 72



\## Average Results

\- ROC-AUC: 0.649327

\- F1-score: 0.661793

\- Brier score: 0.233008



\## Conclusion

Model performance varied across random seeds.

Seed 72 achieved the highest ROC-AUC and F1-score

and the lowest Brier score.



Further validation is required.



\## Output

outputs/random\_seed\_results.csv



