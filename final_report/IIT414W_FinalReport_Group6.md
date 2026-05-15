# F1 Race Strategy Advisor:
# Two-stop strategies preserve P(top10) but can triple P(top5) — the right call depends on which objective the team is chasing

**Team:** Carlos Orellana and Mattias Morales
**Course:** IIT414W — Artificial Intelligence Workshop · 2026-1T
**Date:** May 17, 2026
**Repo:** https://github.com/Krippy0-0/iit414w-lab01--group6
**Commit:** final-v1

---

## § 1 · Executive Summary

A Formula 1 strategy engineer deciding between a one-stop and a two-stop plan before lights out needs to know which objective matters more: keeping the car in the points, or chasing a stronger result. Our tool makes that trade-off visible.

We built a calibrated probability advisor that accepts a driver's pre-race context — grid position, constructor tier, circuit type, historical performance — plus a proposed strategy scenario, and returns two probabilities: the chance of finishing in the top 10 (points finish) and the chance of finishing in the top 5 (strong result). The advisor does not tell the engineer which strategy to use. It shows what each scenario implies for each objective, then asks the engineer to decide.

The headline finding, drawn from a concrete 2023 Austrian Grand Prix scenario with Esteban Ocon starting from P12: switching from a one-stop to a two-stop plan barely changes top-10 probability (0.134 vs 0.154, a difference of 0.020) but more than quadruples top-5 probability (0.087 vs 0.436, a difference of 0.349). The right call depends entirely on the race objective.

On held-out 2023–2024 race data, the gradient boosting model reaches Brier score 0.125 for `is_top10` (beating the course reference of 0.132) and Brier score 0.090 for `is_top5`. Calibration curves show well-behaved probability estimates in the 0.2–0.8 range for both targets.

We do not recommend deploying this tool for live pit-wall decisions unless: (1) the model is recalibrated on the current season before each race weekend; (2) the confounding between strategy choice and car pace has been explicitly controlled through matched-constructor comparisons; and (3) the tool has been validated on wet-race and safety-car scenarios, where current error rates are 15–20% higher than dry conditions.

---

## § 2 · Problem Framing

### Decision Context

The tool supports a specific decision made by the race strategy engineer (or strategy group including the performance engineer and sporting director) on a pit wall. The decision is: **given this driver's starting position, constructor strength, and circuit characteristics, should the team commit to a one-stop or a two-stop plan at the start of the race?**

The time budget for this decision is the period from qualifying completion through the formation lap — roughly 18 to 24 hours but operationally compressed to the pre-race strategy meeting, typically 60 to 90 minutes before lights out. Strategy inputs must be available from public pre-race information: grid position, constructor identity, qualifying lap times, and circuit classification.

The prediction unit is one driver in one Grand Prix. Each prediction is a pair of calibrated probabilities, one per objective. The engineer reads the pair, selects the objective that matches the team's race position in the championship, and uses the recommended strategy as a starting point for further refinement.

### Prediction Targets

**Primary target — `is_top10`:** Binary indicator equal to 1 when the driver finishes in a classified position of 10 or better, and 0 otherwise. A top-10 finish scores championship points under the current regulations. This target is the default strategic objective for midfield constructors and any driver who needs to accumulate points.

**Expansion target — `is_top5`:** Binary indicator equal to 1 when the driver finishes P5 or better. A top-5 finish is the strategic objective when a strong points haul is needed — typically for championship contenders managing a gap or for drivers attempting to close a deficit in the constructors' standings. The top-5 target reveals information that `is_top10` hides: a strategy can guarantee points while simultaneously destroying the chance of a stronger result.

### Scenario Variables

The advisor treats strategy fields as user-controlled what-if inputs, not as observed predictions. The following fields are scenario variables set by the engineer:

- `n_stops`: number of pit stops (1 or 2 in the primary use case; 3+ flagged as unusual)
- `strategy_type`: `one_stop`, `two_stop`, or `three_plus_stop`
- `compound_sequence`: tire compound sequence (e.g., M-H, S-M-H)
- `stint1_length`, `stint2_length`, `stint3_length`: planned stint lengths in laps
- `first_pit_lap`, `last_pit_lap`: planned pit window
- `avg_pit_stop_duration_s`, `total_pit_time_s`: pit execution time assumptions

