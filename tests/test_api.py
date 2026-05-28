from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_TEXT = (
    "My heart rate is 125, blood pressure is 150/95, "
    "I feel anxious and I cannot sleep."
)

MODERATE_SAMPLE = "My heart rate is 100, I can not sleep, I am unhappy."
BP_200_SAMPLE = "My blood pressure is 200."
BP_ANXIOUS_SAMPLE = "BP 145/95 and I feel anxious."
BP_HIGH_QUALITATIVE = "My blood pressure is high."


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "healthlens-llm"}
    assert "OPENAI" not in response.text


def test_version_endpoint_default_values():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "healthlens-llm"
    assert "version" in data
    assert "environment" in data
    assert "extractor_provider" in data
    assert "llm_provider" in data
    assert "OPENAI_API_KEY" not in response.text


def test_serve_frontend():
    response = client.get("/")
    assert response.status_code == 200
    assert "HealthLens-LLM" in response.text


def test_analyse_returns_200():
    response = client.post("/analyse", json={"text": SAMPLE_TEXT})
    assert response.status_code == 200


def test_analyse_response_structure():
    response = client.post("/analyse", json={"text": SAMPLE_TEXT})
    data = response.json()

    assert "structured_input" in data
    assert "risk_result" in data
    assert "explanation" in data
    assert "safety_check" in data
    assert "extractor_provider" in data
    assert "llm_provider" in data
    assert "extraction_evidence" in data["structured_input"]

    assert data["structured_input"]["heart_rate"] == 125
    assert data["structured_input"]["systolic_bp"] == 150
    assert data["structured_input"]["diastolic_bp"] == 95
    assert data["risk_result"]["risk_level"] in ("low", "moderate", "high")
    assert data["safety_check"]["passed"] is True


def test_moderate_sample_end_to_end():
    response = client.post("/analyse", json={"text": MODERATE_SAMPLE})
    data = response.json()

    assert data["structured_input"]["heart_rate"] == 100
    assert data["structured_input"]["sleep_quality"] == "poor"
    assert data["structured_input"]["mood"] == "low"
    assert "diastolic_bp" not in data["structured_input"]["missing_or_ambiguous_fields"]
    assert data["risk_result"]["risk_level"] == "moderate"
    assert "borderline_heart_rate" in data["risk_result"]["flags"]
    assert "low_mood_flag" in data["risk_result"]["flags"]
    assert "poor_sleep" in data["risk_result"]["flags"]
    assert "incomplete_measurement" not in data["risk_result"]["flags"]


def test_bp_200_returns_high_risk_with_mock_extractor():
    response = client.post("/analyse", json={"text": BP_200_SAMPLE})
    data = response.json()

    assert data["structured_input"]["systolic_bp"] == 200
    assert data["structured_input"]["diastolic_bp"] is None
    assert "diastolic_bp" in data["structured_input"]["missing_or_ambiguous_fields"]
    assert data["risk_result"]["risk_level"] == "high"
    assert "very_high_systolic_bp" in data["risk_result"]["flags"]
    assert "incomplete_measurement" in data["risk_result"]["flags"]


def test_bp_and_anxious_end_to_end():
    response = client.post("/analyse", json={"text": BP_ANXIOUS_SAMPLE})
    data = response.json()

    assert data["structured_input"]["systolic_bp"] == 145
    assert data["structured_input"]["diastolic_bp"] == 95
    assert data["structured_input"]["mood"] == "anxious"


def test_qualitative_bp_does_not_invent_numbers():
    response = client.post("/analyse", json={"text": BP_HIGH_QUALITATIVE})
    data = response.json()

    assert data["structured_input"]["systolic_bp"] is None
    assert data["structured_input"]["diastolic_bp"] is None
    assert "blood_pressure" in data["structured_input"]["missing_or_ambiguous_fields"]
