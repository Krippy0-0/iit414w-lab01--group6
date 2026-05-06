# Hito 1 - F1 Race Strategy Advisor

Group 6 repository for Module 5, Unit IV Capstone Hito 1: Problem Framing + Baseline.

## Required Files

- `framing.md`: decision framing, metric rationale, limitations, what-if plan, Hito 2 experiments, and workflow.
- `hito1_baseline.ipynb`: executable notebook for the locked split and baseline evaluation.
- `PROMPTS.md`: documented AI interactions using the required 6-field standard.
- `data/f1_strategy_race_level.csv`: official race-level capstone dataset used by the notebook.
- `data/f1_strategy_lap_level.csv`: optional lap-level capstone dataset included for Hito 2 extension.
- `scripts/build_hito1_assets.py`: helper script that copies the official capstone CSVs from `excel_capstone/` and regenerates the notebook.

## Install

Use Python 3.10+.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run

Open and run all cells:

```bash
jupyter notebook hito1_baseline.ipynb
```

Or verify from the command line:

```bash
jupyter nbconvert --to notebook --execute hito1_baseline.ipynb --output hito1_baseline.executed.ipynb
```

If Windows blocks Jupyter secure connection-file permissions in a classroom machine, run:

```bash
$env:JUPYTER_ALLOW_INSECURE_WRITES='1'
jupyter nbconvert --to notebook --execute hito1_baseline.ipynb --output hito1_baseline.executed.ipynb
```

That environment variable is only a local execution workaround; it is not required by the notebook logic.

## Data Provenance

The package uses the official capstone files provided in `excel_capstone/`:

- `f1_strategy_race_level.csv`
- `f1_strategy_lap_level.csv` as optional supporting data

The notebook treats strategy fields such as `n_stops`, `compound_sequence`, and stint-life summaries as scenario inputs for what-if comparison. They are not presented as pre-race signals.

## Locked Split and Target

- Target: `is_top10`
- Train: 2019-2021
- Calibration: 2022
- Test: 2023-2024

## Current Baseline Result

Executed test-set metrics:

| Model | Brier | Log loss | ROC-AUC |
|---|---:|---:|---:|
| Grid-rule heuristic | 0.160 | 0.495 | 0.839 |
| Calibrated GB strategy baseline | 0.125 | 0.426 | 0.902 |

The calibrated model beats both the grid-rule floor and the docent reference model of Brier 0.132 and ROC-AUC 0.892.
