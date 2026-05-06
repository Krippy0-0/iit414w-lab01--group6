# Technical Memo — F1 Points Prediction Model

**To:** Head of Strategy  
**From:** Carlos Orellana & Mattias Morales, Data Analysis Group  
**Subject:** Can we predict how many points our driver will score on Sunday?  
**Date:** April 2026

---

## What We Built

We trained a computer model that predicts, before each race starts, how many championship points a driver is expected to score. The model uses information available on race morning: starting grid position, recent finishing positions, and which team the driver is racing for.

We tested the model against the 2023 and 2024 seasons — races the model had never seen during training.

---

## What the Numbers Mean

Our best model was off by approximately **2.8 points per driver per race** on average. To put that in context:

- A driver finishing P5 scores 10 points. A driver finishing P6 scores 8 points. A 2.8-point error means we are roughly accurate to within one or two positions for most drivers.
- The simplest possible benchmark — a lookup table that says "drivers starting from position 1 average X points, drivers from position 2 average Y points" — was off by **3.2 points per race**. Our model is **0.4 points more accurate** than this naive baseline.
- A model that ignores all race information and just guesses "everyone scores about 5 points" is off by **5.9 points** — more than twice our error.

| Approach | Average error (points) | Notes |
|---|---|---|
| Ignore all data, guess ~5 pts | 5.9 | Useless for decision-making |
| Grid position lookup table only | 3.2 | Strong simple benchmark |
| **Our model (Random Forest)** | **~2.8** | **Best result; uses 5 features** |

---

## What the Model Can Do For Us

**Championship points accumulation:** Before each race weekend, we can generate expected points for all 20 drivers. Summing these across a season gives a projected constructor championship standing — useful for deciding whether to prioritise one driver over another in a contested race.

**Risk assessment:** When the model predicts a frontrunner scores low points (say, 3–5 points instead of 18–25), that is a signal that something in their recent form or circuit history is unusual. This can prompt the strategy team to investigate further before race day.

---

## What the Model Cannot Do

**Race-day incidents:** The model cannot predict safety cars, first-lap collisions, or mechanical failures. In 2024, Max Verstappen started from pole position at the Australian GP and retired — the model would have predicted ~24 points, but he scored 0. No pre-race model can foresee these events.

**Reliability:** About half of all race entries score zero points. The model sometimes predicts 1–3 points for midfield drivers who end up scoring zero. The 2.8-point average error is partially driven by these cases.

**Recommendation:** Use the model's point estimates as a planning range, not a guarantee. A prediction of "15 points" should be read as "somewhere between 10 and 20 points, most likely." The model is a decision-support tool, not a crystal ball.

---

## Recommendation

The model is ready for internal planning use. It outperforms the simple grid-based lookup table that teams currently use as a reference, and the improvement is consistent across both 2023 and 2024 seasons. We recommend integrating point predictions into the pre-race briefing pack as a supplementary figure, clearly labelled with the ±2.8-point typical error.
