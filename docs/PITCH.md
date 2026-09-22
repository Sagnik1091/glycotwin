# Three-minute judging pitch

## 0:00–0:25 — Problem

Diabetes care is often reactive. HbA1c is infrequent, wearable streams are noisy, and lifestyle context is fragmented. By the time deterioration is visible at a visit, an opportunity for earlier support may have passed.

## 0:25–0:50 — Focus

GlycoTwin is a narrow, inspectable Digital Twin for Type 2 Diabetes. It predicts one outcome: the seven-day risk that mean glucose will remain above 180 mg/dL.

## 0:50–1:30 — Demo

Change HbA1c, recent glucose, steps, and sleep; synchronise the twin; show the risk and plain-language drivers. Then move the scenario sliders to compare the baseline and counterfactual 14-day trajectories. Emphasize that this is exploration—not a prescription.

## 1:30–2:05 — Technology

The virtual patient fuses EHR, wearable, and lifestyle features. An auditable regularized logistic model is blended with a physiology-inspired guardrail. New CGM readings update the twin through a streaming endpoint. FastAPI provides versioned, documented APIs, and every input is bounded.

## 2:05–2:35 — Responsible innovation

The entire PoC uses reproducible synthetic data. We make no clinical claim. The repository contains a model card, datasheet, validation gates, failure modes, privacy controls, and explicit prohibited uses.

## 2:35–3:00 — Path forward

Next: validate on consented, de-identified Indian cohorts; test calibration and subgroups; add FHIR and wearable adapters; then run a silent prospective study before any clinical pilot. GlycoTwin shows the foundation of proactive care while keeping humans and evidence in control.
