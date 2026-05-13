# Hito 2 Baseline Comparison

Expansion target selected: `is_top5`. This target is close to the Hito 1 decision context but adds information about strong points finishes that `is_top10` hides. A strategy can keep a driver inside the points while changing the chance of a top-five result.

Locked split: train 2019-2021, calibration 2022, test 2023-2024. Binary probabilities are calibrated with isotonic regression on the 2022 calibration block only.

| target | model | brier | log_loss | roc_auc | reference |
| --- | --- | --- | --- | --- | --- |
| is_top10 | Calibrated gradient boosting scenario model | 0.125 | 0.426 | 0.902 | docent Brier 0.132 |
| is_top10 | Calibrated logistic scenario model | 0.139 | 0.462 | 0.883 | docent Brier 0.132 |
| is_top10 | Grid-rule heuristic | 0.160 | 0.495 | 0.839 | docent Brier 0.132 |
| is_top5 | Calibrated gradient boosting scenario model | 0.090 | 0.308 | 0.934 | grid-rule expansion baseline |
| is_top5 | Calibrated logistic scenario model | 0.096 | 0.317 | 0.929 | grid-rule expansion baseline |
| is_top5 | Grid-rule heuristic | 0.113 | 0.368 | 0.881 | grid-rule expansion baseline |

## Interpretation

For `is_top10`, the calibrated gradient boosting strategy model reaches Brier 0.125, beating the docent reference Brier 0.132. For `is_top5`, the grid-rule heuristic is the expansion baseline because there is no docent value for this target; the calibrated gradient boosting model improves it from Brier 0.113 to 0.090.

Model comparison evidence is consistent across both targets: the logistic model is a useful linear sanity check, but gradient boosting is better on Brier, log loss, and ROC-AUC for both `is_top10` and `is_top5`.
