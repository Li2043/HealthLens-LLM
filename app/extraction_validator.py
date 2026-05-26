"""Post-extraction validation to enforce absent vs partial vs ambiguous boundaries."""

import re

from app.schemas import FieldEvidence, MeasurementStatus, StructuredHealthInput

_BP_MENTION = re.compile(r"blood\s*pressure|\bbp\b", re.IGNORECASE)
_BP_SLASH = re.compile(r"(\d{2,3})\s*/\s*(\d{2,3})")
_BP_SINGLE = re.compile(
    r"(?:blood\s*pressure|bp)\s*(?:is|:)?\s*(\d{2,3})(?!\s*/|\s+over)",
    re.IGNORECASE,
)
_BP_QUALITATIVE = re.compile(
    r"(?:blood\s*pressure|bp)\s*(?:is|:)?\s*(?:high|low|elevated|raised)",
    re.IGNORECASE,
)
_HR_MENTION = re.compile(r"heart\s*rate|heartbeat|\bhr\b|pulse", re.IGNORECASE)
_HR_VALUE = re.compile(
    r"(?:heart\s*rate|heartbeat|hr|pulse)\s*(?:is|:)?\s*(\d{2,3})",
    re.IGNORECASE,
)

_BP_MISSING_FIELDS = {"systolic_bp", "diastolic_bp", "blood_pressure"}


def blood_pressure_mentioned(text: str) -> bool:
    return bool(_BP_MENTION.search(text) or _BP_SLASH.search(text))


def heart_rate_mentioned(text: str) -> bool:
    return bool(_HR_MENTION.search(text))


def validate_extraction(text: str, result: StructuredHealthInput) -> StructuredHealthInput:
    """Clean missing-field flags and values when measurements were not mentioned."""
    missing = list(result.missing_or_ambiguous_fields)
    systolic = result.systolic_bp
    diastolic = result.diastolic_bp
    heart_rate = result.heart_rate
    notes = result.extraction_notes

    bp_mentioned = blood_pressure_mentioned(text)
    hr_mentioned = heart_rate_mentioned(text)
    bp_has_numbers = bool(_BP_SLASH.search(text) or _BP_SINGLE.search(text))
    bp_qualitative_only = bool(_BP_QUALITATIVE.search(text)) and not bp_has_numbers

    if not bp_mentioned:
        missing = [field for field in missing if field not in _BP_MISSING_FIELDS]
        systolic = None
        diastolic = None
    elif bp_qualitative_only:
        systolic = None
        diastolic = None
        missing = [field for field in missing if field not in ("systolic_bp", "diastolic_bp")]
        if "blood_pressure" not in missing:
            missing.append("blood_pressure")
        if not notes:
            notes = "Blood pressure was mentioned qualitatively without numeric values."
    elif systolic is not None and diastolic is None:
        if "diastolic_bp" not in missing:
            missing.append("diastolic_bp")
        if not notes:
            notes = (
                "Detected a single blood pressure value as systolic blood pressure; "
                "diastolic value was not provided."
            )
    else:
        missing = [field for field in missing if field not in _BP_MISSING_FIELDS or field == "blood_pressure"]

    if not hr_mentioned:
        missing = [field for field in missing if field != "heart_rate"]
        heart_rate = None

    evidence = _build_extraction_evidence(
        text=text,
        heart_rate=heart_rate,
        systolic_bp=systolic,
        diastolic_bp=diastolic,
        mood=result.mood,
        sleep_quality=result.sleep_quality,
        bp_mentioned=bp_mentioned,
        hr_mentioned=hr_mentioned,
        bp_qualitative_only=bp_qualitative_only,
        existing_evidence=result.extraction_evidence,
    )

    return result.model_copy(
        update={
            "heart_rate": heart_rate,
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "missing_or_ambiguous_fields": missing,
            "extraction_notes": notes,
            "extraction_evidence": evidence,
        }
    )