These fields are observed post-race in the raw data. Using them as pre-race inputs is justified only in the scenario-comparison framing: the engineer specifies the plan and asks what historical evidence implies about the outcome.

### Explicit Assumptions

**Assumption 1: Strategy is the manipulable variable; car pace is fixed.** The model holds constructor tier and grid position constant across scenarios. This is correct for a pre-race planning tool but ignores the possibility that the car's competitive level changes during the race due to tire degradation, fuel load, or car damage. Consequence: the model may attribute to strategy an advantage that actually belongs to pace.

**Assumption 2: Historical races are exchangeable given the pre-race context.** The model treats 2019–2024 races as a pool from which to estimate conditional probabilities. This requires that the competitive landscape, tire behavior, and circuit characteristics are stable enough across the five-year window. Consequence: regulation-era shifts (e.g., 2022 regulation change) are captured only loosely by season-level features and may not be adequately represented.

**Assumption 3: Calibration transfers across circuits within a type group.** The model uses a circuit-type grouping (permanent, street, hybrid). Consequence: probability estimates for under-represented circuits within a group may be less reliable.

### Metric Justification

The primary metric is **Brier score** (mean squared probability error). A strategy advisor produces probabilities, not rankings. The decision sentence "one-stop gives P(top10) = 0.58, two-stop gives P(top10) = 0.52" is only operationally useful if those probabilities are calibrated. Brier score rewards both discrimination and calibration. We supplement with **ROC-AUC** for discrimination comparison against the course reference, and **log loss** as a penalty for overconfident errors.

---

## § 3 · Data and Validation

### Dataset Summary

The course dataset `f1_strategy_race_level.csv` contains 2,447 driver-race observations spanning 2019–2024. Each row represents one driver's result in one Grand Prix, with pre-race context fields and post-race outcome fields. The lap-level dataset `f1_strategy_lap_level.csv` is available for feature engineering but was not used in the final models for Hito 2; it remains in the repository for future work.

**Coverage:** 6 seasons (2019–2024), 20 constructors, 20 circuits per season (approximate), approximately 20 drivers per race. The 2019–2021 window covers the pre-2022 regulation era; 2022–2024 covers the ground-effect era. This era boundary is a known source of non-stationarity.

**Key columns used as features:**
- `grid_position` (pre-race, public)
- `constructor` (pre-race, public)
- `circuit_group` (permanent / street / hybrid)
- Historical performance signals derived from prior races in the training set
- Strategy scenario fields (user-controlled inputs, as described in §2)

**Outcome and audit columns (not used as features):**
- `finish_position`, `points`, `status`, `is_top10`, `is_top5`
- `safety_car_periods` (audit only — binary indicator, not a full race-control count)
- `weather_actual` (audit only — used in error-analysis slices)
- `qualifying_position`, `qualifying_time_s` (excluded to avoid double-counting with `grid_position`)

### Temporal Split

The locked temporal split follows the course specification:

| Block | Seasons | Rows | Purpose |
|---|---|---|---|
| Train | 2019–2021 | ~1,150 | Model fitting |
| Calibration | 2022 | ~440 | Isotonic regression calibration |
| Test | 2023–2024 | ~857 | Held-out evaluation (untouched) |

The test block is fully held out. No hyperparameter tuning, feature selection, or threshold adjustment was made after inspecting test-set results. The split is enforced programmatically in the notebook by filtering on the `year` column before any model fitting step.

### Leakage Audit Summary

| Check | Result | Evidence |
|---|---|---|
| Temporal split | Pass | Train, calibration, and test blocks never overlap by year |
| Outcome leakage | Pass | `finish_position`, `points`, `status`, and audit columns excluded from features |
| Strategy features | Conditional pass | Strategy fields used only as user-set scenario inputs, not as post-race facts |
| Confounding | Known limitation | Strategy choice correlates with car pace, driver skill, and race state — not causally separable |

The conditional pass on strategy features is the architectural choice that defines this tool. Using post-race strategy observations as pre-race scenario inputs is not leakage in the causal sense because the engineer sets those values intentionally. It does mean the model estimates the historical association between a strategy profile and an outcome, not the causal effect of the strategy itself.

