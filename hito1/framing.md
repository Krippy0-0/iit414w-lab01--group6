# Hito 1 - Problem Framing + Baseline

Team: Carlos Orellana and Mattias Morales, Group 6  
Module: Capstone - F1 Race Strategy Advisor  
Target locked by course: `is_top10`

## 1. Decision Context

The product we are framing is a race-weekend strategy advisor for a Formula 1 pit wall. The decision we support is: given a specific driver-race context, should the team prefer one strategy scenario over another if the objective is to maximize the probability of finishing in the points, represented here by top 10 finish?

The direct user is the race strategy group: strategy engineer, performance engineer, and sporting director. The decision window is after qualifying and before the race start, when grid position, team/driver history, circuit type, and practice/qualifying summaries are available. The unit of prediction is one driver in one Grand Prix.

This is not a deployment-ready optimizer in Hito 1. It is a disciplined baseline package for deciding whether the official capstone race-level dataset has enough signal to support scenario comparison in Hito 2. The professional recommendation at this stage is: do not deploy this tool for real strategy calls unless Hito 2 confirms calibration under scenario stress tests and explicitly handles confounding between strategy, car pace, incidents, and weather.

## 2. Target and Primary Metric

The locked target is `is_top10`, equal to 1 when the final classified position is 10 or better and 0 otherwise. This target maps directly to a points finish under modern F1 scoring and is understandable to a strategy group: higher predicted probability means a higher chance of scoring points.

The primary metric is Brier score because the advisor produces probabilities, not just rankings. A strategy comparison like "one stop gives 0.58 P(top10), two stop gives 0.52" only helps if the probabilities are calibrated enough to compare. Brier score rewards both discrimination and calibration, and it is easy to explain as mean squared probability error. We also report log loss because it punishes overconfident wrong predictions, and ROC-AUC because the docent reference includes it and it checks ranking quality.

## 3. Baseline Plan with F1-Defendable Rationale

We implement two Hito 1 baselines using the locked temporal split: train 2019-2021, calibration 2022, and test 2023-2024.

The first baseline is a grid-rule heuristic: high probability for starts P1-P5, medium-high for P6-P10, lower for P11-P15, and very low for P16+. This is defendable from F1 logic alone because track position, clean air, and car pace revealed by qualifying are the strongest simple signals for finishing in the points. It does not use post-race strategy information.

The second baseline is a simple calibrated gradient boosting model. It uses pre-race features plus strategy fields as scenario inputs: `n_stops`, `strategy_type`, `compound_sequence`, stint lengths, pit-lap fields, and pit-time summaries. This distinction is essential. In the raw historical data those strategy fields are observed after the race, so they would be leakage in a normal pre-race prediction model. In this capstone they are allowed only because the product is a scenario comparison tool: the user intentionally sets those values to ask what would happen under a one-stop or two-stop plan.

The notebook result on the untouched 2023-2024 test block is:

| Model | Brier | Log loss | ROC-AUC | Reflection |
|---|---:|---:|---:|---|
| Grid-rule heuristic | 0.160 | 0.495 | 0.839 | Beats the course grid-rule floor of 0.208 but is too coarse for strategy comparison. |
| Calibrated GB strategy baseline | 0.125 | 0.426 | 0.902 | Beats the docent reference of Brier 0.132 and ROC-AUC 0.892 on the locked test block. |

This is a strong Hito 1 baseline because it beats the grid-rule floor and the docent calibrated reference without changing the locked split. We should still describe it as promising, not proven, because Hito 1 has only one target and limited scenario robustness analysis.

## 4. What-If Comparison Plan

The model will support paired comparisons where all pre-race context is held fixed and only strategy scenario inputs change. Hito 1 includes a concrete example cell in the notebook; Hito 2 should formalize this as an interface or reusable function.

