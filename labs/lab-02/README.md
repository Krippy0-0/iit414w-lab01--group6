# Lab 2 — Feature Engineering + Improved Baseline

**Team:** Carlos Orellana & Mattias Morales (Group 6)  
**Course:** IIT414W — Artificial Intelligence Workshop  
**Date:** March 2026

## Deliverables in This Folder

- `lab02_feature_engineering.ipynb` — main notebook (data fetch, feature engineering, model, evaluation, leakage checks, error analysis)
- `comparison_table.md` — Lab 1 vs Lab 2 metrics side-by-side
- `PROMPTS.md` — AI usage documentation in 6-field format
- `lab02_metrics_table.csv` — metrics exported directly from notebook execution for consistency checks

## Reproducibility (Runbook)

### Prerequisites
- Python 3.9+ (we used 3.13)
- `pip`
- Internet connection (Jolpica API is queried live)

### Steps
1. From repo root, create/activate environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the notebook:
   ```bash
   jupyter notebook labs/lab_02/lab02_feature_engineering.ipynb
   ```
   Then use **Kernel → Restart & Run All**.

Expected runtime is typically under 10 minutes depending on API/network latency.

## Fixed Settings (Non-Negotiables)

- `RANDOM_SEED = 414` is used in stochastic components (`DummyClassifier`, `LogisticRegression`).
- Temporal split is identical to Lab 1:
  - Train: 2022–2023 full seasons
  - Validation: 2024 rounds 1–12
  - Test (sealed): 2024 rounds 13+
- Primary metric remains **F1 (Top-10 class)** as justified in Lab 1.

## Engineered Features Added

1. `prev_finish_pos` (lag feature)
2. `avg_finish_pos_last3_prior` (rolling aggregate)
3. `driver_circuit_top10_rate_prior` (interaction + historical rate)
4. `constructor_tier_prev_season` (categorical encoding from previous-season constructor performance)

All feature calculations are designed to use pre-race information only.

## Validation + Leakage Controls

The notebook includes:
- temporal non-overlap assertions (`train < val < test` by date)
- race-key overlap assertions
- shift-based historical features (`shift(1)`) to avoid using current-race outcomes
- train-only imputation/encoding fit before validation transforms
- explicit statement that test split is not used for selection/tuning
- 10-item leakage checklist with PASS evidence

## Notes on Results

The Lab 2 model beats majority and prior-period baselines but does not beat the Lab 1 domain heuristic baseline. This is reported honestly and followed by concrete next-step feature ideas in the notebook error analysis section.