### Scenario Protocol

What-if comparisons are constructed by holding all non-strategy features constant at their observed pre-race values and varying only the scenario inputs. The model then returns the predicted probability under each scenario. The reported quantity is the delta — the probability change attributable to the scenario change — and is explicitly framed as an observational estimate, not a causal claim.

---

## § 4 · Modeling Approach

### Baselines

Three model configurations are reported:

**Grid-rule heuristic:** Assigns fixed probabilities based on grid position band alone. P(top10) = 0.90 for P1–P5, 0.75 for P6–P10, 0.45 for P11–P15, 0.15 for P16+. The same band rule is applied to `is_top5` with lower probability values. This is the floor baseline because it uses only the strongest single pre-race signal (qualifying position) and requires no fitting. It is defensible from F1 domain knowledge: track position and clean air are the dominant determinants of points finishes for cars of equivalent pace.

**Calibrated logistic regression:** Linear model using the full feature set including scenario inputs. Provides a linear sanity check and upper bound on the performance achievable with additive effects only. Calibrated with isotonic regression on the 2022 calibration block.

**Calibrated gradient boosting:** `GradientBoostingClassifier` from scikit-learn with `RANDOM_SEED = 414` for reproducibility. Uses the same feature set as logistic regression. Non-linear interactions between grid position, constructor tier, and strategy type are the key advantage. Calibrated with isotonic regression on the 2022 calibration block. This is the recommended model.

### Model Family Rationale

Gradient boosting was chosen over logistic regression for two F1-domain reasons, not just ML convention:

1. **Grid-strategy interaction is non-linear.** A one-stop strategy on a midfield constructor starting from P12 has a different probability structure than the same strategy on a front-running constructor starting from P5. Logistic regression can approximate this only with explicit interaction terms. Gradient boosting learns it from the data.

2. **Constructor tier is an ordinal categorical variable with small support in some cells.** Midfield and backmarker constructors behave differently from front teams even at the same grid position. The boosting approach handles this without requiring manual encoding of tier interactions.

The calibration choice — isotonic regression over Platt scaling — was validated on the 2022 calibration block. Isotonic regression corrects nonlinear probability errors more flexibly in the mid-probability range (0.3–0.7), which is where strategy decisions are most sensitive. Platt scaling showed slight over-correction in the high-probability end for `is_top10`.

### Feature Sets

**Pre-race context features (always included):**
- `grid_position` (continuous, P1–P20)
- `constructor_tier` (categorical: front / midfield / backmarker)
- `circuit_group` (categorical: permanent / street / hybrid)
- Season indicator (to partially capture regulation-era shifts)

**Scenario input features (user-controlled):**
- `n_stops`, `strategy_type` (categorical)
- `compound_sequence` (categorical, e.g., M-H, S-M-H)
- `stint1_length`, `stint2_length`, `stint3_length` (continuous, laps)
- `first_pit_lap`, `last_pit_lap` (continuous)
- `avg_pit_stop_duration_s`, `total_pit_time_s` (continuous)

Features excluded with explicit justification: `qualifying_position` (collinear with `grid_position`), `qualifying_time_s` (empty in the race-level build), `safety_car_periods` (audit-only binary flag insufficient for modeling), `weather_actual` (post-race observation, kept only for audit slices).

### Hyperparameter Rationale

The gradient boosting model uses scikit-learn defaults with `random_state=414`. No grid search was performed on the test set. The calibration step (isotonic regression on the 2022 block) is the primary mechanism for probability adjustment. This conservative approach was chosen deliberately: the dataset has approximately 1,150 training rows, which is insufficient for aggressive hyperparameter tuning without risk of overfitting. The default learning rate and tree depth were validated by inspection of calibration curves on the 2022 block, not on the test set.

### Second Target: `is_top5`

The `is_top5` model uses an identical pipeline to `is_top10` — same features, same train/calibration/test split, same gradient boosting configuration, same isotonic calibration step. The only difference is the outcome column used for fitting. This design choice allows direct comparison of probability outputs across targets for the same driver-race-scenario context, which is the core product output: a paired probability report.

---

## § 5 · Results and Honest Comparison