def _build_extraction_evidence(
    text: str,
    heart_rate: int | None,
    systolic_bp: int | None,
    diastolic_bp: int | None,
    mood: str | None,
    sleep_quality: str | None,
    bp_mentioned: bool,
    hr_mentioned: bool,
    bp_qualitative_only: bool,
    existing_evidence: list[FieldEvidence],
) -> list[FieldEvidence]:
    existing_map = {item.field: item for item in existing_evidence}
    evidence: list[FieldEvidence] = []

    hr_match = _HR_VALUE.search(text)
    if heart_rate is not None:
        status: MeasurementStatus = "complete"
        snippet = hr_match.group(0) if hr_match else existing_map.get("heart_rate", FieldEvidence(field="heart_rate", status="complete")).evidence
        evidence.append(FieldEvidence(field="heart_rate", value=str(heart_rate), evidence=snippet, status=status))
    elif hr_mentioned:
        evidence.append(FieldEvidence(field="heart_rate", value=None, evidence=None, status="ambiguous"))
    else:
        evidence.append(FieldEvidence(field="heart_rate", value=None, evidence=None, status="absent"))

    if systolic_bp is not None and diastolic_bp is not None:
        slash = _BP_SLASH.search(text)
        snippet = slash.group(0) if slash else existing_map.get("systolic_bp", FieldEvidence(field="systolic_bp", status="complete")).evidence
        evidence.append(FieldEvidence(field="systolic_bp", value=str(systolic_bp), evidence=snippet, status="complete"))
        evidence.append(FieldEvidence(field="diastolic_bp", value=str(diastolic_bp), evidence=snippet, status="complete"))
    elif systolic_bp is not None:
        single = _BP_SINGLE.search(text)
        snippet = single.group(0) if single else existing_map.get("systolic_bp", FieldEvidence(field="systolic_bp", status="partial")).evidence
        evidence.append(FieldEvidence(field="systolic_bp", value=str(systolic_bp), evidence=snippet, status="partial"))
        evidence.append(FieldEvidence(field="diastolic_bp", value=None, evidence=None, status="partial"))
    elif bp_qualitative_only:
        qual = _BP_QUALITATIVE.search(text)
        snippet = qual.group(0) if qual else None
        evidence.append(FieldEvidence(field="systolic_bp", value=None, evidence=snippet, status="ambiguous"))
        evidence.append(FieldEvidence(field="diastolic_bp", value=None, evidence=snippet, status="ambiguous"))
    elif bp_mentioned:
        evidence.append(FieldEvidence(field="systolic_bp", value=None, evidence=None, status="ambiguous"))
        evidence.append(FieldEvidence(field="diastolic_bp", value=None, evidence=None, status="ambiguous"))
    else:
        evidence.append(FieldEvidence(field="systolic_bp", value=None, evidence=None, status="absent"))
        evidence.append(FieldEvidence(field="diastolic_bp", value=None, evidence=None, status="absent"))

    mood_evidence = _find_mood_evidence(text, mood)
    if mood:
        evidence.append(FieldEvidence(field="mood", value=mood, evidence=mood_evidence, status="complete"))
    else:
        evidence.append(FieldEvidence(field="mood", value=None, evidence=None, status="absent"))

    sleep_evidence = _find_sleep_evidence(text, sleep_quality)
    if sleep_quality:
        evidence.append(FieldEvidence(field="sleep_quality", value=sleep_quality, evidence=sleep_evidence, status="complete"))
    else:
        evidence.append(FieldEvidence(field="sleep_quality", value=None, evidence=None, status="absent"))

    return evidence


def _find_mood_evidence(text: str, mood: str | None) -> str | None:
    if not mood:
        return None
    keywords = {
        "anxious": ["anxious", "worried", "panic"],
        "stressed": ["stressed", "stress"],
        "low": ["unhappy", "sad", "low", "depressed"],
        "calm": ["calm", "relaxed"],
    }
    lower = text.lower()
    for keyword in keywords.get(mood, [mood]):
        idx = lower.find(keyword)
        if idx >= 0:
            return text[idx : idx + len(keyword)]
    return None


def _find_sleep_evidence(text: str, sleep_quality: str | None) -> str | None:
    if not sleep_quality:
        return None
    patterns = [
        r"can\s*'?t\s*sleep",
        r"cannot\s*sleep",
        r"can\s+not\s*sleep",
        r"slept\s+badly",
        r"poor\s+sleep",
        r"\binsomnia\b",
        r"slept\s+well",
        r"good\s+sleep",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None
