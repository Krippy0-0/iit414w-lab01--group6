# PROMPTS.md — Final Report Writing Phase

Team: Carlos Orellana and Mattias Morales, Group 6

## Interaction 1 — Rubric Coverage Review

**Context:** Before final editing, we had the team-written source material from Hito 1 and Hito 2: `hito1/framing.md`, `hito2/baseline_comparison.md`, `hito2/error_analysis.md`, `hito2/whatif_comparison.md`, `hito2/leakage_audit.md`, `hito2/mitigations.md`, and the draft final report.

**Prompts:** Asked AI to review the draft against the Final Report rubric and identify missing or weak requirements, especially the nine-section order, both-target coverage, the honesty sentence, calibration evidence, and the what-if disagreement.

**Output:** The review flagged that the report needed to make the calibration evidence easier to find, keep the what-if scenario explicitly observational, and make the reproducibility note point to the README and prompt logs.

**Validation:** We checked the recommendations manually against the assignment checklist and the existing Hito 1/Hito 2 artifacts. We verified that the metrics, split, targets, and what-if probabilities matched the notebooks and markdown files already in the repository.

**Adaptations:** The team kept the report structure and evidence from the Hito submissions, added clearer references to calibration figures, and revised wording that could be read as causal.

**Final Decision:** Use AI feedback only as a checklist-style review aid. The final report remains based on the team's Hito 1 framing, Hito 2 metrics, error analysis, and what-if comparison.

## Interaction 2 — Observational Wording Check

**Context:** The rubric requires what-if comparisons to be framed as observational rather than causal, because the model estimates historical associations under proposed scenario inputs.

**Prompts:** Asked AI to identify any phrases in the what-if and limitations sections that could sound like causal claims.

**Output:** The review identified language such as "strategy increases probability" as potentially too causal if not qualified.

**Validation:** We compared the wording with `hito2/leakage_audit.md`, which states that strategy choices correlate with car pace, driver, traffic, safety-car timing, and weather.

**Adaptations:** We kept the quantitative comparison but described it as a model-estimated association. The report now states that the delta is a decision prompt, not proof of the causal effect of switching strategies.

**Final Decision:** Keep observational language throughout Sections 3, 6, and 7.

## Interaction 3 — Failure-Mode Structure Review

**Context:** Section 6 requires three concrete failure-mode hypotheses with a where / why / how-to-test structure. The raw evidence came from `hito2/error_analysis.md`.

**Prompts:** Asked AI to review whether the three failure modes were specific enough and whether each one included evidence, F1-domain reasoning, and a testable follow-up.

**Output:** The review suggested keeping the three failure modes tied to strategy type, circuit group, and constructor tier, because those slices already appeared in Hito 2.

**Validation:** We checked that each failure mode used actual slice metrics from Hito 2: `three_plus_stop` error, hybrid-circuit `is_top10` error, and front-team `is_top5` overestimation.

**Adaptations:** We revised generic modeling explanations into operational F1 explanations: incident-driven pit stops, coarse circuit grouping, and front-team objective context.

**Final Decision:** Keep the three failure modes as team-authored interpretations of the Hito 2 slice tables.

## Interaction 4 — Reproducibility Audit

**Context:** Before submission, we checked the repository state, README runbook, report figures, and tag/commit consistency.

**Prompts:** Asked AI to help audit the repository for reproducibility risks and compare the final report against the required submission checklist.

**Output:** The audit flagged that the root README needed a fuller runbook, the report should embed the available calibration figures, and the title-page commit needed to match the pushed `final-v1` tag.

**Validation:** We used `git status`, `git rev-parse --short HEAD`, `git rev-parse --short final-v1`, artifact listing, and direct inspection of `README.md`, `final_report/IIT414W_FinalReport_Group6.md`, and this file.

**Adaptations:** The README was expanded with a fresh-clone runbook, `environment.yml` was added for Python 3.11 reproducibility, and the final report now embeds both calibration plots from `demo_day/`.

**Final Decision:** Keep the repository reproducibility notes explicit and ensure the submitted PDF title page uses the same short hash as the pushed `final-v1` tag.

## Rejected or Corrected AI Suggestion

**Context:** During wording review, one suggestion was to phrase the what-if result as a direct strategy effect because it reads more simply.

**Prompts:** We checked this suggestion against the honesty requirement in the rubric and against the Hito 2 leakage audit.

**Output:** The suggested phrasing was rejected because the model is not causal.

**Validation:** The assignment explicitly requires what-if comparisons to be observational, and `hito2/leakage_audit.md` documents strategy confounding.

**Adaptations:** We used wording such as "the model estimates higher historical association" and "decision prompt" instead of causal language.

**Final Decision:** Do not present scenario deltas as causal effects.
