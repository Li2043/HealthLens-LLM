from app.safety_validator import validate_llm_output


def test_passes_safe_output():
    text = (
        "Your signals suggest elevated readings. "
        "Please consult a professional if concerned. "
        "This is not a medical diagnosis."
    )
    result = validate_llm_output(text)
    assert result.contains_disclaimer is True
    assert result.contains_diagnostic_language is False
    assert result.contains_medication_advice is False
    assert result.passed is True


def test_fails_diagnostic_language():
    text = "You have hypertension. This is not a medical diagnosis."
    result = validate_llm_output(text)
    assert result.contains_diagnostic_language is True
    assert result.passed is False


def test_fails_medication_advice():
    text = "You should take medication. This is not a medical diagnosis."
    result = validate_llm_output(text)
    assert result.contains_medication_advice is True
    assert result.passed is False


def test_fails_without_disclaimer():
    text = "Your readings look elevated. Please consult a doctor."
    result = validate_llm_output(text)
    assert result.contains_disclaimer is False
    assert result.passed is False
