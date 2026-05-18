# Hito 2 PROMPTS

## Interaction 1

Context: Hito 2 required extending the Hito 1 `is_top10` pipeline to a second fixed-list target and producing model comparison, error analysis, what-if, leakage, and mitigation artifacts.

Prompts: Asked AI to review the Hito 2 assignment and the Hito 1 package, then advise whether `is_top5` was a defensible expansion target.

Output: The review supported `is_top5` because it preserves the points-finish framing from Hito 1 while exposing stronger-result upside. It also suggested keeping the locked split and comparing calibrated logistic regression against calibrated gradient boosting for both targets.

Validation: Metrics were computed from `hito1/data/f1_strategy_race_level.csv`; the notebook was executed with `nbconvert`; the team checked the reports for both targets and the required slices.

Adaptations: The first environment assumption (`python` alias available) was wrong, so execution switched to `python3` and installed the required Python packages for the local user. The what-if text was adapted because `is_top10` was nearly indifferent while `is_top5` provided the useful recommendation signal.

Final Decision: Keep `is_top5` as the expansion target and present the two-target trade-off as "protect points vs chase top-five result."

## Interaction 2

Context: The first Hito 2 what-if showed a large `is_top5` change but listed the same raw recommendation for both targets.

Prompts: Asked AI to audit the submitted Hito 2 against the rubric and identify whether the what-if demonstrated a true target disagreement.

Output: AI flagged that `is_top10` and `is_top5` both recommended `two_stop`, which was weaker than the rubric's requested disagreement case.

Validation: The table was checked directly: P(top10) changed by only 0.020 while P(top5) changed by 0.349.

Adaptations: We added a practical threshold for `is_top10`: if the top-ten delta is below 0.03, keep the simpler one-stop because the extra pit stop does not materially improve points probability. The `is_top5` target still recommends the aggressive two-stop.

Final Decision: Present the disagreement as objective-dependent: choose one-stop to protect points probability, choose two-stop to chase top-five upside.

## Interaction 3

Context: Hito 2 also requires error-analysis slicing, calibration/probability-quality validation, and explicit confounding discussion.

Prompts: Asked AI to check whether the reports covered strategy type, circuit type, an additional context, calibration bins, and confounding limitations.

Output: AI confirmed the required slices were present for both targets and suggested making the README and prompts more explicit.

Validation: `error_analysis.md` contains strategy, circuit, constructor-tier, and weather slices for both `is_top10` and `is_top5`; the notebook prints calibration bins for both targets.

Adaptations: We clarified reproducibility commands and added this prompt entry documenting the validation of slicing, calibration, and confounding coverage.

Final Decision: Keep constructor tier as the required additional context and weather as an audit slice because both connect directly to strategy-confounding risk.

## Rejected or Corrected AI Suggestion

Context: The Hito 1 framing had speculated about a possible `will_dnf` expansion target.

Prompts: Asked AI to align the Hito 2 work with the assignment.

Output: The earlier `will_dnf` idea was rejected because it is not in the Hito 2 allowed target list.

Validation: The enunciado explicitly restricts expansion targets to `is_top5`, `is_top3`, `finish_position`, or `points`.

Adaptations: The pipeline uses `is_top5`, which is present in the dataset and supports calibrated probability comparison.

Final Decision: Do not introduce `will_dnf` as a formal target for Hito 2; keep it only as an audit/limitation concept.
