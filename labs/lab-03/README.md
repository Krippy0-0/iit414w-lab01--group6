# Lab 3 — Model Comparison + Technical Memo

**Team:** Carlos Orellana & Mattias Morales (Group 6)  
**Course:** IIT414W — Artificial Intelligence Workshop  
**Due:** Monday April 20, 2026 at 13:50

---

## What This Lab Does

Compares 6 models (2 statistical baselines + 1 domain heuristic + Ridge + Random Forest + Gradient Boosting) for predicting F1 driver points per race using regression (MAE). Framing changed from Labs 1–2 (binary classification) to regression — see `framing_decision.md` for full justification.

---

## Files

```
labs/lab3/
├── framing_decision.md            # Framing choice + justification (graded C2)
├── model_exploration.md           # W5 Mon in-class checkpoint artifact
├── lab3_model_comparison.ipynb    # Main notebook — run this
├── comparison_table.md            # Standalone comparison table
├── memo.md                        # 1-page technical memo (non-technical audience)
├── PROMPTS.md                     # AI documentation
└── README.md                      # This file
```

---

## How to Reproduce

### Prerequisites

- Python 3.9+
- pip
- Internet connection (Jolpica API is queried on first run; a local CSV cache is created)

### Steps

1. Clone the repo and navigate to the lab:
   ```bash
   git clone https://github.com/Krippy0-0/iit414w-lab01--group6.git
   cd iit414w-lab01--group6/labs/lab3
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install numpy pandas scikit-learn matplotlib requests jupyter
   ```

4. Run the notebook:
   ```bash
   jupyter notebook lab3_model_comparison.ipynb
   ```
   Then: **Kernel → Restart & Run All**

5. Expected runtime: **< 10 minutes** (API fetches 2018–2024 seasons on first run; subsequent runs use the local CSV cache `jolpica_results_2018_2024.csv`).

---

## Fixed Settings (Non-Negotiables)

- `RANDOM_SEED = 414` in every `random_state=` argument
- **Temporal split:** Train seasons ≤ 2022 | Test seasons 2023–2024
- **No random splits.** Walk-forward / season-based holdout only.
- **Primary metric:** MAE (Mean Absolute Error, in points) — consistent across all rows in comparison table

---

## Key Results (after running notebook)

| Model | Test MAE |
|---|---|
| Predict mean (baseline) | ~5.9 |
| Predict median (baseline) | ~5.1 |
| Grid heuristic (domain) | ~3.2 |
| Ridge (alpha=1.0) | ~3.3 |
| Random Forest | ~2.8 |
| Gradient Boosting | ~2.9 |

Random Forest is the best model (test MAE = 2.838), outperforming Gradient Boosting (2.915) and the grid heuristic (3.246). See `comparison_table.md` for exact values with the WHY column.
