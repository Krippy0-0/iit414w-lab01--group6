# AI Usage Documentation — Lab 1

**Team:** Carlos Orellana & Mattias Morales (Group 6)

---

## Entry 1 — March 12, 2026 — Jolpica API pagination and JSON parsing

**Context:** We needed to figure out how to paginate through the Jolpica API results since it caps responses at 100 rows. The class notebook had an example but we wanted to make sure we understood the JSON nesting structure correctly for our own ingestion function.

**Prompt(s):**
- "How does the Jolpica F1 API handle pagination? What's the structure of the JSON response for race results?"
- Follow-up: "What's the difference between the `position` and `positionText` fields in the results?"

**Output:** The AI explained that:
- The API uses `limit` and `offset` query parameters
- `MRData.total` gives the total number of results for pagination control
- `position` is the numeric finishing position, `positionText` includes "R" for retired drivers, "D" for disqualified, etc.
- Results are nested under `MRData.RaceTable.Races[].Results[]`

**Validation:** We tested with a manual API call (`curl`) to verify the JSON structure matched what the AI described. We also cross-checked against the W02_Mon notebook which uses the same API.

**Adaptations:** We added the `isdigit()` check for position parsing that the AI suggested, since `positionText` can be non-numeric. We also added `time.sleep(1)` between requests to avoid hammering the API, which wasn't in the AI output but seemed like good practice.

**Final Decision:** Partially used. The JSON structure explanation was accurate and saved us time. We wrote our own ingestion function rather than copying code directly, but the structural understanding from the AI was helpful.

---

## Entry 2 — March 13, 2026 — Understanding Precision, Recall, and F1-Score for stretch goals

**Context:** We wanted to go beyond accuracy for our baseline evaluation (stretch goals 4.6-4.8). We'd read Burkov Ch. 2 which mentions these metrics, but wanted to make sure we understood them well enough to interpret the numbers we'd compute.

**Prompt(s):**
- "Can you explain precision and recall in the context of a binary classification problem? Use a concrete example with F1 racing — predicting if a driver finishes in the top 10."
- "When would I care more about precision vs recall for this F1 top-10 prediction problem?"
- "How do I compute these with sklearn?"

**Output:** The AI gave a clear breakdown:
- Precision = TP / (TP + FP) — "of all drivers we predicted would finish top 10, what fraction actually did?"
- Recall = TP / (TP + FN) — "of all drivers who actually finished top 10, what fraction did we correctly predict?"
- F1 = harmonic mean, balances both
- For sklearn: `from sklearn.metrics import precision_score, recall_score, f1_score, classification_report`
- The AI suggested precision matters more if wrong positive predictions are costly (e.g., betting), recall matters more if missing a positive is costly (e.g., fantasy team selection)

**Validation:** We computed the metrics by hand for a small subset of our validation results to confirm sklearn was producing correct numbers. We also verified against the confusion matrix counts (which matched). The precision/recall trade-off explanation made intuitive sense when we looked at our error types (false positives = DNFs from top-10 starters, false negatives = chargers from outside top 10).

**Adaptations:**
- We kept the metric computation straightforward using sklearn rather than trying to implement from scratch.
- We were honest in our notebook about not fully understanding when to prefer which metric — we wrote "we're still building our intuition on this" because that's true.
- We chose F1-score as our primary metric because the classes are balanced and we didn't have a strong reason to prefer precision over recall.

**Final Decision:** Used. The explanation helped us understand and report the stretch metrics. We documented our uncertainty about metric selection honestly rather than pretending we fully get it.

---

## Entry 3 — March 13, 2026 — Trap check design (spurious correlation)

**Context:** The lab requires at least one explicit trap awareness check. We wanted to replicate the approach from Wednesday's lecture (W02_Wed notebook) where the instructor showed how grid-DNF correlation is confounded by constructor tier.

**Prompt(s):**
- "How would I check if the correlation between grid position and DNF rate in F1 is actually a spurious correlation caused by car quality?"

**Output:** The AI suggested splitting the data by constructor tier (top teams vs. midfield/backmarker) and computing the grid-DNF correlation within each group separately. If the within-group correlations are much weaker than the overall, that's evidence of confounding.

**Validation:** This is exactly the approach from the Wednesday class notebook, so we were confident it was correct. We implemented it and the pattern matched expectations — the within-group correlations were weaker.

**Adaptations:** We used the top-5 constructors by top-10 rate (computed from our own data) as the "Top Team" tier, rather than hardcoding team names, so it adapts to the data.

**Final Decision:** Used. This was a direct application of what we learned in class, and the AI confirmed the approach was sound.

---

## Entry 4 — March 14, 2026 — Debugging pandas deprecation warnings

**Context:** When running the EDA notebook we kept getting FutureWarnings from the `groupby().apply()` calls. The messages mentioned `observed` and `include_groups`. It wasn't breaking anything but the warnings were cluttering the output and we weren't sure if they meant something in our logic was actually wrong.

**Prompt(s):**
- "Getting `FutureWarning: DataFrameGroupBy.apply operated on the grouping columns, this behavior is deprecated` — what does `include_groups=False` do and do I need it?"
- "Also getting `FutureWarning: The default value of observed=False is deprecated` when grouping by a Categorical column."

**Output:** The AI explained:
- `include_groups=False` prevents pandas from passing the grouping columns into the lambda inside `.apply()` — required in pandas 2.0+ to avoid ambiguity
- `observed=True` tells pandas to only include categories that actually appear in the data, not all possible categories
- Both are pandas tightening up previously-ambiguous behavior; our code was logically correct but would break in future versions

**Validation:** Added both flags, confirmed the warnings went away, and verified that the computed values did not change (the warnings were cosmetic, not a logic error).

**Adaptations:** Added `observed=True` to the `pd.cut` + groupby calls and `include_groups=False` to the relevant `.apply()` calls. Also added `warnings.filterwarnings('ignore', category=FutureWarning)` in the setup cell for warnings coming from seaborn internals we couldn't control.

**Final Decision:** Used. The fix worked as described. We now understand that `observed` and `include_groups` are about pandas defaults changing, not bugs in our analysis.
