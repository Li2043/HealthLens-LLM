"""LLM-assisted and fallback health input extractors."""

import json
import os
import re
from abc import ABC, abstractmethod

from app.extraction_validator import validate_extraction
from app.parser import parse_health_text
from app.schemas import FieldEvidence, StructuredHealthInput

EXTRACTOR_SYSTEM_PROMPT = """You extract structured health signals from free-text input.

Rules:
- Extract ONLY information explicitly present in the user input.
- Do NOT infer diagnosis, advice, or medical risk.
- Distinguish absent, partial, and ambiguous information:
  - absent: the user did not mention that measurement at all.
  - partial: the user mentioned a measurement but gave incomplete numeric values.
  - ambiguous: the user mentioned a measurement qualitatively without usable numbers.
- Do NOT mark a field as missing unless the user attempted to provide that measurement.
- Do NOT mark diastolic_bp as missing unless blood pressure was mentioned.
- If blood pressure is not mentioned at all, leave systolic_bp and diastolic_bp null and do not include any blood pressure field in missing_or_ambiguous_fields.
- If the user says "My blood pressure is 200", set systolic_bp=200, diastolic_bp=null, add diastolic_bp to missing_or_ambiguous_fields, status partial for blood pressure.
- If the user says "BP 145/95", extract both values as complete.
- If the user says "my blood pressure is high" without numbers, leave values null and mark blood pressure as ambiguous. Do not invent numbers.
- Map unhappy/sad/low/depressed mood expressions to "low".
- Map cannot sleep / can't sleep / insomnia / slept badly to sleep_quality "poor".
- Provide source evidence text for every extracted field in field_evidence.
- Return plain JSON only. No Markdown.
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
        "field_evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "value": {"type": ["string", "null"]},
                    "evidence": {"type": ["string", "null"]},
                    "status": {
                        "type": "string",
                        "enum": ["absent", "partial", "complete", "ambiguous"],
                    },
                },
                "required": ["field", "value", "evidence", "status"],
                "additionalProperties": False,
            },
        },
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
        "field_evidence",
    ],
    "additionalProperties": False,
}


class BaseHealthExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> StructuredHealthInput:
        pass


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip().rstrip("."))


def _finalize_extraction(text: str, result: StructuredHealthInput) -> StructuredHealthInput:
    return validate_extraction(text, result)


def _parse_field_evidence(raw_items: list[dict] | None) -> list[FieldEvidence]:
    if not raw_items:
        return []
    return [FieldEvidence(**item) for item in raw_items]


class MockLLMExtractor(BaseHealthExtractor):
    """Deterministic mock extractor for demo inputs and CI."""

    def extract(self, text: str) -> StructuredHealthInput:
        normalized = _normalize_text(text)
        if normalized == "my blood pressure is 200":
            result = StructuredHealthInput(
                systolic_bp=200,
                symptoms=[],
                extraction_confidence="medium",
                missing_or_ambiguous_fields=["diastolic_bp"],
                extraction_notes=(
                    "Detected a single blood pressure value as systolic blood pressure; "
                    "diastolic value was not provided."
                ),
            )
            return _finalize_extraction(text, result)

        if normalized == "my heart rate is 100, i can not sleep, i am unhappy":
            result = StructuredHealthInput(
                heart_rate=100,
                mood="low",
                sleep_quality="poor",
                symptoms=[],
                extraction_confidence="high",
                missing_or_ambiguous_fields=[],
                extraction_notes=None,
            )
            return _finalize_extraction(text, result)

        if normalized == "my heart rate is 125, blood pressure is 150/95, i feel anxious and i cannot sleep":
            result = StructuredHealthInput(
                heart_rate=125,
                systolic_bp=150,
                diastolic_bp=95,
                mood="anxious",
                sleep_quality="poor",
                symptoms=[],
                extraction_confidence="high",
                missing_or_ambiguous_fields=[],
                extraction_notes=None,
            )
            return _finalize_extraction(text, result)

        if normalized == "bp 145/95 and i feel anxious":
            result = StructuredHealthInput(
                systolic_bp=145,
                diastolic_bp=95,
                mood="anxious",
                symptoms=[],
                extraction_confidence="high",
                missing_or_ambiguous_fields=[],
                extraction_notes=None,
            )
            return _finalize_extraction(text, result)

        if normalized == "my blood pressure is high":
            result = StructuredHealthInput(
                symptoms=[],
                extraction_confidence="medium",
                missing_or_ambiguous_fields=["blood_pressure"],
                extraction_notes="Blood pressure was mentioned qualitatively without numeric values.",
            )
            return _finalize_extraction(text, result)

        return RegexFallbackExtractor().extract(text)


class RegexFallbackExtractor(BaseHealthExtractor):
    """Regex parser wrapper used when LLM extraction is unavailable or fails."""

    def extract(self, text: str) -> StructuredHealthInput:
        return _finalize_extraction(text, parse_health_text(text))


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
            field_evidence = _parse_field_evidence(data.pop("field_evidence", []))
            result = StructuredHealthInput(**data, extraction_evidence=field_evidence)
            return _finalize_extraction(text, result)
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
