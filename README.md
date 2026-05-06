# Hito 1 - F1 Race Strategy Advisor

Group 6 repository for Module 5, Unit IV Capstone Hito 1: Problem Framing + Baseline.

## Required Files

- `framing.md`: decision framing, metric rationale, limitations, what-if plan, Hito 2 experiments, and workflow.
- `hito1_baseline.ipynb`: executable notebook for the locked split and baseline evaluation.
- `PROMPTS.md`: documented AI interactions using the required 6-field standard.
- `data/f1_strategy_race_level.csv`: recovered race-level dataset used by the notebook.
- `scripts/build_hito1_assets.py`: reproducible script that rebuilds the CSV and notebook from local course artifacts.

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

The required `f1_strategy_race_level.csv` was not present in the workspace, so this package includes a recovered build from:

- `certamen2_orellana/f1_prerace_features_2019_2024.csv`
- `miniChallenge/md1_pitstops_2019_2024.csv`

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
| Grid-rule heuristic | 0.161 | 0.498 | 0.834 |
| Calibrated GB baseline | 0.134 | 0.440 | 0.887 |

The calibrated model beats the grid-rule floor but does not quite beat the docent reference model of Brier 0.132 and ROC-AUC 0.892.
