from app.risk_rules import evaluate_risk
from app.schemas import StructuredHealthInput

MODERATE_TEXT = "My heart rate is 100, I can not sleep, I am unhappy."
BP_200_TEXT = "My blood pressure is 200."


def test_elevated_heart_rate_flag():
    inp = StructuredHealthInput(heart_rate=110)
    result = evaluate_risk(inp)
    assert "elevated_heart_rate" in result.flags
    assert result.risk_level == "moderate"


def test_elevated_blood_pressure_flag():
    inp = StructuredHealthInput(systolic_bp=145, diastolic_bp=95)
    result = evaluate_risk(inp)
    assert "elevated_blood_pressure" in result.flags
    assert result.risk_level == "moderate"


def test_single_systolic_bp_200_is_high_risk():
    inp = StructuredHealthInput(
        systolic_bp=200,
        diastolic_bp=None,
        missing_or_ambiguous_fields=["diastolic_bp"],
    )
    result = evaluate_risk(inp, BP_200_TEXT)

    assert result.risk_level == "high"
    assert "very_high_systolic_bp" in result.flags
    assert "incomplete_measurement" in result.flags


def test_borderline_heart_rate_only_is_low_risk():
    inp = StructuredHealthInput(heart_rate=100)
    result = evaluate_risk(inp)
    assert result.flags == ["borderline_heart_rate"]
    assert result.risk_level == "low"


def test_moderate_sample_risk():
    inp = StructuredHealthInput(heart_rate=100, mood="low", sleep_quality="poor")
    result = evaluate_risk(inp, MODERATE_TEXT)
    assert "borderline_heart_rate" in result.flags
    assert "low_mood_flag" in result.flags
    assert "poor_sleep" in result.flags
    assert "incomplete_measurement" not in result.flags
    assert result.risk_level == "moderate"


def test_high_risk_sample():
    inp = StructuredHealthInput(
        heart_rate=125,
        systolic_bp=150,
        diastolic_bp=95,
        mood="anxious",
        sleep_quality="poor",
    )
    result = evaluate_risk(inp)
    assert result.risk_level == "high"
    assert "very_elevated_heart_rate" in result.flags
    assert "elevated_blood_pressure" in result.flags
    assert "anxiety_or_stress_flag" in result.flags
    assert "poor_sleep" in result.flags


def test_no_flags_low_risk():
    inp = StructuredHealthInput(heart_rate=72, mood="calm", sleep_quality="good")
    result = evaluate_risk(inp)
    assert result.flags == []
    assert result.risk_level == "low"
