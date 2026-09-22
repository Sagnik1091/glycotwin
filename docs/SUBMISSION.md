# Submission checklist

Replace all bracketed placeholders before submitting.

## Entry details

- **Project:** GlycoTwin
- **Team:** [TEAM NAME]
- **University / incubator:** [INSTITUTION]
- **Members (1–4):** [NAMES]
- **Primary contact:** [EMAIL / PHONE]
- **GitHub repository:** [PUBLIC GITHUB URL]
- **Live demo (optional):** [DEPLOYMENT URL]
- **Demo video (optional):** [VIDEO URL]

## Problem and outcome

Type 2 Diabetes; seven-day risk of sustained mean glucose above 180 mg/dL.

## Included deliverables

- [x] Working browser-based PoC
- [x] Versioned API and interactive OpenAPI documentation
- [x] Reproducible synthetic data and training code
- [x] Saved model metrics
- [x] Unit and API tests
- [x] Dockerfile and CI workflow
- [x] Architecture documentation
- [x] Model card and dataset datasheet
- [x] Validation and responsible-use plan
- [x] Three-minute pitch script
- [ ] Team details completed
- [ ] Screenshot/demo video added
- [ ] Public repository tested from a fresh clone
- [ ] Final Unstop submission completed before the displayed deadline

## Final pre-submission commands

```bash
python -m pip install -e '.[dev]'
python scripts/train.py
pytest -q
ruff check .
docker build -t glycotwin .
```
