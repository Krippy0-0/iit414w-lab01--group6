# AI Usage Documentation — Lab 2

**Team:** Carlos Orellana & Mattias Morales (Group 6)

---

## Entry 1 — Notebook structure and implementation planning

**Context:** We needed to convert the Lab 2 rubric into an executable notebook structure that includes data ingestion, feature engineering, leakage checks, temporal validation, baseline comparison, and error analysis.

**Prompt:** "Create an end-to-end implementation plan for Lab 2 using the same temporal split/metric as Lab 1, with at least 3 leakage-safe engineered features and one simple sklearn model."

**Output:** The AI proposed a concrete section-by-section notebook plan with required artifacts, model constraints, and consistency checks.

**Validation:** We compared the plan against the assignment requirements and confirmed all mandatory constraints were represented (seed, split, metric continuity, baseline rows, leakage checklist, error analysis).

**Adaptations:** We expanded the plan to include 4 engineered features (not just 3) to strengthen rubric coverage and added an explicit prior-period baseline row.

**Final Decision:** Used as implementation blueprint.

---

## Entry 2 — Leakage-safe feature design

**Context:** We needed feature formulas that preserve temporal causality and avoid using current-race outcomes.

**Prompt:** "Design F1 domain features that are pre-race only and satisfy lag/rolling/interaction/encoding feature type requirements."

**Output:** The AI suggested lag (`shift(1)`), rolling prior average, interaction historical rates, and previous-season categorical tiering.

**Validation:** We audited each feature against the 10-item leakage checklist and ensured every historical component excluded the current row.

**Adaptations:** We implemented historical finish features with a bounded fallback (`position_for_history = position.fillna(20)`) and used previous-season constructor rates to define `top/mid/back` tiers.

**Final Decision:** Used with adaptations.

---

## Entry 3 — Comparison and interpretation drafting

**Context:** After running the notebook, we needed concise and honest interpretation text for `comparison_table.md`.

**Prompt:** "Draft a 3–5 sentence interpretation that explicitly states whether the Lab 2 model beats each baseline and what to try next if it does not beat the heuristic."

**Output:** The AI produced a neutral interpretation template emphasizing fair comparison, strongest baseline identification, and concrete next-step feature ideas.

**Validation:** We replaced placeholders with actual computed metric values from the executed notebook and checked consistency against `lab02_metrics_table.csv`.

**Adaptations:** We tailored the final text to our exact results (LogReg beats majority/prior-period but not heuristic) and linked failure modes to specific next features.

**Final Decision:** Used after metric substitution and edits for clarity.
