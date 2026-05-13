# Hito 2 Mitigations

| Risk | Consequence | Mitigation before deployment |
| --- | --- | --- |
| Strategy confounding with car pace and race state | The advisor may credit two-stop plans that were actually chosen by faster cars or chaotic races. | Add matched comparisons by constructor tier, grid band, and race; report deltas only when scenarios are supported by similar historical cases. |
| Sparse `three_plus_stop` and `no_stop` examples | Error estimates are noisy and may overreact to unusual races. | Flag low-support slices and avoid strong recommendations when a proposed strategy has few analogues. |
| Wet and safety-car races compressed into coarse features | The model can miss timing-specific pit windows. | Add lap-level weather/race-control features from the lap-level dataset and stress-test wet races separately. |
| `is_top10` and `is_top5` objectives conflict or diverge | A points-preserving strategy may not maximize stronger finishes, and a top-five chase may add pit-risk without meaningful top-ten gain. | Present both targets side by side and require the engineer to select the race objective before interpreting recommendations. |
| Calibration drift across seasons | 2024 behavior may differ from 2019-2022 due to car development and regulations. | Recalibrate each season and monitor Brier/log loss by constructor tier and circuit group. |
