# Hito 2 Leakage Audit

| check | result | evidence |
| --- | --- | --- |
| Temporal split | pass | train 2019-2021, calibration 2022, test 2023-2024 |
| Outcome leakage | pass | finish_position, points, status, DNF, safety car counts, and weather outcomes are audit-only, not predictors. |
| Strategy features | conditional pass | n_stops, strategy_type, compounds, stint lengths, and pit timing are treated as user-set scenario inputs for both targets. |
| Confounding | known limitation | strategy choices correlate with car pace, driver, traffic, safety-car timing, and weather; recommendations are not causal effects. |

The scenario-input treatment holds up structurally for both `is_top10` and `is_top5` because both models receive the same user-controlled strategy fields. The interpretation changes: the model estimates historical association under a proposed strategy profile, not the causal effect of choosing that strategy in-race.
