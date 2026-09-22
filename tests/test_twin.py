import pytest

from twin.core import Intervention, PatientState, simulate, update_from_stream
from twin.model import predict_risk, synthetic_cohort


def test_risk_is_probability():
    score, model = predict_risk(PatientState())
    assert 0 <= score <= 1
    assert model in {"hybrid-ml-physiology", "physiology-fallback"}


def test_positive_habit_intervention_lowers_glucose():
    state = PatientState()
    base = simulate(state, Intervention(), 14)
    improved = simulate(state, Intervention(steps_delta=3000, sleep_delta=1, carbs_delta=-50,
                                             adherence_delta=0.1), 14)
    assert improved[-1]["predicted_avg_glucose"] < base[-1]["predicted_avg_glucose"]


def test_stream_updates_twin():
    state = PatientState(avg_glucose_7d=150)
    updated = update_from_stream(state, [180, 190, 200, 170])
    assert updated.avg_glucose_7d > state.avg_glucose_7d


def test_invalid_stream_rejected():
    with pytest.raises(ValueError):
        update_from_stream(PatientState(), [10, 20])


def test_synthetic_cohort_reproducible():
    x1, y1 = synthetic_cohort(100, seed=7)
    x2, y2 = synthetic_cohort(100, seed=7)
    assert (x1 == x2).all() and (y1 == y2).all()
