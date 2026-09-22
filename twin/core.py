"""Personalized, explainable glycaemic Digital Twin engine.

This is a research PoC, not a medical device. The simulator combines a compact
physiology-inspired state transition with an ML risk model trained on synthetic data.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp
from typing import Iterable

import numpy as np


@dataclass
class PatientState:
    age: int = 48
    bmi: float = 28.5
    hba1c: float = 7.6
    fasting_glucose: float = 142.0
    avg_glucose_7d: float = 158.0
    glucose_variability: float = 34.0
    resting_hr: float = 76.0
    steps_day: int = 5200
    sleep_hours: float = 6.4
    carbs_g_day: float = 235.0
    medication_adherence: float = 0.78
    systolic_bp: float = 132.0

    def validate(self) -> None:
        bounds = {
            "age": (18, 90), "bmi": (14, 60), "hba1c": (4, 18),
            "fasting_glucose": (50, 500), "avg_glucose_7d": (50, 500),
            "glucose_variability": (1, 150), "resting_hr": (35, 180),
            "steps_day": (0, 50000), "sleep_hours": (0, 16),
            "carbs_g_day": (20, 800), "medication_adherence": (0, 1),
            "systolic_bp": (70, 250),
        }
        for name, (lo, hi) in bounds.items():
            value = getattr(self, name)
            if not lo <= value <= hi:
                raise ValueError(f"{name} must be between {lo} and {hi}")


@dataclass
class Intervention:
    steps_delta: int = 0
    sleep_delta: float = 0.0
    carbs_delta: float = 0.0
    adherence_delta: float = 0.0


FEATURES = list(PatientState.__dataclass_fields__)


def feature_vector(state: PatientState) -> np.ndarray:
    return np.array([getattr(state, key) for key in FEATURES], dtype=float)


def physiology_risk(state: PatientState) -> float:
    """Transparent baseline risk based on clinically plausible directional effects."""
    z = (
        -2.4
        + 0.95 * (state.hba1c - 7.0)
        + 0.018 * (state.avg_glucose_7d - 140)
        + 0.012 * (state.glucose_variability - 30)
        + 0.045 * (state.bmi - 25)
        + 0.003 * (state.carbs_g_day - 200)
        - 0.00011 * (state.steps_day - 5000)
        - 0.22 * (state.sleep_hours - 7)
        - 1.1 * (state.medication_adherence - 0.7)
    )
    return 1.0 / (1.0 + exp(-z))


def simulate(state: PatientState, intervention: Intervention, days: int = 14) -> list[dict]:
    """Run a deterministic counterfactual trajectory from an intervention."""
    state.validate()
    days = max(1, min(days, 30))
    glucose = state.avg_glucose_7d
    adherence = float(np.clip(state.medication_adherence + intervention.adherence_delta, 0, 1))
    steps = max(0, state.steps_day + intervention.steps_delta)
    sleep = float(np.clip(state.sleep_hours + intervention.sleep_delta, 0, 16))
    carbs = max(20, state.carbs_g_day + intervention.carbs_delta)
    results: list[dict] = []
    for day in range(1, days + 1):
        target = (
            state.avg_glucose_7d
            + 0.095 * (carbs - state.carbs_g_day)
            - 0.00115 * (steps - state.steps_day)
            - 3.1 * (sleep - state.sleep_hours)
            - 24.0 * (adherence - state.medication_adherence)
        )
        glucose += 0.32 * (target - glucose)
        circadian = 2.2 * np.sin(day * 1.7)
        predicted = float(np.clip(glucose + circadian, 60, 350))
        results.append({"day": day, "predicted_avg_glucose": round(predicted, 1)})
    return results


def explain(state: PatientState) -> list[dict]:
    """Return directional, user-readable drivers; not causal attributions."""
    drivers = [
        ("HbA1c", max(0.0, (state.hba1c - 7) * 0.95), "higher long-term glucose"),
        ("7-day glucose", max(0.0, (state.avg_glucose_7d - 140) * 0.018), "recent glucose burden"),
        ("variability", max(0.0, (state.glucose_variability - 30) * 0.012), "unstable glucose"),
        ("physical activity", max(0.0, (5000 - state.steps_day) * 0.00011), "low daily movement"),
        ("sleep", max(0.0, (7 - state.sleep_hours) * 0.22), "short sleep"),
        ("medication adherence", max(0.0, (0.7 - state.medication_adherence) * 1.1), "missed doses"),
        ("carbohydrate load", max(0.0, (state.carbs_g_day - 200) * 0.003), "high estimated intake"),
    ]
    return [
        {"feature": name, "impact": round(score, 3), "reason": reason}
        for name, score, reason in sorted(drivers, key=lambda x: x[1], reverse=True)[:5]
    ]


def update_from_stream(state: PatientState, readings: Iterable[float]) -> PatientState:
    """Assimilate a batch of CGM-like readings into the virtual patient state."""
    values = np.asarray(list(readings), dtype=float)
    if not len(values) or np.any((values < 30) | (values > 600)):
        raise ValueError("readings must contain plausible glucose values (30–600 mg/dL)")
    payload = asdict(state)
    payload["avg_glucose_7d"] = round(0.65 * state.avg_glucose_7d + 0.35 * float(values.mean()), 1)
    payload["glucose_variability"] = round(0.65 * state.glucose_variability + 0.35 * float(values.std()), 1)
    payload["fasting_glucose"] = round(0.75 * state.fasting_glucose + 0.25 * float(values[-1]), 1)
    return PatientState(**payload)
