# Hito 2 PROMPTS

## Interaction 1

Context: Hito 2 required extending the Hito 1 `is_top10` pipeline to a second fixed-list target and producing model comparison, error analysis, what-if, leakage, and mitigation artifacts.

Prompts: Asked AI to inspect the Hito 2 assignment and the Hito 1 package, choose an expansion target, and begin building the Hito 2 deliverable.

Output: AI recommended `is_top5`, reused the locked split, trained calibrated logistic and gradient boosting models for both targets, and generated the required Markdown reports plus a reproducible notebook.

Validation: Metrics were computed from `hito1/data/f1_strategy_race_level.csv`; the notebook was executed with `nbconvert`; generated reports were checked for both targets and the required slices.

Adaptations: The first environment assumption (`python` alias available) was wrong, so execution switched to `python3` and installed the required Python packages for the local user. The what-if text was adapted because `is_top10` was nearly indifferent while `is_top5` provided the useful recommendation signal.

Final Decision: Keep `is_top5` as the expansion target and present the two-target trade-off as "protect points vs chase top-five result."

## Rejected or Corrected AI Suggestion

Context: The Hito 1 framing had speculated about a possible `will_dnf` expansion target.

Prompts: Asked AI to align the Hito 2 work with the assignment.

Output: The earlier `will_dnf` idea was rejected because it is not in the Hito 2 allowed target list.

Validation: The enunciado explicitly restricts expansion targets to `is_top5`, `is_top3`, `finish_position`, or `points`.

Adaptations: The pipeline uses `is_top5`, which is present in the dataset and supports calibrated probability comparison.

Final Decision: Do not introduce `will_dnf` as a formal target for Hito 2; keep it only as an audit/limitation concept.
