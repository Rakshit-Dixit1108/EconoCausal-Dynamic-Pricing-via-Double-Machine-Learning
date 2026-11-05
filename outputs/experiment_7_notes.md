

\# Experiment 7 – Min Samples Leaf Tuning



\## Objective

To study the effect of minimum leaf size on Random Forest performance.



\## Configurations Tested

\- 300 trees, min\_samples\_leaf=5

\- 300 trees, min\_samples\_leaf=10

\- 300 trees, min\_samples\_leaf=20

\- 300 trees, min\_samples\_leaf=30



\## Results

\- Min leaf 20 achieved the highest ROC-AUC (0.645457).

\- Min leaf 30 achieved the highest F1-score (0.661512).

\- Min leaf 20 achieved the lowest Brier score (0.233894).

\- Min leaf 30 achieved the highest CV ROC-AUC mean (0.631269).



\## Conclusion

Different leaf sizes performed differently across metrics.

Min leaf 20 performed best in ROC-AUC and Brier score,

while min leaf 30 performed best in F1-score and

cross-validation ROC-AUC.



Further validation is required.



\## Output

outputs/min\_samples\_leaf\_results.csv



