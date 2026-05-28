"""Localized user-facing strings for analysis output."""

from app.schemas import StructuredHealthInput

Language = str

_EXTRACTION_NOTE_ZH = {
    "Blood pressure was mentioned qualitatively without numeric values.": (
        "用户定性提及血压，但未提供具体数值。"
    ),
    "Detected a single blood pressure value as systolic blood pressure; diastolic value was not provided.": (
        "检测到单项血压数值，已作为收缩压；未提供舒张压。"
    ),
    "Extracted using regex fallback parser.": "使用正则回退解析器提取。",
}

_MOOD_ZH = {
    "anxious": "焦虑",
    "stressed": "压力",
    "low": "低落",
    "calm": "平静",
    "unknown": "未知",
}

_SLEEP_ZH = {
    "good": "良好",
    "poor": "不佳",
    "unknown": "未知",
}

_PROVIDER_WARNING_ZH = {
    "OPENAI_API_KEY missing; falling back to mock extractor.": (
        "缺少 OPENAI_API_KEY；已回退至 mock 提取器。"
    ),
}


def localize_extraction_notes(notes: str | None, language: Language) -> str | None:
    if not notes or language != "zh":
        return notes
    return _EXTRACTION_NOTE_ZH.get(notes, notes)


def localize_structured_input(
    structured: StructuredHealthInput, language: Language
) -> StructuredHealthInput:
    if language != "zh":
        return structured

    localized_evidence = []
    for item in structured.extraction_evidence:
        value = item.value
        if value is not None:
            if item.field == "mood":
                value = _MOOD_ZH.get(value, value)
            elif item.field == "sleep_quality":
                value = _SLEEP_ZH.get(value, value)
        localized_evidence.append(item.model_copy(update={"value": value}))

    return structured.model_copy(
        update={
            "extraction_notes": localize_extraction_notes(structured.extraction_notes, language),
            "extraction_evidence": localized_evidence,
        }
    )


def localize_provider_warning(warning: str | None, language: Language) -> str | None:
    if not warning or language != "zh":
        return warning
    return _PROVIDER_WARNING_ZH.get(warning, warning)
