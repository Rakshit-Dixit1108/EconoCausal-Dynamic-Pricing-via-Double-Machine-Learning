# EconoCausal: Dynamic Pricing via Double Machine Learning

## Project Overview
This project aims to estimate the causal impact of different discount levels on customer purchasing behaviour using Double Machine Learning (DML).

## Dataset
- 5,000 customer records
- 16 columns
- Treatment: Discount percentage (0%, 5%, 10%, 20%)
- Outcome: Purchase status (0 or 1)

## My Contribution – Causal ML Engine
- Implemented a multi-level DML model using EconML.
- Used Random Forest models.
- Evaluated outcome-model performance.
- Analyzed discount distribution.
- Performed propensity score overlap analysis.
- Generated treatment-effect estimates.

## Technologies Used
- Python
- Pandas
- Scikit-learn
- EconML
- NumPy

## Project Structure
- `data/` – Dataset
- `causal_engine/` – DML implementation
- `model_evaluation/` – Model evaluation
- `treatment_analysis/` – Discount distribution analysis
- `propensity_analysis/` – Propensity score analysis
- `results/` – Generated output files

## Expected Outcome
Estimate how different discount levels influence customer purchase probability and support data-driven pricing decisions.
