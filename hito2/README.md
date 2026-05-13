# Hito 2 - Midpoint Model + Error Analysis

Group 6 package for the F1 Race Strategy Advisor.

## Targets

- Original Hito 1 target: `is_top10`
- Expansion target: `is_top5`

`is_top5` was selected because it reveals whether a strategy only protects points probability or also improves the chance of a strong points finish.

## Required Artifacts

- `hito2_modeling.ipynb`
- `baseline_comparison.md`
- `error_analysis.md`
- `whatif_comparison.md`
- `leakage_audit.md`
- `mitigations.md`
- `PROMPTS.md`

Extra workshop artifacts included: `pitch_skeleton.md` and `final_report_template.md`.

## Reproduce

From the repository root:

```bash
python -m pip install -r hito1/requirements.txt
python hito2/scripts/build_hito2_assets.py
python -m nbconvert --to notebook --execute hito2/hito2_modeling.ipynb --output hito2_modeling.executed.ipynb
```

On Windows classroom machines that block Jupyter connection-file permissions, run this before the `nbconvert` command:

```powershell
$env:JUPYTER_ALLOW_INSECURE_WRITES='1'
```

The notebook uses the same official race-level dataset from Hito 1 and the locked temporal split: train 2019-2021, calibration 2022, test 2023-2024.
