"""Validate LLM output for safety compliance."""

from app.schemas import SafetyCheck

DISCLAIMER_PHRASE = "not a medical diagnosis"

DIAGNOSTIC_PHRASES = [
    "you have hypertension",
    "you have heart disease",
    "you are diagnosed with",
]

MEDICATION_PHRASES = [
    "take medication",
    "you should take medicine",
    "you should take medication",
]


def validate_llm_output(text: str) -> SafetyCheck:
    """Check that LLM explanation is safe and includes required disclaimer."""
    lower = text.lower()
    contains_disclaimer = DISCLAIMER_PHRASE in lower
    contains_diagnostic_language = any(phrase in lower for phrase in DIAGNOSTIC_PHRASES)
    contains_medication_advice = any(phrase in lower for phrase in MEDICATION_PHRASES)
    passed = (
        contains_disclaimer
        and not contains_diagnostic_language
        and not contains_medication_advice
    )

    return SafetyCheck(
        contains_disclaimer=contains_disclaimer,
        contains_diagnostic_language=contains_diagnostic_language,
        contains_medication_advice=contains_medication_advice,
        passed=passed,
    )
