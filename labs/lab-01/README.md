# Lab 1 — Predicting Top-10 F1 Finishes (EDA & Baseline)

**Team:** Carlos Orellana & Mattias Morales (Group 6)
**Course:** IIT414W — Artificial Intelligence Workshop
**Date:** March 2026

---

## Overview

This repo contains our exploratory data analysis and baseline model for predicting whether a Formula 1 driver finishes in the top 10 of a race, using data from the 2022–2024 seasons.

## Repository Structure

```
├── eda.ipynb              # Decision-oriented EDA notebook
├── baseline.ipynb         # Domain heuristic baseline + stretch metrics
├── DATA_QUALITY_LOG.md    # Log of data quality issues and decisions
├── PROMPTS.md             # AI usage documentation
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── .gitignore             # Excludes cache, checkpoints, etc.
```

## How to Reproduce (Runbook)

### Prerequisites
- Python 3.9+ (we used 3.13)
- pip
- Internet connection (notebooks fetch data from the Jolpica API)

### Steps

1. **Clone the repo:**
   ```bash
   git clone https://github.com/Krippy0-0/iit414w-lab01--group6-.git
   cd iit414w-lab01--group6-
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the EDA notebook:**
   ```bash
   jupyter notebook eda.ipynb
   ```
   Then do **Kernel → Restart & Run All**.

5. **Run the Baseline notebook:**
   ```bash
   jupyter notebook baseline.ipynb
   ```
   Then do **Kernel → Restart & Run All**.

Both notebooks fetch data directly from the Jolpica API on each run. No local CSV files are needed. Each notebook should complete in under 5 minutes (most of the time is API calls with sleep delays to be polite to the server).

### Notes
- Both notebooks use `RANDOM_SEED = 414` for reproducibility.
- Data is fetched live from `https://api.jolpi.ca/ergast/f1/` — make sure you have internet access.
- The API has a 100-row response limit, so the ingestion function paginates automatically.
- We add `time.sleep(1)` between API calls to avoid rate limiting.

## Temporal Split

| Set        | Data                    |
|------------|-------------------------|
| Training   | 2022 + 2023 full seasons |
| Validation | 2024 rounds 1–12        |
| Test       | 2024 rounds 13+         |

The test set is **not used** in either notebook. It's defined but held out for future evaluation in Lab 2.

## Key Finding (1-3-1)

**Grid position is the best pre-race predictor for top-10 finishes — use it as the primary feature.**

1. Drivers starting P1–P10 finish in the top 10 roughly 70–80% of the time across all three seasons.
2. The Spearman correlation between grid position and top-10 finish is the strongest among all pre-race features, and this holds stable across seasons.
3. A simple "grid ≤ 10 → predict top 10" heuristic achieves ~86% accuracy on the validation set, well above the 50% random baseline.

**Action:** Any ML model from Lab 2 must beat 86% accuracy. If it can't outperform this one-variable rule, it adds no value.

## Team Members

- **Carlos Orellana**
- **Mattias Morales**
