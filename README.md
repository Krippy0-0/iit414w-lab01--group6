# IIT414W Group 6

This repository contains Group 6 coursework and capstone artifacts.

## Final Report / Capstone

Final report source and writing-phase AI log:

- `final_report/IIT414W_FinalReport_Group6.md`
- `final_report/IIT414W_FinalReport_Group6.pdf`
- `final_report/PROMPTS.md`
- `final_report/figures/cal_top10.png`
- `final_report/figures/cal_top5.png`

The submitted repository URL should point to:

```text
https://github.com/Krippy0-0/iit414w-lab01--group6
```

The submitted PDF title page should list the short hash of the `final-v1` tag:

```bash
git rev-parse --short final-v1
```

## Reproducibility Runbook

The full capstone artifacts can be regenerated from a fresh clone in a standard Python 3.11 environment. From the repository root:

```bash
conda env create -f environment.yml
conda activate iit414w-group6
python hito2/scripts/build_hito2_assets.py
python -m nbconvert --to notebook --execute hito2/hito2_modeling.ipynb --output hito2_modeling.executed.ipynb
```

If you are using the course-provided environment instead of the local `environment.yml`, install the small package set from `hito1/requirements.txt` and add `python-pptx` before running the same commands.

On Windows classroom machines that block Jupyter connection-file permissions, run this before the `nbconvert` command:

```powershell
$env:JUPYTER_ALLOW_INSECURE_WRITES='1'
```

Expected outputs:

- Hito 2 markdown artifacts in `hito2/`
- Executed notebook at `hito2/hito2_modeling.executed.ipynb`
- Final report figures at `final_report/figures/cal_top10.png` and `final_report/figures/cal_top5.png`

The scripts use repository-relative paths only. `RANDOM_SEED = 414` is set in every stochastic model component.

## Hito 1

The complete Hito 1 submission package is in [`hito1/`](hito1/):

- `framing.md`
- `hito1_baseline.ipynb`
- `PROMPTS.md`
- `README.md`
- `data/f1_strategy_race_level.csv`
- `data/f1_strategy_lap_level.csv`

Run instructions and baseline results are documented in [`hito1/README.md`](hito1/README.md).

## Hito 2

The complete Hito 2 submission package is in [`hito2/`](hito2/):

- `hito2_modeling.ipynb`
- `baseline_comparison.md`
- `error_analysis.md`
- `whatif_comparison.md`
- `leakage_audit.md`
- `mitigations.md`
- `PROMPTS.md`

Run instructions and the two-target model comparison are documented in [`hito2/README.md`](hito2/README.md).
