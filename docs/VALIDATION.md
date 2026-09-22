# Validation plan

## PoC checks completed

- Deterministic cohort generation and held-out evaluation.
- Input range validation through Pydantic and domain checks.
- Unit tests for probability bounds, beneficial scenario directionality, stream assimilation, and invalid readings.
- API tests for health, risk, simulation, and invalid input.
- Safe fallback when the learned artifact is absent.

## Clinical validation gates

| Gate | Study | Pass criteria (to be pre-specified with clinicians) |
|---|---|---|
| 1 | Retrospective internal | Discrimination, calibration, missingness robustness |
| 2 | External Indian cohort | Site/device/subgroup transportability |
| 3 | Silent prospective | Operational reliability and alert burden |
| 4 | Human factors | Comprehension, appropriate reliance, actionability |
| 5 | Controlled pilot | Safety, workflow fit, and patient-relevant endpoints |

No gate can be skipped based on the synthetic metrics in this repository.

## Failure modes to test

Sensor dropouts, compression artifacts, meal-related spikes, steroid use, acute infection, pregnancy, renal impairment, medication changes, extreme diets, manual-entry errors, duplicate events, stale EHR data, and distribution shift.
