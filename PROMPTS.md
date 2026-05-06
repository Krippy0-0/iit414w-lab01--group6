# PROMPTS.md - Hito 1 AI Use

Team: Carlos Orellana and Mattias Morales, Group 6

## Interaction 1 - Turning the Rubric into a Work Plan

**Context:** We needed to complete Hito 1 using the entire local workspace, previous labs, and the locked course decisions: target `is_top10`, train 2019-2021, calibration 2022, test 2023-2024.

**Prompts:** "Necesito que completes este trabajo (hito 1), considerando todo el workspace, trabajos previos, labs, etc. Creo que es necesario que crees el repo de git... aquí la URL del repo de mi grupo..."

**Output:** The AI inspected the workspace, found the existing group repo at `Labs/iit414w-lab01--group6`, verified that it already points to the GitHub URL, identified that `f1_strategy_race_level.csv` was missing, and proposed building it from recovered pre-race and pit-stop artifacts.

**Validation:** We checked local files with `rg --files`, `git remote -v`, and pandas column inspection. The repository remote matched the provided URL, and the needed source files existed locally.

**Adaptations:** Instead of creating a new repo in the workspace root, we used the existing Git repository to avoid duplicating history or submitting the wrong folder.

**Final Decision:** Use the existing group repository and create the Hito 1 package there.

## Interaction 2 - Dataset Recovery and Leakage Framing

**Context:** The assignment requires `f1_strategy_race_level.csv`, but the exact CSV was not present in the workspace.

**Prompts:** "Find or reconstruct the Hito 1 dataset from previous labs, Certamen work, and miniChallenge files while preserving the assignment's leakage rules."

**Output:** The AI suggested merging `certamen2_orellana/f1_prerace_features_2019_2024.csv` with `miniChallenge/md1_pitstops_2019_2024.csv` aggregated at driver-race level. It also suggested creating `is_top10`, strategy summaries, and a leakage audit that separates pre-race predictors from scenario inputs and audit columns.

**Validation:** The generated CSV has 2,559 driver-race rows across 2019-2024, includes the locked target, and preserves the exact temporal split. The notebook asserts split membership and confirms outcome/audit columns are not used as model features.

**Adaptations:** We rejected treating `n_stops`, `compound_sequence`, and stint features as normal pre-race features. They are documented and used only as scenario inputs for what-if comparisons.

**Final Decision:** Commit the recovered dataset plus the script that builds it, so the data provenance is visible.

## Interaction 3 - Notebook Execution Failure and Fix

**Context:** The first executable notebook used `HistGradientBoostingClassifier`.

**Prompts:** "Run the notebook end-to-end and fix any execution issue so Run All works from a clean clone."

**Output:** The AI ran `nbconvert`. The first failure was a Windows Jupyter permission issue when writing secure connection files. After enabling insecure writes for verification only, execution reached the model cell but failed because `HistGradientBoostingClassifier` tried to create thread/pipe resources blocked by the environment.

**Validation:** The failure traceback pointed to joblib/threading inside the histogram gradient boosting binning step, not to the dataset or metric code.

**Adaptations:** We replaced the model with `GradientBoostingClassifier`, a simpler sequential sklearn model. The notebook then executed successfully end-to-end with Brier 0.134, log loss 0.440, and ROC-AUC 0.887 on 2023-2024 test data.

**Final Decision:** Keep the more robust sequential model for Hito 1 rather than a slightly more complex model that may fail in the classroom environment.

## Interaction 4 - Honest Comparison Against the Docent Baseline

**Context:** The rubric says teams should match or beat the docent model with Brier 0.132 and ROC-AUC 0.892, or honestly explain why they did not.

**Prompts:** "Draft the baseline reflection so it does not overclaim when the model comes close but does not beat the docent model."

**Output:** The AI proposed saying the model beats the grid-rule floor and nearly matches, but does not beat, the docent baseline.

**Validation:** Executed notebook metrics show Brier 0.134 vs docent 0.132 and ROC-AUC 0.887 vs docent 0.892.

**Adaptations:** We explicitly included the phrase that this is promising but not deployment-ready, and tied the next step to calibration and scenario robustness experiments in Hito 2.

**Final Decision:** Use honest wording in `framing.md` and avoid claiming that the advisor is ready for live strategy calls.
