"""
Regex-based health-text parser used as a fallback extractor.

Extracts heart rate, blood pressure, mood, and sleep quality from free text.
"""

import re

from app.schemas import StructuredHealthInput

_HEART_RATE_PATTERNS = [
    re.compile(
        r"(?:heart\s*rate|heartbeat|hr|pulse)\s*(?:is|:)?\s*(\d{2,3})",
        re.IGNORECASE,
    ),
]

_BP_SLASH_PATTERN = re.compile(
    r"(?:blood\s*pressure|bp)\s*(?:is|:)?\s*(\d{2,3})\s*/\s*(\d{2,3})",
    re.IGNORECASE,
)
_BP_OVER_PATTERN = re.compile(
    r"(?:blood\s*pressure|bp)\s*(?:is|:)?\s*(\d{2,3})\s+over\s+(\d{2,3})",
    re.IGNORECASE,
)
_BP_SINGLE_PATTERN = re.compile(
    r"(?:blood\s*pressure|bp)\s*(?:is|:)?\s*(\d{2,3})(?!\s*/|\s+over)",
    re.IGNORECASE,
)
_BP_BARE_SLASH_PATTERN = re.compile(r"(\d{2,3})\s*/\s*(\d{2,3})")

_MOOD_RULES: list[tuple[list[str], str]] = [
    (["anxious", "panic", "panicked", "worried"], "anxious"),
    (["stressed", "stress"], "stressed"),
    (["unhappy", "sad", "low", "depressed"], "low"),
    (["calm", "relaxed"], "calm"),
]

_POOR_SLEEP_PATTERNS = [
    re.compile(r"can\s*'?t\s*sleep", re.IGNORECASE),
    re.compile(r"cannot\s*sleep", re.IGNORECASE),
    re.compile(r"can\s+not\s*sleep", re.IGNORECASE),
    re.compile(r"slept\s+badly", re.IGNORECASE),
    re.compile(r"poor\s+sleep", re.IGNORECASE),
    re.compile(r"\binsomnia\b", re.IGNORECASE),
    re.compile(r"trouble\s+sleeping", re.IGNORECASE),
]

_GOOD_SLEEP_KEYWORDS = ["slept well", "good sleep"]


def parse_health_text(text: str) -> StructuredHealthInput:
    """Parse free-text health input into structured fields using regex."""
    heart_rate = _extract_heart_rate(text)
    systolic_bp, diastolic_bp = _extract_blood_pressure(text)
    mood = _extract_mood(text)
    sleep_quality = _extract_sleep_quality(text)

    missing: list[str] = []
    if systolic_bp is not None and diastolic_bp is None:
        missing.append("diastolic_bp")

    return StructuredHealthInput(
        heart_rate=heart_rate,
        systolic_bp=systolic_bp,
        diastolic_bp=diastolic_bp,
        mood=mood,  # type: ignore[arg-type]
        sleep_quality=sleep_quality,  # type: ignore[arg-type]
        symptoms=[],
        extraction_confidence="low",
        missing_or_ambiguous_fields=missing,
        extraction_notes="Extracted using regex fallback parser.",
    )


def _extract_heart_rate(text: str) -> int | None:
    for pattern in _HEART_RATE_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def _extract_blood_pressure(text: str) -> tuple[int | None, int | None]:
    for pattern in (_BP_SLASH_PATTERN, _BP_OVER_PATTERN, _BP_BARE_SLASH_PATTERN):
        match = pattern.search(text)
        if match:
            return int(match.group(1)), int(match.group(2))

    single = _BP_SINGLE_PATTERN.search(text)
    if single:
        return int(single.group(1)), None
    return None, None


def _extract_mood(text: str) -> str | None:
    lower = text.lower()
    for keywords, mood in _MOOD_RULES:
        for keyword in keywords:
            if keyword in lower:
                return mood
    return None


def _extract_sleep_quality(text: str) -> str | None:
    for pattern in _POOR_SLEEP_PATTERNS:
        if pattern.search(text):
            return "poor"
    lower = text.lower()
    for keyword in _GOOD_SLEEP_KEYWORDS:
        if keyword in lower:
            return "good"
    return None
