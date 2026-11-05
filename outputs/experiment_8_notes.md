

\# Experiment 8 – Max Features Tuning



\## Objective

To compare different max\_features settings in Random Forest.



\## Fixed Parameters

\- n\_estimators = 300

\- min\_samples\_leaf = 20



\## Configurations Tested

\- sqrt

\- log2

\- None



\## Results

\- sqrt and log2 achieved identical ROC-AUC and F1-score.

\- None achieved a slightly lower Brier score.

\- sqrt and log2 achieved better cross-validation ROC-AUC.



\## Conclusion

sqrt and log2 performed identically in this experiment.

The sqrt configuration is retained for further experiments.



\## Output

outputs/max\_features\_results.csv



