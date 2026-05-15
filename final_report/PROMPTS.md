# PROMPTS.md — Final Report Writing Phase

Team: Carlos Orellana and Mattias Morales, Group 6

## Interaction 1 — Drafting All Nine Sections

**Context:** The Final Report requires nine sections in order, 8–12 pages in English. We had all source material in the repo: `hito1/framing.md`, `hito2/baseline_comparison.md`, `hito2/error_analysis.md`, `hito2/whatif_comparison.md`, `hito2/leakage_audit.md`, `hito2/mitigations.md`, and both PROMPTS.md files.

**Prompts:** "ahora empieza el final report y terminalo. Tienes todo en esta repo."

**Output:** The AI read all source files, identified the rubric requirements from `final_report/enunciado.md`, and generated the complete nine-section report in `final_report/IIT414W_FinalReport_Group6.md`. The report integrated all Hito 1 and Hito 2 material into prose form with tables, added new sections (Executive Summary, improved Problem Framing with explicit assumptions, Limitations with the mandatory honesty sentence), and translated technical metrics into domain-specific language throughout.

**Validation:** We checked that all nine sections were present in order, that both targets were discussed in §4–§6, that the honesty sentence in §7 had three concrete testable conditions, that the what-if comparison demonstrated a genuine target disagreement, and that the calibration discussion covered both targets with specific probability ranges.

**Adaptations:** The AI initially used causal language in the what-if section ("the two-stop strategy increases top-5 probability"). This was corrected to observational framing: "the model estimates higher historical association between a two-stop profile and a top-5 result." The correction reflects the fundamental limit of the scenario-comparison tool — it estimates historical association, not causal effects, and the engineer must understand this distinction before acting on the output.

**Final Decision:** Keep the observational framing throughout §6 and the what-if comparison. Add a note in §6 explicitly flagging that the comparison is observational, not causal.

## Rejected or Corrected AI Suggestion

**Context:** First draft of the what-if recommendation table used the phrase "two-stop strategy causes top-5 probability to quadruple."

**Prompt:** Reviewed the draft against the rubric requirement that "what-if comparisons are framed as observational, not causal."

**Output:** AI initially defended the causal phrasing on the grounds that "it is more readable for a non-technical audience."

**Validation:** The rubric explicitly states (D3 Honestidad criteria): "What-if comparisons are framed as observational, not causal." The AI suggestion would have failed the honesty dimension.

**Adaptations:** The phrasing was changed to: "the model estimates higher historical association between a two-stop profile and a top-5 result" with an explicit footnote in §6 that the comparison is observational.

**Final Decision:** Use observational language throughout. Causal claims are not supported by the data or the modeling approach and would misrepresent the tool's capabilities to an engineer who might act on them.

## Interaction 2 — Framing the Three Failure-Mode Hypotheses

**Context:** The rubric requires three concrete failure-mode hypotheses in §6 with a where / why / how-to-test structure. The error analysis tables were available from `hito2/error_analysis.md`.

**Prompts:** Asked AI to translate the raw slice tables into structured failure-mode hypotheses with the required three-part structure.

**Output:** AI produced three hypotheses: (1) three-plus-stop incident confounding, (2) hybrid circuit feature coarseness, (3) front-team top-5 overestimation in championship battles. Each was structured with a where (specific slice), why (domain reasoning), and how-to-test (concrete empirical test).

**Validation:** The three hypotheses cover strategy type, circuit type, and constructor tier — matching all three required slice dimensions from the rubric.

**Adaptations:** The AI's initial framing of hypothesis 3 attributed the overestimation to "model overfitting." We replaced this with the domain-specific explanation: in close championship battles, front-running constructors sometimes sacrifice top-5 finishing position for strategic reasons, and the model does not capture race-objective context. The domain explanation is more actionable for a strategy engineer.

**Final Decision:** Use the domain-specific explanations for all three failure modes. ML-internal explanations (overfitting, variance) are less useful for a strategy audience than operational F1 explanations.
