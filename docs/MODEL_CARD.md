# Model Card — GlycoTwin risk forecaster

## Intended use

Research demonstration of an end-to-end Digital Twin pipeline for adults with Type 2 Diabetes. It estimates the probability of sustained mean glucose above 180 mg/dL within seven days.

## Prohibited use

Diagnosis, emergency detection, insulin dosing, medication changes, autonomous care decisions, insurance/employment decisions, or use on real patients without governance and clinical validation.

## Inputs

Age, BMI, HbA1c, fasting glucose, seven-day mean glucose, glucose variability, resting heart rate, steps, sleep, estimated carbohydrates, medication adherence, and systolic blood pressure.

## Model

A compact L2-regularized logistic regression, trained with auditable NumPy gradient descent on 6,000 reproducibly generated synthetic records. At inference, 65% of the ML probability is blended with 35% of a transparent physiology-inspired score. If the model artifact is unavailable, the transparent score is returned and labeled `physiology-fallback`.

## Evaluation

The train script uses a stratified 75/25 split with seed 42 and reports ROC-AUC and Brier score. These numbers assess whether the implementation recovers its synthetic data-generating process. They are **not evidence of clinical utility or generalization**.

## Explainability

The UI reports top directional drivers from explicit feature rules. These are associations and not causal explanations. The counterfactual simulator is kept separate from risk-driver display.

## Key limitations

- Synthetic cohort has no real-world missingness, device artifacts, care pathways, or population shift.
- No subgroup fairness claim; sex, geography, socioeconomic context, diet patterns, comorbidities, and medication class are absent.
- Self-reported adherence and carbohydrates are noisy in practice.
- The outcome is a surrogate rather than a clinical event.
- Counterfactual coefficients are illustrative, not estimated individual treatment effects.
- Input values outside validated ranges are rejected, but in-range combinations can still be unusual.

## Validation required before real use

Retrospective external validation, temporal validation, calibration, decision-curve analysis, subgroup evaluation, clinician usability studies, silent prospective evaluation, and a pre-specified safety analysis.
