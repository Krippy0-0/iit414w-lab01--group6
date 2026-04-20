# Lab 3 - Model Comparison Table
**Team:** Carlos Orellana & Mattias Morales (Group 6)

**Primary metric:** MAE (points) - lower is better  
**Temporal split:** Train <= 2022 | Test 2023-2024  
**Framing:** Regression - predicting points scored per driver per race  

| Model | Features | Validation | Train MAE | Test MAE | Gap | WHY |
|---|---|---|---|---|---|---|
| Predict mean | — | 2023–2024 | 5.905 | 5.923 | 0.018 | Trivial upper bound: predicts ~5 pts for everyone, ignores all features |
| Predict median | — | 2023–2024 | 5.092 | 5.129 | 0.037 | Predicts 0 for all (median=0 due to ~50% zero-point rate); better than mean by exploiting zero-inflation |
| Grid heuristic (domain) | grid only | 2023–2024 | 3.341 | 3.246 | -0.096 | Strong because it directly encodes the empirical grid→points distribution from training data |
| Ridge (alpha=1.0) | 5 numeric + circuit + constructor | 2023–2024 | 3.35 | 3.299 | -0.051 | Linear model misses nonlinear grid→points curve; near-zero gap shows underfitting, not overfitting |
| Random Forest | 5 numeric + circuit + constructor | 2023–2024 | 2.482 | 2.838 | 0.356 | Trees capture nonlinear top-3 points premium; moderate overfitting (12.5% gap) on ~2000 training rows |
| Gradient Boosting | 5 numeric + circuit + constructor | 2023–2024 | 2.722 | 2.915 | 0.192 | Sequential residual correction; shallow trees + low lr reduce overfitting vs RF on small dataset |

**Sample sizes:** 2,022 training rows (seasons 2018–2022) · 908 test rows (seasons 2023–2024). All models evaluated on the same test set with identical feature preprocessing within the tree-based vs. linear families.

**Note on Ridge gap:** Ridge test MAE (3.299) < Ridge train MAE (3.350), producing a negative Gap (−0.051). This is underfitting, not test-set leakage — the assertion block in the notebook confirms zero temporal overlap between train and test season ranges.