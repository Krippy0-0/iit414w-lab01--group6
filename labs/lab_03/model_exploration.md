# Model Exploration - Carlos Orellana & Mattias Morales
## IIT414W - Lab 3 - Initial exploration - March 30, 2026

## 0. Framing Decision (initial - you can revise for Lab 3 final submission)
- **Business question:** How many championship points will a driver score in the next race?
- **Target:** points (continuous, 0–25 scale) → regression
- **Metric:** MAE — directly interpretable in real points (not squared), so a "3-point error" means something concrete to a team principal
- **Why this framing:** Points determine championship standings, not position. Predicting P5 vs P6 matters differently depending on the season — sometimes one position is 2 points apart, sometimes more. Regression on points captures the actual value at stake for constructors' championship math.
- **Rejected alternative:** Binary top-10 classification (top10 = 1/0). We dropped this because it collapses P1 (25 pts) and P10 (1 pt) into the same label, throwing away almost all the information that matters for championship decisions.

## 1. Models Trained
| Model | Key Hyperparameters | Features Used |
|---|---|---|
| Grid heuristic (baseline) | threshold = grid ≤ 10 | grid only |
| Ridge Regression | alpha=1.0, StandardScaler inside pipeline | grid, position_lag_1, rolling_avg_pos_3, constructor_avg_grid_5, rolling_avg_pts_3, constructor_id (OHE), circuit_id (OHE) |
| Random Forest Regressor | n_estimators=100, max_depth=10, min_samples_leaf=5 | grid, position_lag_1, rolling_avg_pos_3, constructor_avg_grid_5, rolling_avg_pts_3, constructor_id (OHE), circuit_id (OHE) |

## 2. Comparison Table (same metric, same validation)
| Model | Features | Validation | Train MAE | Test MAE | WHY this result |
|---|---|---|---|---|---|
| Predict mean (floor) | none | 2023–2024 | — | 5.923 | Ignores all driver/grid signal — pure noise ceiling |
| Predict median (floor) | none | 2023–2024 | — | 5.129 | Slightly better than mean due to skewed points distribution |
| Grid heuristic (domain rule) | grid | 2023–2024 | — | 3.246 | Strong because grid encodes starting advantage directly |
| Ridge alpha=1.0 | grid + lags + rolling + constructor | 2023–2024 | 3.350 | 3.299 | Linear model can't capture nonlinear grid-to-points step shape; barely beats heuristic |
| **RF n=100, depth=10** | grid + lags + rolling + constructor | 2023–2024 | **2.482** | **2.838** | **Best test MAE — trees learn the P1/P2 points gap naturally; gap shows partial overfitting to 2018–2022** |

## 3. Best Model Justification (3+ sentences)
The Random Forest (n_estimators=100, max_depth=10, min_samples_leaf=5) gives the lowest test MAE of 2.838 — beating the grid heuristic by 0.408 points and Ridge by 0.461 points. The reason it works better than Ridge isn't just model complexity: the grid-to-points relationship is fundamentally nonlinear, and Ridge can't represent that. The gap between P1 (25 pts) and P2 (18 pts) is 7 points, but P9 to P10 is only 1 point — Ridge assigns the same linear coefficient to every grid position step, so it systematically underestimates points at the front and overestimates them in the midfield. Random Forest splits on specific grid thresholds and can learn this step-function behavior from the data directly. The train-test gap (2.482 vs 2.838, ~12.5%) tells us the model is partially memorizing 2018–2022 race patterns rather than fully generalizing, but it still outperforms simpler alternatives on unseen data.

## 4. One Honest Limitation
The model's biggest structural weakness is that it cannot see race-day disruptions. All features describe the past — last race position, rolling averages, constructor grid trend — and none capture safety cars, rain, mechanical failures, or first-lap incidents that completely flip the points order. In 2023–2024 there were races where midfield drivers scored big because of chaos at the front (e.g., multi-car incidents on lap 1); our model would predict near-zero points for them every single time. Until we incorporate weather data or some proxy for race instability, this is a gap that more model complexity cannot close.
