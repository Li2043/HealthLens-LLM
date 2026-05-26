from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_TEXT = (
    "My heart rate is 125, blood pressure is 150/95, "
    "I feel anxious and I cannot sleep."
)

MODERATE_SAMPLE = "My heart rate is 100, I can not sleep, I am unhappy."
BP_200_SAMPLE = "My blood pressure is 200"


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

    assert data["structured_input"]["heart_rate"] == 125
    assert data["structured_input"]["systolic_bp"] == 150
    assert data["structured_input"]["diastolic_bp"] == 95
    assert data["risk_result"]["risk_level"] in ("low", "moderate", "high")
    assert "rule_explanation" in data["risk_result"]
    assert data["safety_check"]["passed"] is True
    assert data["extractor_provider"] == "mock"
    assert data["llm_provider"] == "mock"


def test_moderate_sample_end_to_end():
    response = client.post("/analyse", json={"text": MODERATE_SAMPLE})
    data = response.json()

    assert data["structured_input"]["heart_rate"] == 100
    assert data["structured_input"]["sleep_quality"] == "poor"
    assert data["structured_input"]["mood"] == "low"
    assert data["risk_result"]["risk_level"] == "moderate"
    assert "borderline_heart_rate" in data["risk_result"]["flags"]
    assert "low_mood_flag" in data["risk_result"]["flags"]
    assert "poor_sleep" in data["risk_result"]["flags"]


def test_bp_200_returns_high_risk_with_mock_extractor():
    response = client.post("/analyse", json={"text": BP_200_SAMPLE})
    data = response.json()

    assert data["structured_input"]["systolic_bp"] == 200
    assert data["structured_input"]["diastolic_bp"] is None
    assert "diastolic_bp" in data["structured_input"]["missing_or_ambiguous_fields"]
    assert data["risk_result"]["risk_level"] == "high"
    assert "very_high_systolic_bp" in data["risk_result"]["flags"]
    assert "incomplete_measurement" in data["risk_result"]["flags"]