Scenario 1: Charles Leclerc, Monaco Grand Prix 2024. Compare `n_stops=1`, `strategy_type=one_stop`, `compound_sequence=M-H`, `stint1_length=34`, `stint2_length=44`, `avg_pit_stop_duration_s=22.5`, `total_pit_time_s=22.5`, `first_pit_lap=34`, `last_pit_lap=34` against `n_stops=2`, `strategy_type=two_stop`, `compound_sequence=M-M-H`, `stint1_length=22`, `stint2_length=21`, `stint3_length=35`, `avg_pit_stop_duration_s=22.5`, `total_pit_time_s=45.0`, `first_pit_lap=22`, `last_pit_lap=43`.

Scenario 2: Sergio Perez, British Grand Prix 2024. Compare an aggressive two-stop plan with `n_stops=2`, `strategy_type=two_stop`, `compound_sequence=S-M-H`, `stint1_length=18`, `stint2_length=26`, `stint3_length=28`, `total_pit_time_s=44.0`, `first_pit_lap=18`, `last_pit_lap=44` against a conservative one-stop plan with `n_stops=1`, `strategy_type=one_stop`, `compound_sequence=M-H`, `stint1_length=31`, `stint2_length=40`, `total_pit_time_s=22.0`, `first_pit_lap=31`, `last_pit_lap=31`.

Scenario 3: Lando Norris, Hungarian Grand Prix 2024. Compare `n_stops=1`, `strategy_type=one_stop`, `compound_sequence=M-H`, `stint1_length=33`, `stint2_length=41`, `total_pit_time_s=21.5`, `first_pit_lap=33`, `last_pit_lap=33` against `n_stops=2`, `strategy_type=two_stop`, `compound_sequence=M-H-M`, `stint1_length=22`, `stint2_length=30`, `stint3_length=28`, `total_pit_time_s=43.0`, `first_pit_lap=22`, `last_pit_lap=52`.

For each pair, the recommendation should be reported as a probability delta, not as a guaranteed outcome.

## 5. Known Dataset Limitations

The recovered dataset starts in 2019, not earlier. This means the model cannot learn older regulation-era behavior and has limited exposure to rare race patterns. Any recommendation should be understood as modern-era only.

`qualifying_position` is a stand-in for `grid_position`, and `qualifying_time_s` is intentionally empty in the race-level build. We use position-like qualifying/grid fields carefully, but we do not tell a story around qualifying time because the assignment explicitly warns that this would be a graded error.

`safety_car_periods` is a binary driver-race indicator in this build, not a complete race-control interval count. We keep it as an audit/stress-test column and do not use it as a normal predictor.

Strategy features are observed post-race in the raw data. They are not pre-race facts. We use them only as scenario inputs, which makes sense for a what-if advisor but would be leakage in an ordinary predictive model.

Finally, strategy choice is confounded with car pace, driver quality, weather, traffic, and incidents. A two-stop strategy may look better historically partly because faster cars or chaotic races selected into it. Hito 2 must test whether recommendations remain stable under slices by constructor tier, grid band, and circuit type.

## 6. Three Hito 2 Experiments

Experiment 1: add a second target required by Hito 2, likely `will_dnf` or podium/top5 depending on the assignment page. Hypothesis: a second target will reveal when a high top10 probability hides unacceptable reliability or downside risk. Metric: Brier score and calibration curve by target.

Experiment 2: compare calibration methods using the same locked calibration block: isotonic vs Platt scaling. Hypothesis: Platt scaling may reduce overfitting in sparse high-probability bins while isotonic may better correct nonlinear probability errors. Metric: test Brier, log loss, and calibration curve by probability decile.

Experiment 3: scenario robustness slices. Hypothesis: strategy deltas are less reliable for back-grid starts and incident-heavy races because confounding is stronger there. Metric: Brier and average absolute calibration error by grid band, constructor tier, circuit type, and `safety_car_periods` audit slice.

## 7. Team Workflow

Carlos owns the dataset recovery, notebook execution, metric reporting, and GitHub submission. Mattias reviews the framing, validates whether the F1 rationale is defendable, and checks the leakage audit against the rubric.

Between Monday and Wednesday, Carlos prepares the executable baseline and README, Mattias edits the decision framing and scenario plan, and both review `PROMPTS.md` so AI use is documented honestly. Before the deadline, the team runs the notebook from a clean repo state, confirms the required files exist, commits the package, and submits the GitHub URL in Canvas.
