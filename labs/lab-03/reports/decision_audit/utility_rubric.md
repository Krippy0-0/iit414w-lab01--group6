# Utility Rubric - Live Strategy Calls

**Audit scope:** live race strategy calls.  
**Notebook source:** `lab3_model_comparison.ipynb`, section `Decision Audit Metrics`.

| # | Criterion | Decision test | Notebook evidence | Required level | Score | Rating |
|---|---|---|---|---|---|---|
| 1 | Decision Relevance | Can this support a live strategy call during the race? | Live-race input count = 0; live refresh count = 0; owner role named for live calls = 0 | Live-race input count >= 1, live refresh count >= 1, owner role = 1 | 0/2 | Red |
| 2 | Baseline Lift | Does it beat the strongest simple option? | Random Forest test MAE = 2.838; grid heuristic test MAE = 3.246; lift = 12.57% | Green >= 10%; Yellow 2% to 10%; Red < 2% | 2/2 | Green |
| 3 | Operating-Point Fit | At the live-call action point, are the hit and miss rates good enough? | Predicted points >= 10: precision = 0.776; recall = 0.651; support = 229; false positives = 43; false negatives = 80 | Precision >= 0.850 and recall >= 0.700 | 0/2 | Red |
| 4 | Failure-Cost Asymmetry | Are errors cheaper than the decisions they would trigger? | False positive cost weight = 2.0; false negative cost weight = 1.0; weighted false positive cost = 86.0; weighted false negative cost = 80.0 | Weighted false positive cost <= weighted false negative cost | 0/2 | Red |
| 5 | Deployment Friction | Can the input and owner loop exist during the race? | Live-race input count = 0; live refresh count = 0; owner role named for live calls = 0 | Inputs ready before the call window and owner role = 1 | 0/2 | Red |

## Result

Total score: 2/10. The model has real baseline lift for pre-race point estimates, but the live-call audit has 4 Red criteria out of 5. The blocking facts are numeric: 0 live inputs, 0 live refreshes, 0 named live owner, operating-point precision 0.776 below 0.850, operating-point recall 0.651 below 0.700, and weighted false-positive cost 86.0 above weighted false-negative cost 80.0.
