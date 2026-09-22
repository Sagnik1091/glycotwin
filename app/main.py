"""FastAPI service for GlycoTwin."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from twin import Intervention, PatientState, explain, predict_risk, simulate, update_from_stream

BASE = Path(__file__).resolve().parent
app = FastAPI(
    title="GlycoTwin API",
    version="1.0.0",
    description="Research PoC for seven-day glycaemic deterioration risk and counterfactual simulation.",
)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


class PatientInput(BaseModel):
    age: Annotated[int, Field(ge=18, le=90)] = 48
    bmi: Annotated[float, Field(ge=14, le=60)] = 28.5
    hba1c: Annotated[float, Field(ge=4, le=18)] = 7.6
    fasting_glucose: Annotated[float, Field(ge=50, le=500)] = 142
    avg_glucose_7d: Annotated[float, Field(ge=50, le=500)] = 158
    glucose_variability: Annotated[float, Field(ge=1, le=150)] = 34
    resting_hr: Annotated[float, Field(ge=35, le=180)] = 76
    steps_day: Annotated[int, Field(ge=0, le=50000)] = 5200
    sleep_hours: Annotated[float, Field(ge=0, le=16)] = 6.4
    carbs_g_day: Annotated[float, Field(ge=20, le=800)] = 235
    medication_adherence: Annotated[float, Field(ge=0, le=1)] = 0.78
    systolic_bp: Annotated[float, Field(ge=70, le=250)] = 132


class InterventionInput(BaseModel):
    steps_delta: Annotated[int, Field(ge=-20000, le=30000)] = 2500
    sleep_delta: Annotated[float, Field(ge=-8, le=8)] = 0.75
    carbs_delta: Annotated[float, Field(ge=-500, le=500)] = -45
    adherence_delta: Annotated[float, Field(ge=-1, le=1)] = 0.1


class SimulationRequest(BaseModel):
    patient: PatientInput
    intervention: InterventionInput = InterventionInput()
    days: Annotated[int, Field(ge=1, le=30)] = 14


class StreamRequest(BaseModel):
    patient: PatientInput
    glucose_readings: Annotated[list[float], Field(min_length=1, max_length=288)]


def risk_band(risk: float) -> str:
    return "high" if risk >= 0.65 else "moderate" if risk >= 0.35 else "low"


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE / "static" / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "glycotwin", "version": "1.0.0"}


@app.post("/api/v1/risk")
def risk(patient: PatientInput) -> dict:
    state = PatientState(**patient.model_dump())
    score, model = predict_risk(state)
    return {"risk": score, "risk_percent": round(score * 100, 1), "band": risk_band(score),
            "model": model, "horizon_days": 7, "outcome": "sustained_mean_glucose_above_180",
            "drivers": explain(state), "disclaimer": "Research prototype; not medical advice."}


@app.post("/api/v1/simulate")
def run_simulation(request: SimulationRequest) -> dict:
    state = PatientState(**request.patient.model_dump())
    intervention = Intervention(**request.intervention.model_dump())
    baseline = simulate(state, Intervention(), request.days)
    counterfactual = simulate(state, intervention, request.days)
    delta = counterfactual[-1]["predicted_avg_glucose"] - baseline[-1]["predicted_avg_glucose"]
    return {"baseline": baseline, "counterfactual": counterfactual,
            "estimated_day_end_delta_mg_dl": round(delta, 1),
            "assumptions": ["Daily habits remain constant", "No acute illness or medication change",
                            "Simulation is directional and is not a treatment recommendation"]}


@app.post("/api/v1/stream")
def stream(request: StreamRequest) -> dict:
    try:
        updated = update_from_stream(PatientState(**request.patient.model_dump()), request.glucose_readings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    score, model = predict_risk(updated)
    return {"updated_twin": asdict(updated), "risk": score, "band": risk_band(score), "model": model}
