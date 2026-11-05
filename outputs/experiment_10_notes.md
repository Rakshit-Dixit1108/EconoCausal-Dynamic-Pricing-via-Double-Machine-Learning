

\# Experiment 10 – Combined Model Comparison



\## Objective

To compare selected Random Forest configurations.



\## Configurations

\- Baseline: 200 trees, leaf 10, sqrt

\- Experiment 6: 300 trees, leaf 20, sqrt

\- Experiment 7: 300 trees, leaf 30, sqrt

\- Experiment 8: 300 trees, leaf 20, log2



\## Results

\- Experiment 6 achieved ROC-AUC of 0.645457.

\- Experiment 7 achieved the highest F1-score of 0.661512.

\- Experiment 6 achieved the lowest Brier score of 0.233894.

\- Experiment 6 and Experiment 8 produced identical results.



\## Conclusion

The 300-tree, 20-leaf, sqrt configuration

is selected as a candidate for further validation.



The improvement over baseline is modest.



\## Output

outputs/combined\_model\_comparison.csv



