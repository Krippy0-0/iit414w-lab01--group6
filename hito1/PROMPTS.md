# PROMPTS.md - Hito 1 AI Use

Team: Carlos Orellana and Mattias Morales, Group 6

## Interaction 1 - Turning the Rubric into a Work Plan

**Context:** We needed to complete Hito 1 using the entire local workspace, previous labs, and the locked course decisions: target `is_top10`, train 2019-2021, calibration 2022, test 2023-2024.

**Prompts:** "Necesito que completes este trabajo (hito 1), considerando todo el workspace, trabajos previos, labs, etc. Creo que es necesario que crees el repo de git... aquí la URL del repo de mi grupo..."

**Output:** The AI inspected the workspace, found the existing group repo at `Labs/iit414w-lab01--group6`, verified that it already points to the GitHub URL, and initially identified that `f1_strategy_race_level.csv` was missing from the searched folders.

**Validation:** We checked local files with `rg --files`, `git remote -v`, and pandas column inspection. The repository remote matched the provided URL, and the needed source files existed locally.

**Adaptations:** Instead of creating a new repo in the workspace root, we used the existing Git repository to avoid duplicating history or submitting the wrong folder. After the `excel_capstone/` folder was identified, the package was rebuilt using the official capstone CSVs.

**Final Decision:** Use the existing group repository and create the Hito 1 package there.

## Interaction 2 - Official Dataset and Leakage Framing

**Context:** The assignment requires `f1_strategy_race_level.csv`, and the user clarified that the required capstone CSVs were in `excel_capstone/`.

**Prompts:** "In the folder `excel_capstone` are the files needed for Hito 1. Complete Hito 1 and upload it to the repo."

**Output:** The review confirmed that `excel_capstone/f1_strategy_race_level.csv` and `excel_capstone/f1_strategy_lap_level.csv` were the official capstone files. It also identified which columns should be treated as outcome/audit fields rather than normal predictors.

**Validation:** The official race-level CSV has 2,447 driver-race rows across 2019-2024, includes the locked target, and preserves the exact temporal split. The notebook asserts split membership and confirms outcome/audit columns are not used as model features.

**Adaptations:** We rejected treating `n_stops`, `strategy_type`, `compound_sequence`, and stint features as normal pre-race facts. They are documented and used only as scenario inputs for what-if comparisons.

**Final Decision:** Use the official dataset plus the script that copies it from `excel_capstone/`, so the data provenance is visible.

## Interaction 3 - Notebook Execution Failure and Fix

**Context:** The notebook needed to run end-to-end from a clean clone using the official race-level CSV.

**Prompts:** "Run the notebook end-to-end and fix any execution issue so Run All works from a clean clone."

**Output:** The AI ran `nbconvert`. A Windows Jupyter permission issue appeared when writing secure connection files, so verification used `JUPYTER_ALLOW_INSECURE_WRITES=1` as a local workaround. The notebook then ran successfully with a sequential `GradientBoostingClassifier`.

**Validation:** The executed notebook reported Brier 0.125, log loss 0.426, and ROC-AUC 0.902 on the locked 2023-2024 test block.

**Adaptations:** We kept `GradientBoostingClassifier` because it is simple, sklearn-native, and robust in the classroom Windows environment.

**Final Decision:** Keep the more robust sequential model for Hito 1 rather than a slightly more complex model that may fail in the classroom environment.

## Interaction 4 - Honest Comparison Against the Docent Baseline

**Context:** The rubric says teams should match or beat the docent model with Brier 0.132 and ROC-AUC 0.892, or honestly explain why they did not.

**Prompts:** "Draft the baseline reflection so it reports the result honestly against the docent reference."

**Output:** The AI proposed saying the model beats both the grid-rule floor and the docent baseline, while still warning that Hito 1 is not deployment-ready.

**Validation:** Executed notebook metrics show Brier 0.125 vs docent 0.132 and ROC-AUC 0.902 vs docent 0.892.

**Adaptations:** We explicitly included the phrase that this is promising but not deployment-ready, and tied the next step to calibration and scenario robustness experiments in Hito 2.

**Final Decision:** Use honest wording in `framing.md` and avoid claiming that the advisor is ready for live strategy calls.

## Interaction 5 - Final Hito 1 Rubric Review

**Context:** Before submission, we reviewed the complete Hito 1 package against the assignment statement: required files, locked temporal split, leakage audit, baseline metrics, what-if plan, limitations, README, and prompt log.

**Prompts:** "Revisa todo el hito 1, aqui esta mi enunciado:" followed by the full Hito 1 assignment text.

**Output:** The AI confirmed the required Hito 1 files were present under `hito1/`, executed the notebook with `python -m nbconvert`, and identified one rubric risk: `qualifying_position` was included as a model feature even though the assignment says it is a stand-in for `grid_position`.

**Validation:** The notebook was re-run after removing `qualifying_position` from the feature list. It still passed end-to-end and reported Brier 0.125, log loss 0.426, and ROC-AUC 0.902 on the locked 2023-2024 test set.

**Adaptations:** We kept `grid_position` as the position signal, moved `qualifying_position` into the audit/not-used group, updated `framing.md` to state that qualifying fields are not treated as separate predictive signals, and made the notebook data path work from either the repo root or `hito1/`.

**Final Decision:** Submit the package with the safer leakage audit and qualifying-field language, while keeping the same calibrated baseline result.
