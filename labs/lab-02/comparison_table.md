# Lab 1 vs Lab 2 — Comparison Table
## Carlos Orellana & Mattias Morales

| Model / Baseline | Accuracy | Precision | Recall | F1 | ROC-AUC |
|------------------------|----------|-----------|--------|-------|---------|
| Majority class (Lab 1) | 0.4979 | 0.0000 | 0.0000 | 0.0000 | 0.5000 |
| Domain heuristic (Lab 1) | 0.8577 | 0.8583 | 0.8583 | 0.8583 | 0.8577 |
| Prior-period baseline | 0.7782 | 0.8190 | 0.7167 | 0.7644 | 0.7785 |
| Lab 2 model (LogReg) | 0.8243 | 0.8362 | 0.8083 | 0.8220 | 0.8932 |

## Primary metric: F1 (Top-10 class) (justified in Lab 1)

## Interpretation (3–5 sentences)
Our Lab 2 Logistic Regression improved clearly over the majority-class baseline (+0.8220 F1) and also beat the prior-period baseline (+0.0576 F1). However, it did **not** beat the Lab 1 domain heuristic: the model scored 0.8220 F1 vs. 0.8583 for the heuristic (gap = -0.0363). The hardest baseline to beat was the grid-based heuristic, which remains extremely strong for this target because starting position already captures much of top-10 probability. Error analysis shows most misses come from race-day volatility (retirements/incidents from strong grid starts) and deep-grid chargers, suggesting next features should focus on pre-race reliability and stronger pace proxies.
