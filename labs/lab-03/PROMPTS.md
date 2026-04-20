# PROMPTS.md — AI Documentation
**Team:** Carlos Orellana & Mattias Morales (Group 6)  
**Lab:** 3 — Model Comparison + Technical Memo  
**Course:** IIT414W — Artificial Intelligence Workshop

---

## Entry 1 — April 2026 — Framing decision: regression vs. binary classification

**Context:** We needed to decide whether to continue with binary classification (Top-10 yes/no, from Labs 1–2) or switch to regression (points scored, MAE). Our Lab 2 LogReg had failed to beat the heuristic (F1 gap = −0.036).

**Prompt:** "We've been doing binary classification for F1 top-10 prediction in Labs 1–2 and never beat the heuristic. For Lab 3 the rubric asks for a justified framing decision. Should we switch to regression (predicting points, MAE) or keep binary classification? What's the strongest business justification for regression in an F1 constructor strategy context?"

**Output:** AI suggested switching to regression and offered the argument that a team principal needs point estimates for championship accumulation — not just yes/no. It suggested using MAE as the metric and flagged that ~50% zero-point entries would create a zero-inflation challenge. It also provided the P1 vs P10 distinction argument (25 pts vs 1 pt lost in binary label).

**Validation:** We cross-checked against the W05 notebook demo results, which showed Random Forest achieving MAE=2.838 vs heuristic MAE=3.246 — confirming that regression with a tree model actually beats the heuristic, unlike our binary classification results. The zero-inflation claim was verified: `(y_train==0).mean()` on the 2018–2022 training set returns ~50%, matching the AI's description.

**Adaptations:** The AI's generic justification was adapted to specifically reference the constructor championship points accumulation use case and the P1 vs P10 point gap. We added the explicit rejection of multiclass (no_points/scoring/podium) in `framing_decision.md` because the rubric requires rejecting at least one alternative, which the AI did not initially include.

**Final Decision:** Used — regression framing adopted. The AI's core argument was sound and supported by the W05 notebook empirical results.

---

## Entry 2 — April 2026 — Model selection: adding Gradient Boosting as third model

**Context:** The rubric requires at least 3 models. We already had Ridge and Random Forest from the W05 notebook demo. We asked the AI for a third model appropriate for this dataset size and target.

**Prompt:** "We have Ridge and Random Forest for F1 points regression (~2000 training rows, 5 numeric features + 2 categorical). What's a good third model to add? We want something that can plausibly beat RF but won't massively overfit on a small dataset."

**Output:** AI suggested Gradient Boosting with `max_depth=4`, `learning_rate=0.05`, `n_estimators=100` as a third option. It explained that the low learning rate and shallow depth reduce overfitting on small datasets. It also mentioned XGBoost and LightGBM but noted they require additional installs.

**Validation:** We used `sklearn.ensemble.GradientBoostingRegressor` (no extra install) with the suggested hyperparameters. We verified train and test MAE both decrease relative to baseline, and that the train-test gap is reported in the comparison table alongside all other models.

**Adaptations:** Used sklearn's built-in GBM instead of XGBoost to keep the environment requirement-free. Kept `random_state=RANDOM_SEED` (414) consistent with course non-negotiables.

**Final Decision:** Used — GradientBoostingRegressor added as third ML model.

---

## Entry 3 — April 2026 — Technical memo audience calibration

**Context:** The rubric's C3 criterion requires a 1-page memo for "the Head of Strategy at a Formula 1 team — understands racing but not machine learning."

**Prompt:** "Write a 1-page technical memo for the Head of Strategy at an F1 team explaining that our points prediction model (Random Forest, test MAE ~2.8 points) is ready for use. Audience: understands F1 but not ML. No jargon. Include what it can and cannot do."

**Output:** AI produced a memo with a section on what MAE means in plain language, a comparison table with the baselines, and a section on limitations. It used the phrase "machine learning model" and "algorithm."

**Validation:** We checked the memo against the rubric requirement: "no jargon, or jargon defined when first used." The AI's draft used "algorithm" and "training data" without definition. We also verified that the 2.8-point figure matched the notebook output before including it.

**Adaptations:** Removed "algorithm" and "training data" references. Replaced with plain-language analogies. Added the "±2.8-point typical error" framing in the recommendation section, which the AI's draft lacked. The comparison table numbers were manually verified against notebook cell outputs.

**Final Decision:** Partially used — structure and framing adopted, but jargon removed and specific numbers updated from notebook outputs.

---

## AI Limitation Specific to This Lab

The AI consistently suggested using the 2022-start dataset (Lab 2's 1359-row set) for all models. This was incorrect — Ridge and Random Forest benefit from larger training sets, and the W05 notebook used 2018–2024 (~2930 rows). We corrected the data loading cell to fetch 2018–2024 and use the TRAIN_END=2022 / TEST_START=2023 boundary, matching the W05 notebook's validated approach. This is a specific instance where the AI anchored to the most recently discussed dataset (Lab 2) rather than considering what would be best for the current task.
