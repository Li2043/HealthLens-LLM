"""Extensible LLM provider for explaining rule-based risk results."""

import os
import re
from abc import ABC, abstractmethod

from app.extraction_validator import blood_pressure_mentioned
from app.schemas import RiskResult, StructuredHealthInput

SYSTEM_PROMPT = """You explain rule-based health signal results. You must:
- NOT diagnose disease.
- NOT prescribe medication.
- ALWAYS state this is not a medical diagnosis.
- Recommend professional medical advice if symptoms are concerning, unusual, persistent, or worsening.
- Use simple, calm plain text only. Do NOT use Markdown formatting.
- Mention the detected rule-based flags in plain language.
- Do NOT mention missing blood pressure unless blood pressure was mentioned in the original user input.
- Base your explanation ONLY on the structured input and risk flags provided.
"""

_FLAG_PLAIN_LANGUAGE = {
    "very_high_systolic_bp": "very high systolic blood pressure",
    "very_high_diastolic_bp": "very high diastolic blood pressure",
    "elevated_blood_pressure": "elevated blood pressure",
    "elevated_heart_rate": "an elevated heart rate",
    "very_elevated_heart_rate": "a very elevated heart rate",
    "borderline_heart_rate": "a borderline heart rate",
    "anxiety_or_stress_flag": "signs of anxiety or stress",
    "low_mood_flag": "a low mood",
    "poor_sleep": "poor sleep quality",
    "incomplete_measurement": "incomplete or ambiguous measurements",
}


class LLMService(ABC):
    @abstractmethod
    def generate_explanation(
        self, structured: StructuredHealthInput, risk: RiskResult, source_text: str = ""
    ) -> str:
        pass

    def explain(self, structured: StructuredHealthInput, risk: RiskResult) -> str:
        """Backward-compatible alias."""
        return self.generate_explanation(structured, risk)


def _strip_markdown(text: str) -> str:
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)
    cleaned = re.sub(r"`(.*?)`", r"\1", cleaned)
    cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()


def _format_flags_plain(flags: list[str]) -> str:
    if not flags:
        return "no rule-based flags"
    descriptions = [_FLAG_PLAIN_LANGUAGE.get(flag, flag.replace("_", " ")) for flag in flags]
    if len(descriptions) == 1:
        return descriptions[0]
    return ", ".join(descriptions[:-1]) + f", and {descriptions[-1]}"


def _format_signals(structured: StructuredHealthInput, source_text: str) -> str:
    signals: list[str] = []
    if structured.heart_rate is not None:
        signals.append(f"heart rate of {structured.heart_rate} bpm")
    if blood_pressure_mentioned(source_text):
        if structured.systolic_bp is not None and structured.diastolic_bp is not None:
            signals.append(
                f"blood pressure of {structured.systolic_bp}/{structured.diastolic_bp}"
            )
        elif structured.systolic_bp is not None:
            signals.append(f"systolic blood pressure of {structured.systolic_bp}")
    if structured.mood:
        signals.append(f"mood described as {structured.mood}")
    if structured.sleep_quality:
        signals.append(f"sleep quality described as {structured.sleep_quality}")
    if structured.symptoms:
        signals.append(f"symptoms noted: {', '.join(structured.symptoms)}")
    return ", ".join(signals) if signals else "limited structured signals"


class MockLLMService(LLMService):
    """Deterministic mock provider for testing and default operation."""

    def generate_explanation(
        self, structured: StructuredHealthInput, risk: RiskResult, source_text: str = ""
    ) -> str:
        signals_text = _format_signals(structured, source_text)
        flags_text = _format_flags_plain(risk.flags)

        parts = [
            f"Based on the sample input, the workflow extracted {signals_text}.",
            f"The rule engine assigned a {risk.risk_level} risk level and noted {flags_text}.",
            risk.rule_explanation,
        ]

        if structured.extraction_notes and blood_pressure_mentioned(source_text):
            parts.append(structured.extraction_notes + ".")

        parts.append(
            "These results come from simple automated rules, not a clinical evaluation. "
            "If your symptoms feel concerning, unusual, persistent, or worsening, "
            "please seek professional medical advice. "
            "This is not a medical diagnosis."
        )
        return _strip_markdown(" ".join(parts))


class OpenAILLMService(LLMService):
    """OpenAI Responses API provider. Falls back gracefully if SDK or key is missing."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_explanation(
        self, structured: StructuredHealthInput, risk: RiskResult, source_text: str = ""
    ) -> str:
        user_prompt = (
            f"Original user input: {source_text}\n"
            f"Structured input: {structured.model_dump_json()}\n"
            f"Risk result: {risk.model_dump_json()}\n"
            "Provide a brief, calm explanation of these rule-based results in plain text only. "
            "Mention the flags in plain language."
        )

        client = self._get_client()
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
        )
        return _strip_markdown(response.output_text)


def get_llm_service() -> LLMService:
    """Return the configured LLM provider. Defaults to mock; falls back if OpenAI unavailable."""
    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return MockLLMService()
        try:
            return OpenAILLMService(api_key=api_key)
        except Exception:
            return MockLLMService()

    return MockLLMService()


def get_llm_provider_name() -> str:
    """Return the active LLM provider label for API responses."""
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "mock"
