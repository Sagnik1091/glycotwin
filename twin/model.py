"""Small auditable ML model implemented with NumPy for reproducibility."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from twin.core import FEATURES, PatientState, feature_vector, physiology_risk

MODEL_PATH = Path(__file__).resolve().parent.parent / "artifacts" / "risk_model.json"


def synthetic_cohort(n: int = 6000, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Generate a reproducible, non-identifiable cohort for PoC development only."""
    rng = np.random.default_rng(seed)
    X = np.column_stack([
        rng.integers(20, 81, n), rng.normal(27.5, 5.1, n).clip(15, 55),
        rng.normal(7.2, 1.5, n).clip(4.2, 15), rng.normal(135, 42, n).clip(60, 400),
        rng.normal(150, 45, n).clip(60, 400), rng.normal(32, 14, n).clip(3, 120),
        rng.normal(75, 12, n).clip(40, 150), rng.lognormal(8.5, 0.55, n).clip(200, 25000),
        rng.normal(6.8, 1.2, n).clip(2, 12), rng.normal(220, 65, n).clip(40, 600),
        rng.beta(7, 2.2, n), rng.normal(130, 18, n).clip(85, 220),
    ])
    logits = (-3.2 + 0.8 * (X[:, 2] - 7) + 0.018 * (X[:, 4] - 140)
              + 0.012 * (X[:, 5] - 30) + 0.035 * (X[:, 1] - 25)
              - 0.00009 * (X[:, 7] - 5000) - 0.2 * (X[:, 8] - 7)
              + 0.0025 * (X[:, 9] - 200) - 0.9 * (X[:, 10] - 0.7)
              + rng.normal(0, 0.75, n))
    probability = 1 / (1 + np.exp(-logits))
    return X.astype(float), rng.binomial(1, probability)


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def _auc(y: np.ndarray, scores: np.ndarray) -> float:
    """ROC-AUC via rank sum, with no third-party metrics dependency."""
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)
    positives = y == 1
    n_pos, n_neg = positives.sum(), (~positives).sum()
    return float((ranks[positives].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def train_model(path: Path = MODEL_PATH) -> dict:
    X, y = synthetic_cohort()
    rng = np.random.default_rng(42)
    indices = rng.permutation(len(y))
    split = int(0.75 * len(y))
    train, test = indices[:split], indices[split:]
    mean, scale = X[train].mean(0), X[train].std(0)
    X_train = (X[train] - mean) / scale
    weights, bias = np.zeros(X.shape[1]), 0.0
    for _ in range(1200):
        pred = _sigmoid(X_train @ weights + bias)
        error = pred - y[train]
        weights -= 0.08 * ((X_train.T @ error) / len(train) + 0.002 * weights)
        bias -= 0.08 * float(error.mean())
    test_pred = _sigmoid(((X[test] - mean) / scale) @ weights + bias)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"features": FEATURES, "mean": mean.tolist(), "scale": scale.tolist(),
                                "weights": weights.tolist(), "bias": bias}, indent=2) + "\n")
    return {"roc_auc": round(_auc(y[test], test_pred), 3),
            "brier_score": round(float(np.mean((test_pred - y[test]) ** 2)), 3),
            "test_samples": len(test), "positive_rate": round(float(y[test].mean()), 3)}


def predict_risk(state: PatientState) -> tuple[float, str]:
    state.validate()
    if MODEL_PATH.exists():
        bundle = json.loads(MODEL_PATH.read_text())
        values = feature_vector(state)
        z = ((values - np.array(bundle["mean"])) / np.array(bundle["scale"])) @ np.array(bundle["weights"])
        ml = float(_sigmoid(np.array([z + bundle["bias"]]))[0])
        return round(0.65 * ml + 0.35 * physiology_risk(state), 4), "hybrid-ml-physiology"
    return round(physiology_risk(state), 4), "physiology-fallback"
