

\# Experiment 9 – Cross-Validation Comparison



\## Objective

To compare 3-fold, 5-fold and 10-fold stratified cross-validation.



\## Fixed Model Configuration

\- n\_estimators = 300

\- min\_samples\_leaf = 20

\- max\_features = sqrt



\## Results

\- 3-fold mean ROC-AUC: 0.630983

\- 5-fold mean ROC-AUC: 0.632724

\- 10-fold mean ROC-AUC: 0.633473



\## Conclusion

10-fold achieved the highest mean ROC-AUC.

3-fold showed the lowest fold-to-fold standard deviation.

Further validation is required before selecting a strategy.



\## Output

outputs/cross\_validation\_results.csv



