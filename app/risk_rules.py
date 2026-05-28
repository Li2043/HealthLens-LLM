"""Rule-based risk evaluation from structured health input."""

from app.extraction_validator import blood_pressure_mentioned
from app.schemas import Language, RiskLevel, RiskResult, StructuredHealthInput

_FLAG_DESCRIPTIONS = {
    "very_high_systolic_bp": "very high systolic blood pressure",
    "very_high_diastolic_bp": "very high diastolic blood pressure",
    "elevated_blood_pressure": "elevated blood pressure",
    "elevated_heart_rate": "heart rate above 100 bpm",
    "very_elevated_heart_rate": "heart rate above 120 bpm",
    "borderline_heart_rate": "heart rate between 95 and 100 bpm",
    "anxiety_or_stress_flag": "anxiety or stress noted in mood",
    "low_mood_flag": "low mood noted",
    "poor_sleep": "poor sleep quality reported",
    "incomplete_measurement": "incomplete or ambiguous measurements",
}

_FLAG_DESCRIPTIONS_ZH = {
    "very_high_systolic_bp": "收缩压非常高",
    "very_high_diastolic_bp": "舒张压非常高",
    "elevated_blood_pressure": "血压升高",
    "elevated_heart_rate": "心率超过 100 次/分",
    "very_elevated_heart_rate": "心率超过 120 次/分",
    "borderline_heart_rate": "心率在 95 至 100 次/分之间",
    "anxiety_or_stress_flag": "情绪显示焦虑或压力",
    "low_mood_flag": "情绪低落",
    "poor_sleep": "睡眠质量不佳",
    "incomplete_measurement": "测量不完整或存在歧义",
}

_RISK_LEVEL_ZH = {"low": "低", "moderate": "中", "high": "高"}

_CRITICAL_FLAGS = {
    "very_high_systolic_bp",
    "very_high_diastolic_bp",
    "very_elevated_heart_rate",
}
_BORDERLINE_FLAGS = {"borderline_heart_rate"}


def evaluate_risk(
    input: StructuredHealthInput,
    source_text: str = "",
    language: Language = "en",
) -> RiskResult:
    """Evaluate risk flags and overall risk level from structured input."""
    flags: list[str] = []

    if input.systolic_bp is not None:
        if input.systolic_bp >= 180:
            flags.append("very_high_systolic_bp")
        if input.systolic_bp >= 140:
            _append_unique(flags, "elevated_blood_pressure")

    if input.diastolic_bp is not None:
        if input.diastolic_bp >= 120:
            flags.append("very_high_diastolic_bp")
        if input.diastolic_bp >= 90:
            _append_unique(flags, "elevated_blood_pressure")

    if input.heart_rate is not None:
        if input.heart_rate > 120:
            flags.append("very_elevated_heart_rate")
        if input.heart_rate > 100:
            _append_unique(flags, "elevated_heart_rate")
        elif 95 <= input.heart_rate <= 100:
            flags.append("borderline_heart_rate")

    if input.mood in ("anxious", "stressed"):
        flags.append("anxiety_or_stress_flag")
    elif input.mood == "low":
        flags.append("low_mood_flag")

    if input.sleep_quality == "poor":
        flags.append("poor_sleep")

    if input.missing_or_ambiguous_fields:
        flags.append("incomplete_measurement")

    risk_level = _compute_risk_level(flags)
    rule_explanation = _build_rule_explanation(flags, risk_level, input, source_text, language)

    return RiskResult(
        risk_level=risk_level,
        flags=flags,
        rule_explanation=rule_explanation,
    )


def _append_unique(flags: list[str], flag: str) -> None:
    if flag not in flags:
        flags.append(flag)


def _compute_risk_level(flags: list[str]) -> RiskLevel:
    if not flags:
        return "low"

    if any(flag in _CRITICAL_FLAGS for flag in flags):
        return "high"

    non_borderline = [flag for flag in flags if flag not in _BORDERLINE_FLAGS]
    if not non_borderline:
        return "low"
    return "moderate"


def _flag_descriptions(language: Language) -> dict[str, str]:
    return _FLAG_DESCRIPTIONS_ZH if language == "zh" else _FLAG_DESCRIPTIONS


def _build_rule_explanation(
    flags: list[str],
    risk_level: RiskLevel,
    input: StructuredHealthInput,
    source_text: str,
    language: Language = "en",
) -> str:
    descriptions_map = _flag_descriptions(language)

    if not flags:
        if language == "zh":
            return "未触发任何规则标志。总体风险等级为低。这是基于规则的 prototype 结果，非临床评估。"
        return (
            "No rule-based flags were triggered. Overall risk level is low. "
            "This is a rule-based prototype result, not a clinical evaluation."
        )

    descriptions = [descriptions_map.get(flag, flag) for flag in flags]
    joined = "; ".join(descriptions)

    if language == "zh":
        level_label = _RISK_LEVEL_ZH[risk_level]
        explanation = (
            f"规则引擎检测到 {len(flags)} 个标志：{joined}。"
            f"总体风险等级为{level_label}。"
            "这是基于规则的 prototype 结果，非临床评估。"
        )
    else:
        explanation = (
            f"Rule engine detected {len(flags)} flag(s): {joined}. "
            f"Overall risk level is {risk_level}. "
            "This is a rule-based prototype result, not a clinical evaluation."
        )

    if input.missing_or_ambiguous_fields and blood_pressure_mentioned(source_text):
        missing = ", ".join(input.missing_or_ambiguous_fields)
        if language == "zh":
            explanation += f" 缺失或歧义字段：{missing}。"
        else:
            explanation += f" Missing or ambiguous fields: {missing}."

    return explanation