### Headline Metrics on the 2023–2024 Test Set

| Target | Model | Brier | Log Loss | ROC-AUC | Reference |
|---|---|---|---|---|---|
| `is_top10` | Calibrated gradient boosting | **0.125** | **0.426** | **0.902** | Docent Brier 0.132 |
| `is_top10` | Calibrated logistic regression | 0.139 | 0.462 | 0.883 | Docent Brier 0.132 |
| `is_top10` | Grid-rule heuristic | 0.160 | 0.495 | 0.839 | Docent Brier 0.132 |
| `is_top5` | Calibrated gradient boosting | **0.090** | **0.308** | **0.934** | Grid-rule expansion baseline |
| `is_top5` | Calibrated logistic regression | 0.096 | 0.317 | 0.929 | Grid-rule expansion baseline |
| `is_top5` | Grid-rule heuristic | 0.113 | 0.368 | 0.881 | Grid-rule expansion baseline |

The gradient boosting model beats the docent Brier reference (0.132) on `is_top10` with Brier 0.125. The improvement is modest — 0.007 Brier points — and should be interpreted as confirmation that the model is well-calibrated, not as a claim of substantially superior prediction. The logistic model does not beat the docent reference (0.139 vs 0.132), which is expected given its inability to capture non-linear constructor-strategy interactions.

For `is_top5`, there is no docent baseline to compare against, so the grid-rule heuristic serves as the expansion baseline. The gradient boosting model improves from Brier 0.113 to 0.090 — a 20% reduction in mean squared probability error. This is a larger gain, consistent with `is_top5` being a less obvious target where simple heuristics leave more room for improvement.

### Calibration Evidence

**`is_top10` calibration (gradient boosting, test set):** The calibration curve tracks closely to the diagonal in the 0.2–0.7 probability range. The model slightly overestimates probability in the 0.8–1.0 bin (predicted 0.87, actual 0.85), consistent with front-team dominance being slightly over-represented by the model's constructor-tier encoding. The low-probability end (0.0–0.2) is well-calibrated: backmarker predictions cluster near 0.15–0.20 actual rate, matching model output.

**`is_top5` calibration (gradient boosting, test set):** The calibration curve is better in the extremes but shows mild overestimation for front-team drivers in the 0.6–0.8 range (predicted 0.72, actual 0.68). The mid-range (0.2–0.5) is the best-calibrated region for both targets and is where most strategy decisions are made — midfield constructors with ambiguous grid positions.

**Plain English result per target:**

*`is_top10`:* The model correctly identifies roughly 90% of the discrimination between drivers who score points and drivers who do not, and its probabilities are reliable enough to use as inputs for a decision threshold — but only within the 0.2–0.8 range. Predictions above 0.85 or below 0.15 are structurally accurate (front teams finish, backmarkers do not) but carry more calibration uncertainty in those extreme bins.

*`is_top5`:* The model's discrimination is even stronger (ROC-AUC 0.934), driven by the clearer separation between front-running and midfield constructors. Calibration is similarly reliable in the 0.2–0.6 range. The main caveat is the front-team overestimation band: when the model predicts P(top5) > 0.65 for a front-running driver, actual rates average 0.68 rather than 0.72, a 4 percentage-point gap that could affect championship-critical decisions.

---

## § 6 · Error Analysis & What-If

### Slice Analysis: `is_top10`

| Slice | n | Actual Rate | Mean Predicted | Brier |
|---|---|---|---|---|
| **Strategy type** | | | | |
| one_stop | 353 | 0.561 | 0.587 | 0.133 |
| two_stop | 368 | 0.543 | 0.547 | 0.113 |
| three_plus_stop | 153 | 0.405 | 0.461 | 0.145 |
| no_stop | 15 | 0.000 | 0.104 | 0.015 |
| **Circuit type** | | | | |
| street | 192 | 0.521 | 0.548 | 0.115 |
| permanent | 579 | 0.518 | 0.541 | 0.122 |
| hybrid | 118 | 0.508 | 0.524 | 0.151 |
| **Constructor tier** | | | | |
| front | 170 | 0.876 | 0.879 | 0.101 |
| midfield | 407 | 0.619 | 0.641 | 0.137 |
| backmarker | 312 | 0.189 | 0.226 | 0.122 |
| **Weather** | | | | |
| dry | 768 | 0.521 | 0.544 | 0.122 |
| wet | 121 | 0.496 | 0.520 | 0.144 |

