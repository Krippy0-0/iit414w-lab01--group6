# Hito 2 Error Analysis

All slices use the calibrated gradient boosting scenario model on the untouched 2023-2024 test block. The additional context slice is constructor tier because the Hito 1 limitation was strategy confounding with car pace and team quality.

## Target: `is_top10`

### Strategy type
| strategy_type | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| three_plus_stop | 153 | 0.405 | 0.461 | 0.145 | 0.290 |
| one_stop | 353 | 0.561 | 0.587 | 0.133 | 0.264 |
| two_stop | 368 | 0.543 | 0.547 | 0.113 | 0.243 |
| no_stop | 15 | 0.000 | 0.104 | 0.015 | 0.104 |

### Circuit type
| circuit_group | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| hybrid | 118 | 0.508 | 0.524 | 0.151 | 0.289 |
| permanent | 579 | 0.518 | 0.541 | 0.122 | 0.254 |
| street | 192 | 0.521 | 0.548 | 0.115 | 0.247 |

### Additional context: constructor tier
| constructor_tier | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| midfield | 407 | 0.619 | 0.641 | 0.137 | 0.285 |
| backmarker | 312 | 0.189 | 0.226 | 0.122 | 0.259 |
| front | 170 | 0.876 | 0.879 | 0.101 | 0.186 |

### Weather audit slice
| weather_actual | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| wet | 121 | 0.496 | 0.520 | 0.144 | 0.287 |
| dry | 768 | 0.521 | 0.544 | 0.122 | 0.252 |

## Target: `is_top5`

### Strategy type
| strategy_type | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| three_plus_stop | 153 | 0.196 | 0.226 | 0.114 | 0.198 |
| one_stop | 353 | 0.283 | 0.327 | 0.093 | 0.178 |
| two_stop | 368 | 0.272 | 0.310 | 0.081 | 0.160 |
| no_stop | 15 | 0.000 | 0.042 | 0.013 | 0.042 |

### Circuit type
| circuit_group | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| street | 192 | 0.260 | 0.287 | 0.101 | 0.180 |
| permanent | 579 | 0.259 | 0.302 | 0.093 | 0.176 |
| hybrid | 118 | 0.254 | 0.294 | 0.060 | 0.138 |

### Additional context: constructor tier
| constructor_tier | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| front | 170 | 0.676 | 0.718 | 0.174 | 0.309 |
| midfield | 407 | 0.278 | 0.337 | 0.118 | 0.227 |
| backmarker | 312 | 0.006 | 0.018 | 0.010 | 0.024 |

### Weather audit slice
| weather_actual | n | actual_rate | mean_pred | brier | abs_error |
| --- | --- | --- | --- | --- | --- |
| wet | 121 | 0.248 | 0.292 | 0.122 | 0.200 |
| dry | 768 | 0.260 | 0.298 | 0.085 | 0.167 |

## Failure-Mode Hypotheses

- `is_top10` has its largest strategy-slice error on `three_plus_stop`, suggesting incident-heavy or recovery races remain harder to represent as normal strategy scenarios.
- `is_top10` is weakest on hybrid/semi-street circuits, where track position, safety-car timing, and pit-loss interact in ways the race-level features compress too aggressively.
- `is_top5` has its largest constructor-tier error for front teams. The model separates front teams from the field, but top-five outcomes are sensitive to small gaps among front-running cars.
- Wet races increase error for both targets, so weather should stay in the audit layer until the final report can test richer wet-lap and race-control features.
