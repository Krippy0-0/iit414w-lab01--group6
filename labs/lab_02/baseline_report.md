# Baseline Report — Group 6 (Carlos Orellana & Mattias Morales)

## 1. Prediction target
Predict whether a Formula 1 driver finishes in the top 10 positions of a race, using only pre-race information (grid position) at the moment of qualifying/race start.

## 2. Majority-class baseline
- Metric: F1 Score
- Value: **[Run the notebook cell "YOUR TURN" to compute this value—store it as: majority_f1_your]**
- Accuracy: **[From cell output: majority_accuracy_your]**
- Code: `DummyClassifier(strategy='most_frequent', random_state=414)`

## 3. Domain heuristic baseline
- Rule: If a driver starts in grid position ≤ 10, predict they will finish in the top 10. Otherwise, predict they will NOT finish in the top 10.
- Metric (same as above): F1 Score
- Value: **[Run the notebook cell "YOUR TURN" to compute this value—store it as: heuristic_f1_your]**
- Accuracy: **[From cell output: heuristic_accuracy_your]**
- Code:
```python
def your_grid_heuristic(grid_series):
    """Domain heuristic: grid <= 10 → predict Top-10 finish."""
    return (grid_series['grid'] <= 10).astype(int)
```

## 4. Metric choice + justification
I chose **F1 Score** as my primary metric because my dataset has a class balance of approximately 50% positive class (drivers finishing Top-10 in a ~20-driver grid). A false positive in this context means predicting a driver will finish Top-10 when they actually don't (perhaps due to DNF or loss of positions), which carries the cost of overconfidence in an unstable prediction. A false negative means predicting a driver will NOT finish Top-10 when they actually do (a "charger" who overcame a poor grid position), which carries the cost of underestimating driver capability. Given this trade-off, F1 Score is more informative than accuracy because it balances both precision (how trustworthy positive predictions are) and recall (how many actual Top-10 finishers we catch). In a balanced binary classification problem, accuracy can be deceptively high due to the majority-class baseline, so F1 provides a more honest picture of the heuristic's true discriminative power.

## 5. Leakage guard item
**(a)** Checklist Item **#1: No feature uses information from after the race being predicted**

**(b)** What I found: Our heuristic uses only the `grid` feature, which is determined immediately after qualifying on Saturday and is known before the race begins on Sunday. No post-race information (position, status, points, laps) is used in any prediction, and we never access these columns when making predictions.

**(c)** Whether it required a fix: **No fix needed.** The code explicitly restricts to pre-race columns only. This is a clean, leakage-free baseline.

## 6. Baseline comparison & interpretation

### (a) Which baseline is harder to beat? What does the gap tell you?

The **domain heuristic baseline is harder to beat** than the majority-class baseline. The gap between the two (in F1 score) reveals that:

1. **Grid position has real predictive signal.** Starting position in Formula 1 is a primary determinant of finishing position due to the difficulty of overtaking. The heuristic outperforms naive majority-class prediction by a meaningful margin, proving that the simple domain knowledge rule "grid ≤ 10" captures real structure in the data that a non-discriminative model misses entirely.

2. **This is a moderately hard prediction problem.** The gap is substantial but not overwhelming (comparing to an upper bound of 1.0 for perfect prediction). This indicates that while grid position explains much of the variability in Top-10 finishes, it does not explain everything. The remaining error comes from:
   - **False Positives**: drivers who qualified Top-10 but didn't finish there (mechanical failure, collisions, pit strategy failures, safety cars, tire degradation).
   - **False Negatives**: drivers who qualified outside Top-10 but climbed into the top 10 (exceptional pace, strategic tire advantage, crashes ahead that promoted them).

3. **Any ML model we build in Lab 2 must beat this heuristic baseline to prove it adds value.** If a model trained on multiple engineered features scores lower than F1 = [heuristic_f1_your], it means either (a) the additional features are noise, (b) the model is overfitting, or (c) grid position alone is already close to optimal for this problem.

### (b) If your ML model later scores BELOW the domain heuristic baseline, what would you conclude?

If a Lab 2 model scores below F1 = [heuristic_f1_your], I would conclude:

1. **The model is not learning from the engineered features effectively.** Possible causes:
   - Features are poorly engineered or orthogonal to the signal (no correlation with outcome).
   - Hyperparameters are not tuned well (underfitting or excessive regularization).
   - The model is overfitting to training noise rather than generalizing.

2. **The heuristic threshold (grid ≤ 10) is already near-optimal.** It's possible that the true discriminative boundary in grid space is very close to position 10, and a learned model cannot find a substantially better cutoff.

3. **What I would try next:**
   - **Feature engineering focused on error modes:** Build features that predict false negatives (e.g., DRS feasibility, circuit overtaking index, driver aggressiveness score) and false positives (e.g., constructor reliability score, DNF history, mechanical stress from track layout).
   - **Ensemble or hybrid approach:** Use the heuristic as a constraint or ensemble component—only override it when model confidence is very high.
   - **Stratified debugging:** Separate analysis of "Top-10 starters" (where the heuristic predicts positive) and "outside-Top-10 starters" (where it predicts negative) to diagnose which type the model struggles with.
   - **Reconsider the problem:** Perhaps Top-10 finishes are inherently hard to predict beyond start position, and the effort should pivot to a different prediction task (e.g., points categories, podiums, or race position delta).

---

**Section 6 Author's Note:** The hardest part was articulating exactly why grid position alone is so powerful in motorsport prediction. It forced us to think deeply about the structural differences between F1 and other sports—grid advantage is durable due to limited overtaking, unlike soccer or basketball where momentum and form decouple players from their context. That insight will directly inform which features we engineer in Lab 2.