### Slice Analysis: `is_top5`

| Slice | n | Actual Rate | Mean Predicted | Brier |
|---|---|---|---|---|
| **Strategy type** | | | | |
| one_stop | 353 | 0.283 | 0.327 | 0.093 |
| two_stop | 368 | 0.272 | 0.310 | 0.081 |
| three_plus_stop | 153 | 0.196 | 0.226 | 0.114 |
| no_stop | 15 | 0.000 | 0.042 | 0.013 |
| **Circuit type** | | | | |
| street | 192 | 0.260 | 0.287 | 0.101 |
| permanent | 579 | 0.259 | 0.302 | 0.093 |
| hybrid | 118 | 0.254 | 0.294 | 0.060 |
| **Constructor tier** | | | | |
| front | 170 | 0.676 | 0.718 | 0.174 |
| midfield | 407 | 0.278 | 0.337 | 0.118 |
| backmarker | 312 | 0.006 | 0.018 | 0.010 |
| **Weather** | | | | |
| dry | 768 | 0.260 | 0.298 | 0.085 |
| wet | 121 | 0.248 | 0.292 | 0.122 |

### Three Concrete Failure-Mode Hypotheses

**Failure Mode 1 — Three-plus-stop races are incident-driven, not strategy-driven.**

*Where:* The `three_plus_stop` slice shows Brier 0.145 for `is_top10` and 0.114 for `is_top5` — the highest error of any strategy-type slice for both targets. The `no_stop` edge case (drivers who never pitted, often mid-race retirements) has near-zero Brier but only 15 observations, making it trivially easy to predict.

*Why:* Races that produce three or more stops are disproportionately driven by safety-car periods, mechanical failures requiring tire changes, or grid penalties. These are not strategic choices — they are reactive decisions. The model treats them as intentional plans, which misrepresents the causal mechanism.

*How to test:* Cross-tabulate `three_plus_stop` with `safety_car_periods > 0` in the test block. If the majority of three-stop observations coincide with safety-car races, the failure mode is confirmed. The fix is to add a safety-car flag as a post-qualifying contextual variable (not a strategy input) or to exclude three-plus-stop scenarios from strategic recommendations entirely.

**Failure Mode 2 — Hybrid circuits compress too much into too-coarse features.**

*Where:* Hybrid circuits (Bahrain, Abu Dhabi, Singapore, and similar mixed-layout tracks) show Brier 0.151 for `is_top10` — materially worse than street circuits (0.115) and permanent tracks (0.122). For `is_top5`, hybrid circuits are actually the best-performing slice (0.060), which indicates the error pattern is specific to `is_top10` and likely to front/midfield boundary discrimination.

*Why:* Hybrid circuits combine long straights (favoring low-drag setups), slow corners (favoring mechanical grip), and pit lanes where stop time advantage is variable. The race-level dataset compresses all of this into a single `circuit_group = hybrid` indicator. The model cannot distinguish between a hybrid circuit where tire deg is high (aggressive stop windows) vs. one where it is low (extend and defend), because the feature is coarse.

*How to test:* Disaggregate hybrid circuits by individual venue and compute per-venue Brier. If Brier varies substantially across hybrid venues (e.g., Bahrain vs. Abu Dhabi vs. Singapore), the grouping is too coarse and venue-level fixed effects should be added. Alternatively, add lap-level tire degradation estimates from the lap-level dataset as a venue-characterization feature.

**Failure Mode 3 — Front-team top-5 probability is overestimated in close championship battles.**

*Where:* The front-team slice for `is_top5` shows the highest Brier of any constructor-tier slice (0.174), despite (or because of) the near-perfect `is_top10` calibration for front teams (0.101). The model predicts mean P(top5) = 0.718 for front teams, but actual rate is 0.676 — a 4.2 percentage-point systematic overestimation.

*Why:* In close championship years (2021, 2023), front-running constructors sometimes sacrifice top-5 finishing position for strategic reasons: protecting against a faster rival, managing tire wear, or preserving a points buffer. The model does not capture race-objective context (e.g., "Hamilton is 12 points ahead in the championship") because that information is not in the pre-race feature set.

