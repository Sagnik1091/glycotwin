# Datasheet — synthetic GlycoTwin cohort

## Motivation

The dataset exists solely to demonstrate model training, evaluation, inference, and deployment without collecting or exposing personal health information.

## Composition

6,000 rows generated at training time with 12 numeric features. There are no names, contact details, identifiers, free text, dates, device IDs, or real patient records.

## Generation

`synthetic_cohort()` uses seeded NumPy distributions with bounded ranges. A noisy logistic function creates a binary seven-day deterioration label. The code—not a static hidden dataset—is the source of truth, making generation reproducible and auditable.

## Recommended uses

Software tests, API demonstrations, UI evaluation, architecture reviews, and hackathon judging.

## Non-recommended uses

Clinical research conclusions, epidemiology, prevalence estimation, patient care, benchmarking real models, fairness claims, or deployment.

## Bias and representativeness

The cohort is not representative of India or any subpopulation. Correlations are authored for demonstration, and omitted variables are substantial. Synthetic data avoids privacy harm but does not avoid modeling bias.

## Maintenance

Generation is deterministic at seed 42. Any change to distributions, labels, features, or seed should be versioned and accompanied by regenerated metrics and model artifacts.
