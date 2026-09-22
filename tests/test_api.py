from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_risk_endpoint():
    response = client.post("/api/v1/risk", json={})
    assert response.status_code == 200
    assert 0 <= response.json()["risk"] <= 1
    assert len(response.json()["drivers"]) > 0


def test_simulation_endpoint():
    response = client.post("/api/v1/simulate", json={"patient": {}, "days": 7})
    assert response.status_code == 200
    assert len(response.json()["baseline"]) == 7


def test_validation():
    response = client.post("/api/v1/risk", json={"hba1c": 50})
    assert response.status_code == 422