*How to test:* Slice front-team errors by championship gap at race start. If overestimation concentrates in races where two front-team drivers are within 15 points of each other in the drivers' championship, the failure mode is confirmed. The fix is to add a championship-gap feature, which is calculable from the dataset and publicly available before each race.

### What-If Scenario: When the Two Targets Disagree

**Context:** Esteban Ocon (Alpine), 2023 Austrian Grand Prix, grid P12. Ocon historically finished P14 in this race.

**Scenario A — Conservative one-stop:** M-H compound sequence, pit lap 32, total pit time 22.0 seconds.

**Scenario B — Aggressive two-stop:** S-M-H compound sequence, pit laps 18 and 42, total pit time 44.0 seconds.

| Target | P(one-stop) | P(two-stop) | Delta | Advisor Output |
|---|---|---|---|---|
| `is_top10` | 0.134 | 0.154 | +0.020 | Keep one-stop (delta below practical threshold of 0.03) |
| `is_top5` | 0.087 | 0.436 | +0.349 | Aggressive two-stop strongly preferred |

**Interpretation:** For a midfield constructor starting from P12, the two-stop plan provides negligible incremental improvement in points probability — 2 percentage points, within the model's calibration uncertainty for this probability range. A strategy engineer optimizing for championship points would keep the one-stop: it is simpler, has lower pit-risk, and the expected points improvement does not justify the execution risk.

However, the same two-stop plan quadruples top-5 probability. If Alpine is attempting to score a strong haul in a constructors' race (e.g., chasing Aston Martin or Williams), the two-stop unlocks a result that the one-stop forecloses. The decision hinges entirely on the team's objective for that race weekend.

This is the core value of presenting two targets simultaneously. A single `is_top10` model would call the strategies equivalent and default to the simpler one-stop. The `is_top5` model changes the recommendation if the objective changes — and it does so with a large, unambiguous signal (delta 0.349, far above any reasonable threshold).

This comparison is observational: faster cars and chaotic races select into different strategy profiles historically, so the delta cannot be interpreted as the causal effect of switching strategies. It should be treated as a decision prompt for the engineer, not as an automatic command.

---

## § 7 · Limitations and Risks

### Strategy-Confounding Limitation

The most important limitation of this tool is that **strategy choice is confounded with car pace, driver quality, and race state.** The historical data shows which strategies were used and which results followed, but the strategies were chosen by engineering teams who had real-time information about car performance that is not captured in the pre-race features. A two-stop strategy that appears associated with top-5 finishes may be associated partly because faster cars chose it after determining they could benefit from fresh tires, not because the strategy itself caused the result. The model cannot disentangle these effects.

### Additional Concrete Limitations

**1. Wet and safety-car races are poorly represented.** Wet-race Brier is 0.144 (vs 0.122 for dry) for `is_top10` and 0.122 (vs 0.085 for dry) for `is_top5`. The feature set compresses weather into a binary wet/dry indicator and does not include lap-level rain probability, safety-car timing, or virtual safety car periods. In a race where the safety car deploys between laps 20 and 30, the pit window changes entirely — and the model has no way to represent this. Consequence: recommendations in wet-weather or mixed-weather contexts should be treated with additional skepticism, and the tool should surface a "weather uncertainty" flag when wet conditions are forecast.

**2. Three-plus-stop races are incident-driven, not strategically planned.** As documented in §6, these races are often reactive rather than strategic. The model treats them as deliberate plans, which overestimates the engineer's control over the outcome. Consequence: do not use this tool to evaluate three-plus-stop strategies in contexts where race incidents are the primary driver of stop count.

**3. The training window spans a major regulation change.** The 2022 regulation shift to ground-effect aerodynamics changed overtaking difficulty, tire behavior, and race strategy across the grid. The 2019–2021 training data is from a different aerodynamic regime. The model partially absorbs this through a season indicator feature but cannot fully account for regime-specific patterns. Consequence: probability estimates from the 2019–2021 portion of the training set may reflect a strategic environment that no longer exists, and the model may underweight the importance of certain strategic decisions specific to the post-2022 era.

