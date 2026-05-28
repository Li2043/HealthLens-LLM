"""Tests for the Evaluation Lab API and runner."""

from fastapi.testclient import TestClient

from app.evaluation.runner import run_evaluation_suite
from app.main import app

client = TestClient(app)


def test_get_evaluation_cases_returns_cases():
    response = client.get("/evaluation/cases")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8
    assert data[0]["id"]
    assert "expected_risk_level" in data[0]
    assert "expected_signals" in data[0]


def test_post_evaluation_run_returns_summary():
    response = client.post("/evaluation/run?provider=mock")
    assert response.status_code == 200
    data = response.json()

    assert data["suite"] == "healthlens-eval-v1"
    assert data["provider"] == "mock"
    assert "summary" in data
    assert "results" in data
    assert data["summary"]["total_cases"] >= 8
    assert "pass_rate" in data["summary"]
    assert "safety_pass_rate" in data["summary"]
    assert "risk_match_rate" in data["summary"]
    assert "average_latency_ms" in data["summary"]


def test_evaluation_run_does_not_require_openai():
    response = client.post("/evaluation/run")
    assert response.status_code == 200
    assert response.json()["provider"] == "mock"


def test_evaluation_results_include_risk_and_trace():
    response = client.post("/evaluation/run?provider=mock")
    results = response.json()["results"]
    assert results
    first = results[0]
    assert "expected_risk_level" in first
    assert "actual_risk_level" in first or first.get("error_code")
    assert "workflow_trace" in first
    assert len(first["workflow_trace"]) >= 1


def test_evaluation_runner_unit_pass_rate():
    report = run_evaluation_suite(provider="mock")
    assert report.summary.total_cases >= 8
    assert 0.0 <= report.summary.pass_rate <= 1.0
    assert report.summary.safety_pass_rate >= 0.0


def test_evaluation_openai_provider_requires_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/evaluation/run?provider=openai")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_PROVIDER"
