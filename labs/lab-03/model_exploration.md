# Model Exploration — Carlos Orellana & Mattias Morales
## IIT414W — Lab 3 — Initial Exploration — March 30, 2026

---

## 0. Framing Decision (initial draft)

- **Business question:** How many championship points will this driver score in Sunday's race? A constructor's Head of Strategy needs point estimates — not just a yes/no — to plan championship accumulation race by race.
- **Target:** Points scored per driver per race (continuous, 0–25). Regression target.
- **Metric:** MAE (Mean Absolute Error, in points). Chosen because it is on the same scale as the target and interpretable without ML knowledge: "on average, the model is off by X points."
- **Why this framing:** Regression preserves the distinction between P1 (25 pts) and P10 (1 pt), which matters enormously for constructor championship strategy. Binary classification collapses both into "scored" and loses that resolution.
- **Rejected alternative:** Binary classification (Top-10 yes/no, macro F1) — used in Labs 1–2. Rejected because (a) a binary model loses P1 vs P10 distinction critical to strategy, and (b) our Lab 2 LogReg never beat the simple grid heuristic (F1 gap = −0.036).

---

## 1. Models Trained

| Model | Key Hyperparameters | Features Used |
|---|---|---|
| Predict mean (baseline) | strategy='mean' | none |
| Predict median (baseline) | strategy='median' | none |
| Grid heuristic (domain baseline) | avg points by grid pos (train-only lookup) | grid |
| Ridge Regression | alpha=1.0, StandardScaler | grid, position_lag_1, rolling_avg_pos_3, constructor_avg_grid_5, rolling_avg_pts_3, circuit_id, constructor_id |
| Random Forest | n_estimators=100, max_depth=10, min_samples_leaf=5 | grid, position_lag_1, rolling_avg_pos_3, constructor_avg_grid_5, rolling_avg_pts_3, circuit_id, constructor_id |

---

## 2. Comparison Table (same metric, same temporal split)

Train: seasons 2018–2022 | Test: seasons 2023–2024

| Model | Features | Validation | Train MAE | Test MAE | WHY this result |
|---|---|---|---|---|---|
| Predict mean | — | 2023–2024 | — | 5.923 | Trivial upper bound; ignores all features, predicts ~5 pts for every driver |
| Predict median | — | 2023–2024 | — | 5.129 | Predicts 0 for most drivers due to zero-inflation (~50% score 0 pts); mechanically better than mean |
| Grid heuristic | grid only | 2023–2024 | — | 3.246 | Strong because it directly encodes the grid→points nonlinear mapping learned from training data |
| Ridge (alpha=1.0) | 5 numeric + 2 categorical | 2023–2024 | 3.350 | 3.299 | Linear model misses the nonlinear grid→points curve; multi-feature input adds marginal value over heuristic |
| Random Forest | 5 numeric + 2 categorical | 2023–2024 | 2.482 | 2.838 | Captures nonlinear grid→points threshold; train-test gap (0.356, 12.5%) shows mild overfitting on ~2000 rows |

---

## 3. Best Model Justification

Random Forest (test MAE = 2.838) is the best model, outperforming the grid heuristic by 12.6% (0.408 MAE points). This makes sense mechanistically: the relationship between grid position and points is highly nonlinear — P1 earns 25 points while P5 earns 10 and P10 earns 1. Trees learn this threshold structure naturally without being told, whereas Ridge assumes a constant linear rate per grid position and therefore underestimates the top-3 premium. The rolling points feature (`rolling_avg_pts_3`) adds signal beyond grid alone by capturing current car-driver form. The train-test gap of 0.356 (12.5% of test MAE) is moderate — the model is not wildly overfitting, but with ~2000 training rows and 100 trees, some memorisation of constructor-circuit combinations is expected.

---

## 4. One Honest Limitation

Random Forest's biggest weakness on this dataset is zero-inflation: roughly 50% of race entries score 0 points, and the model often predicts small positive values (0.5–2.0 pts) for midfield drivers who score 0. This inflates MAE for the non-scoring majority. A model that predicted exactly 0 for every driver starting P11–P20 would perform well on MAE for that slice but would be useless for strategy. The current model does not handle the zero-inflation structure explicitly — a two-stage model (first predict whether the driver scores at all, then predict how many) would likely improve MAE further.
