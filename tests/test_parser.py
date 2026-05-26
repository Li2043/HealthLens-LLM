from app.parser import parse_health_text


def test_extracts_heart_rate():
    text = "My heart rate is 110 and I feel fine."
    result = parse_health_text(text)
    assert result.heart_rate == 110


def test_extracts_single_blood_pressure():
    text = "My blood pressure is 200"
    result = parse_health_text(text)
    assert result.systolic_bp == 200
    assert result.diastolic_bp is None
    assert "diastolic_bp" in result.missing_or_ambiguous_fields


def test_extracts_blood_pressure_slash():
    text = "blood pressure is 145/95"
    result = parse_health_text(text)
    assert result.systolic_bp == 145
    assert result.diastolic_bp == 95


def test_detects_anxious_mood():
    text = "I feel anxious about work."
    result = parse_health_text(text)
    assert result.mood == "anxious"


def test_detects_poor_sleep():
    text = "I slept badly last night."
    result = parse_health_text(text)
    assert result.sleep_quality == "poor"


def test_moderate_sample_parses_all_fields():
    text = "My heart rate is 100, I can not sleep, I am unhappy"
    result = parse_health_text(text)
    assert result.heart_rate == 100
    assert result.sleep_quality == "poor"
    assert result.mood == "low"
