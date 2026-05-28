import time

from fastapi.testclient import TestClient

from app.errors import AnalysisPipelineError, ProviderConfigurationError
from app.main import app

client = TestClient(app)

SAMPLE_TEXT = (
    "My heart rate is 125, blood pressure is 150/95, "
    "I feel anxious and I cannot sleep."
)


def test_version_endpoint_returns_safe_metadata(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-secret-key-must-not-leak")
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("EXTRACTOR_PROVIDER", "mock")
    monkeypatch.setenv("LLM_PROVIDER", "mock")

    import importlib

    import app.config
    import app.main

    importlib.reload(app.config)
    importlib.reload(app.main)

    version_client = TestClient(app.main.app)
    response = version_client.get("/version")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "healthlens-llm"
    assert data["version"] == "1.2.3"
    assert data["environment"] == "staging"
    assert data["extractor_provider"] == "mock"
    assert data["llm_provider"] == "mock"
    assert "OPENAI_API_KEY" not in response.text
    assert "sk-test-secret-key-must-not-leak" not in response.text


def test_analyse_empty_input_returns_400():
    response = client.post("/analyse", json={"text": ""})
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "EMPTY_INPUT"
    assert "health-related text" in data["error"]["message"]


def test_analyse_whitespace_only_input_returns_400():
    response = client.post("/analyse", json={"text": "   \n\t  "})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_INPUT"


def test_analyse_input_too_large_returns_413(monkeypatch):
    monkeypatch.setattr("app.config.MAX_INPUT_CHARS", 20)
    response = client.post("/analyse", json={"text": "x" * 21})
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "INPUT_TOO_LARGE"
    assert "too long" in data["error"]["message"]


def test_analyse_timeout_returns_504(monkeypatch):
    def slow_analysis(text: str, language: str = "en"):
        time.sleep(0.2)
        return {"should": "not reach"}

    monkeypatch.setattr("app.main.run_analysis", slow_analysis)
    monkeypatch.setattr("app.main.ANALYSE_TIMEOUT_SECONDS", 0.01)

    response = client.post("/analyse", json={"text": SAMPLE_TEXT})
    assert response.status_code == 504
    data = response.json()
    assert data["error"]["code"] == "ANALYSIS_TIMEOUT"
    assert "timed out" in data["error"]["message"]


def test_analyse_provider_exception_returns_controlled_error(monkeypatch):
    def failing_analysis(text: str, language: str = "en"):
        raise AnalysisPipelineError from RuntimeError("OpenAI secret sk-live-abc123 exploded")

    monkeypatch.setattr("app.main.run_analysis", failing_analysis)

    response = client.post("/analyse", json={"text": SAMPLE_TEXT})
    assert response.status_code == 503
    data = response.json()
    assert data["error"]["code"] == "ANALYSIS_FAILED"
    assert "sk-live-abc123" not in response.text
    assert "exploded" not in response.text


def test_analyse_provider_configuration_error(monkeypatch):
    def misconfigured_analysis(text: str, language: str = "en"):
        raise ProviderConfigurationError("OPENAI_API_KEY missing")

    monkeypatch.setattr("app.main.run_analysis", misconfigured_analysis)

    response = client.post("/analyse", json={"text": SAMPLE_TEXT})
    assert response.status_code == 503
    data = response.json()
    assert data["error"]["code"] == "PROVIDER_CONFIGURATION_ERROR"
    assert "OPENAI_API_KEY" not in response.text


def test_analyse_production_misconfiguration_returns_provider_error(monkeypatch):
    monkeypatch.setattr("app.main.APP_ENV", "production")
    monkeypatch.setattr("app.main.is_openai_provider_misconfigured", lambda: True)

    response = client.post("/analyse", json={"text": SAMPLE_TEXT})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "PROVIDER_CONFIGURATION_ERROR"
