# Hito 2 What-If Comparison

Scenario context: 2023 Austrian Grand Prix, Ocon (Alpine), grid P12. Historical finish: P14.

The paired comparison holds driver, constructor, circuit, grid position, and prior-performance context fixed. Only strategy scenario fields change:

- Conservative one-stop: `M-H`, pit lap 32, total pit time 22.0s.
- Aggressive two-stop: `S-M-H`, pit laps 18 and 42, total pit time 44.0s.

| target | one_stop_probability | two_stop_probability | delta_two_minus_one | recommendation |
| --- | --- | --- | --- | --- |
| is_top10 | 0.134 | 0.154 | 0.020 | two_stop |
| is_top5 | 0.087 | 0.436 | 0.349 | two_stop |

## Recommendation

`is_top10` is nearly indifferent: the two-stop changes P(top10) by only 0.020. If the team used only Hito 1's target, this would look like a marginal points-finish decision.

`is_top5` changes the decision surface: the same two-stop scenario increases P(top5) by 0.349. The expansion target therefore surfaces a recommendation that `is_top10` alone could not produce: accept the extra pit stop only when the objective is to chase a stronger result, not merely to protect points probability.

This is still a scenario-model recommendation, not proof of causal strategy value. Faster cars and race states select into different strategies historically, so this case should be used as a decision prompt for engineers rather than an automatic pit-wall command.