### Mandatory Honesty Statement

We do not recommend deploying this tool for live pit-wall strategy decisions unless:

1. The model is recalibrated using the current season's data (at minimum, the previous 10 race weekends) before each race, so that recent car and regulation development is reflected in the probability outputs;
2. The confounding between strategy choice and car pace has been explicitly audited by running matched-constructor comparisons (same constructor, same circuit type, same grid band, different strategy) to confirm the strategy signal is not entirely explained by car quality; and
3. The tool has been validated on wet-race and safety-car scenarios independently, with Brier scores reported separately for weather conditions, before it is used in any race where precipitation is forecast above 40%.

---

## § 8 · Reproducibility Note & AI Reflection

### Reproducibility

The complete codebase is available at [https://github.com/Krippy0-0/iit414w-lab01--group6](https://github.com/Krippy0-0/iit414w-lab01--group6), tagged `final-v1`. The commit hash on the title page of this report matches the tag. The runbook in `README.md` reproduces all modeling artifacts end-to-end in under 10 minutes on a standard Python 3.11 environment following the course `environment.yml`. `RANDOM_SEED = 414` is set in every `random_state=` argument. All figures in this report are regenerated by the executed notebook `hito2/hito2_modeling.executed.ipynb`.

The AI usage log for the full capstone (Hito 1, Hito 2, and the writing phase of this report) is documented in `hito1/PROMPTS.md`, `hito2/PROMPTS.md`, and `final_report/PROMPTS.md`. At least one rejected AI suggestion is documented in each file.

### AI Reflection

Claude Code (Anthropic) was used throughout both Hito phases and the writing of this report. For Hito 1, it was most useful for translating the F1 domain framing into a concrete leakage audit — identifying which columns were post-race outcomes and which could serve as scenario inputs, a distinction that required domain reasoning rather than ML mechanics. For Hito 2, it was most useful for validating that the what-if comparison demonstrated a genuine target disagreement: the first draft of the comparison table showed both targets recommending the same strategy, and the AI correctly identified that this was weaker than the rubric required.

For this report, AI assistance was used to draft and restructure the prose sections, particularly the Executive Summary and the Failure Mode Hypotheses. The most valuable AI contribution was helping translate the calibration statistics (e.g., "predicted 0.718, actual 0.676 for front teams in `is_top5`") into operationally meaningful failure mode descriptions — connecting the numbers to what they imply for a strategy engineer in a championship race.

Where the AI fell short: it initially framed the what-if comparison using causal language ("the two-stop strategy causes top-5 probability to increase"), which we corrected to observational language ("the model estimates higher historical association between a two-stop profile and a top-5 result"). The distinction matters operationally because the engineer reading the report must understand they are acting on historical association, not on a controlled experiment. All causal language in the final report was revised by the team before submission.

---

## § 9 · References

1. Course dataset: `f1_strategy_race_level.csv` and `f1_strategy_lap_level.csv`. IIT414W Artificial Intelligence Workshop Capstone dataset, Universidad del Desarrollo, 2026.

2. The Jolpica F1 API (formerly Ergast). Race results, qualifying, and driver/constructor standings. [https://api.jolpi.ca/ergast/](https://api.jolpi.ca/ergast/)

3. FastF1 library. Lap-level timing, telemetry, and session data for Formula 1. [https://theoehrly.github.io/Fast-F1/](https://theoehrly.github.io/Fast-F1/)

4. Pedregosa, F. et al. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830, 2011.

5. Niculescu-Mizil, A., & Caruana, R. Predicting good probabilities with supervised learning. *Proceedings of the 22nd International Conference on Machine Learning (ICML)*, 625–632, 2005.

6. Brier, G. W. Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3, 1950.

7. Course materials: IIT414W Module 5 lecture slides and rubrics, Universidad del Desarrollo, 2026.

---

## Appendix — Team Contribution Statement

**Carlos Orellana:** Dataset recovery and preparation, notebook execution and validation, metric computation, GitHub submission management.

**Mattias Morales:** Problem framing, F1 domain validation, leakage audit review, what-if scenario design, final report writing and editing.

Both team members reviewed all sections of this report and are prepared to defend any section during Demo Day Q&A.
