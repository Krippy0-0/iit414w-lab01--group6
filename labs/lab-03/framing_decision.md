# Framing Decision — Lab 3
**Team:** Carlos Orellana & Mattias Morales (Group 6)  
**Course:** IIT414W — Artificial Intelligence Workshop

---

## Business Question

A constructor's Head of Strategy needs to estimate, before each race, how many championship points each driver will contribute. The question is: *"How many points will this driver score on Sunday?"* — not just whether they will score at all.

## Target Variable

**Points scored per driver per race** (continuous, range 0–25 under the current scoring system). This is the `points` column in the Jolpica API results table, representing actual race-day points awarded.

## Metric

We use **Mean Absolute Error (MAE)**, measured in points. MAE is appropriate because:

1. It is on the same scale as the target (points), making it directly interpretable to a non-technical audience ("on average, our model is off by X points per driver per race").
2. It treats over- and under-predictions symmetrically, which is correct here — overestimating a backmarker's points is as bad as underestimating a frontrunner's.
3. It is less sensitive to the outlier case of a surprise winner (25 points) than RMSE, which squares large errors and would penalise rare events disproportionately.

## Rejected Alternative — Binary Classification (Top-10 yes/no)

In Labs 1 and 2 we framed this as binary classification (Top-10 finish) using macro F1. We considered continuing that framing but rejected it for Lab 3 for two reasons:

1. **Loss of resolution:** A binary model cannot distinguish between P1 (25 pts) and P10 (1 pt). For constructor championship strategy, that 24-point difference is critical — it determines whether a team fights for the title or consolidates a mid-table position. The binary label collapses this into a single "scored" outcome.
2. **Heuristic ceiling:** Our Lab 2 Logistic Regression (F1 = 0.8220) failed to beat the simple "grid ≤ 10 → top-10" heuristic (F1 = 0.8583). Continuing binary classification in Lab 3 without fundamentally new features would likely produce the same result. Regression over a wider season range (2018–2024) provides a larger training set and a more nuanced target that tree-based models can exploit.
