"""LLM-assisted and fallback health input extractors."""

import json
import os
import re
from abc import ABC, abstractmethod

from app.parser import parse_health_text
from app.schemas import StructuredHealthInput

EXTRACTOR_SYSTEM_PROMPT = """You extract structured health signals from free-text input.
Rules:
- Extract ONLY information explicitly present in the user input.
- Do NOT infer diagnosis.
- Do NOT provide advice.
- Do NOT classify medical risk.
- If only one blood pressure number is provided with a blood pressure phrase, set systolic_bp to that number, diastolic_bp to null, and add "diastolic_bp" to missing_or_ambiguous_fields.
- If information is absent, use null.
- Map "unhappy", "sad", "low", or "depressed" mood expressions to "low".
- Map "can not sleep", "cannot sleep", "can't sleep", "insomnia", or "slept badly" to sleep_quality "poor".
- Return ONLY valid JSON matching the schema.
"""

EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "heart_rate": {"type": ["integer", "null"]},
        "systolic_bp": {"type": ["integer", "null"]},
        "diastolic_bp": {"type": ["integer", "null"]},
        "mood": {
            "type": ["string", "null"],
            "enum": ["anxious", "stressed", "low", "calm", "unknown", None],
        },
        "sleep_quality": {
            "type": ["string", "null"],
            "enum": ["good", "poor", "unknown", None],
        },
        "symptoms": {"type": "array", "items": {"type": "string"}},
        "extraction_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "missing_or_ambiguous_fields": {"type": "array", "items": {"type": "string"}},
        "extraction_notes": {"type": ["string", "null"]},
    },
    "required": [
        "heart_rate",
        "systolic_bp",
        "diastolic_bp",
        "mood",
        "sleep_quality",
        "symptoms",
        "extraction_confidence",
        "missing_or_ambiguous_fields",
        "extraction_notes",
    ],
    "additionalProperties": False,
}


class BaseHealthExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> StructuredHealthInput:
        pass


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip().rstrip("."))


class MockLLMExtractor(BaseHealthExtractor):
    """Deterministic mock extractor for demo inputs and CI."""

    _DEMO_OUTPUTS: dict[str, StructuredHealthInput] = {
        "my blood pressure is 200": StructuredHealthInput(
            systolic_bp=200,
            symptoms=[],
            extraction_confidence="medium",
            missing_or_ambiguous_fields=["diastolic_bp"],
            extraction_notes=(
                "Detected a single blood pressure value as systolic blood pressure; "
                "diastolic value was not provided."
            ),
        ),
        "my heart rate is 100, i can not sleep, i am unhappy": StructuredHealthInput(
            heart_rate=100,
            mood="low",
            sleep_quality="poor",
            symptoms=[],
            extraction_confidence="high",
            missing_or_ambiguous_fields=[],
            extraction_notes=None,
        ),
        "my heart rate is 125, blood pressure is 150/95, i feel anxious and i cannot sleep": StructuredHealthInput(
            heart_rate=125,
            systolic_bp=150,
            diastolic_bp=95,
            mood="anxious",
            sleep_quality="poor",
            symptoms=[],
            extraction_confidence="high",
            missing_or_ambiguous_fields=[],
            extraction_notes=None,
        ),
    }

    def extract(self, text: str) -> StructuredHealthInput:
        normalized = _normalize_text(text)
        if normalized in self._DEMO_OUTPUTS:
            return self._DEMO_OUTPUTS[normalized].model_copy(deep=True)
        return RegexFallbackExtractor().extract(text)


class RegexFallbackExtractor(BaseHealthExtractor):
    """Regex parser wrapper used when LLM extraction is unavailable or fails."""

    def extract(self, text: str) -> StructuredHealthInput:
        return parse_health_text(text)


class OpenAILLMExtractor(BaseHealthExtractor):
    """OpenAI Responses API extractor with regex fallback on failure."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
        self._fallback = RegexFallbackExtractor()

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def extract(self, text: str) -> StructuredHealthInput:
        try:
            client = self._get_client()
            response = client.responses.create(
                model="gpt-4o-mini",
                instructions=EXTRACTOR_SYSTEM_PROMPT,
                input=text,
                temperature=0,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "health_extraction",
                        "schema": EXTRACTION_JSON_SCHEMA,
                        "strict": True,
                    }
                },
            )
            data = json.loads(response.output_text)
            return StructuredHealthInput(**data)
        except Exception:
            fallback = self._fallback.extract(text)
            return fallback.model_copy(
                update={
                    "extraction_confidence": "low",
                    "extraction_notes": (
                        "LLM extraction failed; regex fallback was used. "
                        + (fallback.extraction_notes or "")
                    ).strip(),
                }
            )


def get_extractor() -> tuple[BaseHealthExtractor, str, str | None]:
    """
    Return configured extractor, provider name, and optional warning.

    Falls back to MockLLMExtractor when openai is requested without an API key.
    """
    provider = os.getenv("EXTRACTOR_PROVIDER", "mock").lower()
    warning: str | None = None

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            warning = "OPENAI_API_KEY missing; falling back to mock extractor."
            return MockLLMExtractor(), "mock", warning
        return OpenAILLMExtractor(api_key=api_key), "openai", None

    if provider == "regex":
        return RegexFallbackExtractor(), "regex", None

    return MockLLMExtractor(), "mock", None
