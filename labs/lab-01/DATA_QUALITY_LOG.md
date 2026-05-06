# Data Quality Log — Lab 1

**Team:** Carlos Orellana & Mattias Morales (Group 6)

---

## Issue 1: `position` vs `positionText` — Unexpected API encoding of retirements

- **What:** We expected retired (DNF) drivers to have a null or non-numeric `position` field, based on the data dictionary description. The API does return "R" in `positionText` for retired drivers. However, after running the ingestion and auditing the data, we found that `position` is **always numeric** in the 2022–2024 dataset — even for drivers whose `positionText = "R"`. The API assigns a classification position to every driver based on laps completed, including retirements. Our 1,359-row dataset has **0 null values** in `position`. The safeguard `if res['position'].isdigit() else None` in our parser was written in anticipation of nulls but never triggered.
- **Classification:** Not technically a missing data issue — it's an API behavior difference from what the documentation implied. If it were a missing data concern, we'd classify it as **MNAR** (drivers who retired would be the ones with missing positions). But in practice no values are missing.
- **Impact:** Our target variable `top10_finish` is unaffected — retired drivers get classified positions (e.g., P18, P19) which are all > 10, so they're correctly labeled as "not top 10." However, we cannot use `position IS NULL` as a retirement indicator; we must rely on the `status` field instead.
- **Decision:** Confirmed 0 nulls via data audit. Kept `position` as-is. Use `status` field to identify retirement type (not `position`). Kept the null-handling safeguard in the parser for robustness.
- **Justification:** The `top10_finish` target is constructed correctly regardless — any position > 10 maps to 0. Retirements are handled implicitly by their high classification positions.

## Issue 2: `grid` — Pit lane starts coded as 0

- **What:** Some drivers start from the pit lane instead of the grid (due to penalties, car changes after parc fermé, etc.). The API encodes these as `grid = 0`.
- **Classification:** MAR — the value isn't truly "missing," but `grid = 0` doesn't correspond to an actual starting position. It depends on observable factors (penalty, technical issue) rather than the grid value itself.
- **Impact:** Affects our heuristic baseline. A grid value of 0 is below our threshold of 10, which would incorrectly predict a top-10 finish for pit lane starters (who almost never finish top 10).
- **Decision:** Our heuristic rule explicitly requires `1 <= grid <= 10` to predict top 10. Grid=0 defaults to "not top 10" prediction, which is correct behavior. We kept the value as-is rather than imputing.
- **Justification:** Pit lane starts almost always result in finishes outside the top 10 due to the massive disadvantage. The heuristic handles this correctly, so no imputation needed.

## Issue 3: `status` — High cardinality of retirement reasons

- **What:** The `status` field contains many distinct values: "Finished", "+1 Lap", "+2 Laps", "Engine", "Gearbox", "Collision", "Accident", etc. This makes it hard to use as a simple binary feature.
- **Classification:** Not a missing data issue — all rows have a status value. This is a data representation problem.
- **Impact:** We needed a clean binary indicator for DNF. Using `status` raw would introduce dozens of categories, many with very few observations.
- **Decision:** Created a binary `dnf` flag: `True` if status is not "Finished" (and not "+N Laps" which still counts as finishing). Actually we ended up using `status != 'Finished'` which is slightly aggressive — "+1 Lap" drivers DID finish the race, just a lap behind. But this is a post-race variable anyway, so it only matters for our EDA understanding, not for the baseline.
- **Justification:** For EDA purposes, the binary DNF flag is sufficient. We're not using status as a prediction feature (it's post-race), so the granularity doesn't affect our model.

## Issue 4: `points` — Zero-inflated distribution

- **What:** Most race entries score 0 points (only the top 10 score, plus 1 point for fastest lap). This creates a heavily zero-inflated distribution.
- **Classification:** Not missing data — the zeros are real. This is a distributional issue.
- **Impact:** If we were to use points as a feature (which we can't — it's post-race), the zero inflation would make it tricky to model. It also affects how we interpret summary statistics: the mean points per race entry is low and the median is 0.
- **Decision:** Points is a post-race outcome, so we flagged it as leakage and excluded it from features. We only use it in EDA to verify our understanding of the scoring system.
- **Justification:** Post-race variable, cannot be used. The zero-inflation is expected behavior given F1's scoring rules.

## Issue 5: `dob` (date of birth) — Varying driver ages, potential staleness

- **What:** Driver birth dates are available from the API. Some drivers in our dataset span a wide age range (early 20s to 40+). The data itself isn't missing, but age as a feature has questionable predictive value.
- **Classification:** MCAR (for the rare cases where it might be missing in older data). In our 2022-2024 dataset, all drivers have DOB records.
- **Impact:** We initially considered engineering an "age" or "experience" feature but realized it's confounded with team quality (experienced drivers stay because top teams keep them, and top teams score more).
- **Decision:** Did not use driver age as a feature. We flagged this in our trap check (spurious correlation between experience and performance, confounded by team quality).
- **Justification:** Not a useful independent predictor. The causal chain is: top team → keeps good driver → driver accumulates experience. Using age would pick up team effects, not genuine age effects.

## Issue 6: `constructor` — Name changes and team identity shifts

- **What:** Some constructors changed names across seasons. For example, AlphaTauri became RB (or vice versa terminology-wise). The API uses different `constructorId` values for what is functionally the same team under new branding.
- **Classification:** Not missing, but a consistency/identity issue.
- **Impact:** If encoding constructor as a categorical feature, a team that changed its name would appear as two separate teams, splitting their historical data.
- **Decision:** We noted this but didn't merge constructor identities for the heuristic baseline (which doesn't use constructor anyway). For Lab 2, we'd need to create a mapping table for renamed teams.
- **Justification:** The heuristic only uses grid position. For future work, constructorId changes would need to be resolved, but it's not blocking for Lab 1.

## Issue 7: Temporal leakage risk in feature engineering

- **What:** Computing rolling averages or historical rates (e.g., "driver's top-10 rate in past races") requires careful ordering. If we compute an expanding mean without sorting by date first, we could leak future data into past calculations.
- **Classification:** Not a data quality issue per se — this is a process/engineering risk.
- **Impact:** Could lead to inflated model performance if historical features accidentally include future outcomes.
- **Decision:** When computing `constructor_hist_top10` and `driver_hist_top10` in the correlation analysis, we explicitly sorted by date first and used `expanding().mean()` grouped by entity. This ensures each calculation only uses data from prior races.
- **Justification:** Temporal ordering is essential for any time-series feature engineering in F1 data. We verified this through our leakage checks.
