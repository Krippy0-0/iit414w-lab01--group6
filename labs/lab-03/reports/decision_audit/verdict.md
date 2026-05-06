# Verdict - Live Strategy Calls

**Verdict:** No-Go as a live strategy-call tool.

The score is not the verdict. The model beats the grid heuristic for pre-race point estimates: test MAE is 2.838 versus 3.246, a 12.57% lift. That is useful evidence for a briefing pack, but it does not make the tool fit for live calls. The live-call audit has 0 live-race inputs, 0 live refreshes, and 0 named live-call owner. At the action proxy of predicted points >= 10, precision is 0.776 and recall is 0.651, below the required 0.850 and 0.700. The expensive error side is also larger: weighted false-positive cost is 86.0 versus weighted false-negative cost of 80.0.

## Flip-Condition to Go

The verdict flips to Go only if a live version of the tool satisfies all three conditions on the same 2023-2024 test window:

1. Live-race input count >= 1 and live refresh count >= 1 before the strategy call window.
2. Operating-point precision >= 0.850 and recall >= 0.700 for the predicted-points >= 10 action point.
3. Weighted false-positive cost <= weighted false-negative cost under the 2.0 versus 1.0 live-call cost rule.

"Use a better model" is not the lever. The lever is adding live race-state evidence and proving that it changes the operating point.

## Smallest Experiment

Run a two-hour notebook experiment that adds one live proxy input available during a race, such as current running position after lap 10 or pit-stop-adjusted track position. Recompute the same Decision Audit Metrics cell on 2023-2024 races and compare only the three flip-condition numbers: live input count, operating-point precision/recall, and weighted false-positive versus false-negative cost.

## Downgrade Condition

The verdict remains or returns to No-Go if the tool stays pre-race-only, if live refresh count remains 0, or if false positives continue to cost more than false negatives under the live-call cost rule. A model that is accurate before lights out can still be unsafe once safety cars, tire state, failures, and incidents start changing the race.
