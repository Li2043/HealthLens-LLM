from app.extractor import MockLLMExtractor


def test_mock_extracts_single_blood_pressure():
    extractor = MockLLMExtractor()
    result = extractor.extract("My blood pressure is 200")

    assert result.systolic_bp == 200
    assert result.diastolic_bp is None
    assert "diastolic_bp" in result.missing_or_ambiguous_fields
    assert result.extraction_confidence == "medium"
    assert result.extraction_notes is not None


def test_mock_extracts_moderate_sample():
    extractor = MockLLMExtractor()
    result = extractor.extract("My heart rate is 100, I can not sleep, I am unhappy")

    assert result.heart_rate == 100
    assert result.mood == "low"
    assert result.sleep_quality == "poor"
    assert result.extraction_confidence == "high"
    assert result.missing_or_ambiguous_fields == []


def test_mock_extracts_high_sample():
    extractor = MockLLMExtractor()
    text = (
        "My heart rate is 125, blood pressure is 150/95, "
        "I feel anxious and I cannot sleep"
    )
    result = extractor.extract(text)

    assert result.heart_rate == 125
    assert result.systolic_bp == 150
    assert result.diastolic_bp == 95
    assert result.mood == "anxious"
    assert result.sleep_quality == "poor"
