from app.extraction_validator import validate_extraction
from app.extractor import MockLLMExtractor
from app.schemas import StructuredHealthInput


def test_moderate_sample_does_not_mark_missing_bp():
    extractor = MockLLMExtractor()
    text = "My heart rate is 100, I can not sleep, I am unhappy."
    result = extractor.extract(text)

    assert result.heart_rate == 100
    assert result.mood == "low"
    assert result.sleep_quality == "poor"
    assert result.systolic_bp is None
    assert result.diastolic_bp is None
    assert "diastolic_bp" not in result.missing_or_ambiguous_fields
    assert result.missing_or_ambiguous_fields == []
    assert result.extraction_evidence


def test_single_blood_pressure_marks_missing_diastolic():
    extractor = MockLLMExtractor()
    result = extractor.extract("My blood pressure is 200.")

    assert result.systolic_bp == 200
    assert result.diastolic_bp is None
    assert "diastolic_bp" in result.missing_or_ambiguous_fields
    assert any(item.field == "systolic_bp" and item.status == "partial" for item in result.extraction_evidence)


def test_bp_slash_and_anxious_mood():
    extractor = MockLLMExtractor()
    result = extractor.extract("BP 145/95 and I feel anxious")

    assert result.systolic_bp == 145
    assert result.diastolic_bp == 95
    assert result.mood == "anxious"
    assert result.missing_or_ambiguous_fields == []


def test_qualitative_blood_pressure_does_not_invent_numbers():
    extractor = MockLLMExtractor()
    result = extractor.extract("My blood pressure is high.")

    assert result.systolic_bp is None
    assert result.diastolic_bp is None
    assert "blood_pressure" in result.missing_or_ambiguous_fields
    assert any(item.status == "ambiguous" for item in result.extraction_evidence if item.field == "systolic_bp")


def test_validator_removes_false_missing_bp_from_llm_output():
    raw = StructuredHealthInput(
        heart_rate=100,
        mood="low",
        sleep_quality="poor",
        missing_or_ambiguous_fields=["diastolic_bp"],
        extraction_confidence="high",
    )
    text = "My heart rate is 100, I can not sleep, I am unhappy."
    result = validate_extraction(text, raw)

    assert "diastolic_bp" not in result.missing_or_ambiguous_fields
    assert result.systolic_bp is None
    assert result.diastolic_bp is None
