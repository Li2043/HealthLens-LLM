"""Extensible LLM provider for explaining rule-based risk results."""

import os
import re
from abc import ABC, abstractmethod

from app.extraction_validator import blood_pressure_mentioned
from app.schemas import Language, RiskResult, StructuredHealthInput

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

SYSTEM_PROMPT_ZH = """你负责解释基于规则的健康信号分析结果。必须遵守：
- 不得诊断疾病。
- 不得给出用药建议。
- 必须说明这不是医疗诊断。
- 若症状令人担忧、异常、持续或加重，建议寻求专业医疗帮助。
- 仅使用简洁、平实的纯文本，不要使用 Markdown。
- 用通俗语言说明检测到的规则标志。
- 除非原始输入提及血压，否则不要提及缺失的血压数据。
- 解释必须仅基于提供的结构化输入和风险标志。
- 必须使用简体中文回复。
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

_FLAG_PLAIN_LANGUAGE_ZH = {
    "very_high_systolic_bp": "收缩压非常高",
    "very_high_diastolic_bp": "舒张压非常高",
    "elevated_blood_pressure": "血压升高",
    "elevated_heart_rate": "心率偏高",
    "very_elevated_heart_rate": "心率明显偏高",
    "borderline_heart_rate": "心率临界偏高",
    "anxiety_or_stress_flag": "焦虑或压力迹象",
    "low_mood_flag": "情绪低落",
    "poor_sleep": "睡眠质量不佳",
    "incomplete_measurement": "测量不完整或存在歧义",
}

_RISK_LEVEL_ZH = {"low": "低", "moderate": "中", "high": "高"}

_MOOD_ZH = {
    "anxious": "焦虑",
    "stressed": "压力",
    "low": "低落",
    "calm": "平静",
    "unknown": "未知",
}

_SLEEP_ZH = {"good": "良好", "poor": "不佳", "unknown": "未知"}


class LLMService(ABC):
    @abstractmethod
    def generate_explanation(
        self,
        structured: StructuredHealthInput,
        risk: RiskResult,
        source_text: str = "",
        language: Language = "en",
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


def _format_flags_plain(flags: list[str], language: Language = "en") -> str:
    mapping = _FLAG_PLAIN_LANGUAGE_ZH if language == "zh" else _FLAG_PLAIN_LANGUAGE
    if not flags:
        return "无规则标志" if language == "zh" else "no rule-based flags"
    descriptions = [mapping.get(flag, flag.replace("_", " ")) for flag in flags]
    if language == "zh":
        if len(descriptions) == 1:
            return descriptions[0]
        return "、".join(descriptions[:-1]) + f"以及{descriptions[-1]}"
    if len(descriptions) == 1:
        return descriptions[0]
    return ", ".join(descriptions[:-1]) + f", and {descriptions[-1]}"


def _format_signals(
    structured: StructuredHealthInput, source_text: str, language: Language = "en"
) -> str:
    signals: list[str] = []
    if structured.heart_rate is not None:
        if language == "zh":
            signals.append(f"心率 {structured.heart_rate} 次/分")
        else:
            signals.append(f"heart rate of {structured.heart_rate} bpm")
    if blood_pressure_mentioned(source_text):
        if structured.systolic_bp is not None and structured.diastolic_bp is not None:
            if language == "zh":
                signals.append(f"血压 {structured.systolic_bp}/{structured.diastolic_bp}")
            else:
                signals.append(
                    f"blood pressure of {structured.systolic_bp}/{structured.diastolic_bp}"
                )
        elif structured.systolic_bp is not None:
            if language == "zh":
                signals.append(f"收缩压 {structured.systolic_bp}")
            else:
                signals.append(f"systolic blood pressure of {structured.systolic_bp}")
    if structured.mood:
        mood_label = (
            _MOOD_ZH.get(structured.mood, structured.mood)
            if language == "zh"
            else structured.mood
        )
        if language == "zh":
            signals.append(f"情绪为{mood_label}")
        else:
            signals.append(f"mood described as {mood_label}")
    if structured.sleep_quality:
        sleep_label = (
            _SLEEP_ZH.get(structured.sleep_quality, structured.sleep_quality)
            if language == "zh"
            else structured.sleep_quality
        )
        if language == "zh":
            signals.append(f"睡眠质量为{sleep_label}")
        else:
            signals.append(f"sleep quality described as {sleep_label}")
    if structured.symptoms:
        if language == "zh":
            signals.append(f"提及症状：{', '.join(structured.symptoms)}")
        else:
            signals.append(f"symptoms noted: {', '.join(structured.symptoms)}")
    if language == "zh":
        return "、".join(signals) if signals else "结构化信号有限"
    return ", ".join(signals) if signals else "limited structured signals"


class MockLLMService(LLMService):
    """Deterministic mock provider for testing and default operation."""

    def generate_explanation(
        self,
        structured: StructuredHealthInput,
        risk: RiskResult,
        source_text: str = "",
        language: Language = "en",
    ) -> str:
        signals_text = _format_signals(structured, source_text, language)
        flags_text = _format_flags_plain(risk.flags, language)

        if language == "zh":
            level_label = _RISK_LEVEL_ZH[risk.risk_level]
            parts = [
                f"根据示例输入，工作流提取到{signals_text}。",
                f"规则引擎判定为{level_label}风险，并注意到{flags_text}。",
                risk.rule_explanation,
            ]
            if structured.extraction_notes and blood_pressure_mentioned(source_text):
                parts.append(structured.extraction_notes)
            parts.append(
                "以上结果来自简单的自动化规则，并非临床评估。"
                "若您的症状令人担忧、异常、持续或加重，请寻求专业医疗帮助。"
                "这不是医疗诊断。"
            )
        else:
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
        self,
        structured: StructuredHealthInput,
        risk: RiskResult,
        source_text: str = "",
        language: Language = "en",
    ) -> str:
        if language == "zh":
            user_prompt = (
                f"原始用户输入：{source_text}\n"
                f"结构化输入：{structured.model_dump_json()}\n"
                f"风险结果：{risk.model_dump_json()}\n"
                "请用简体中文简要、平和地解释这些基于规则的结果。"
                "用通俗语言说明相关标志。"
            )
            instructions = SYSTEM_PROMPT_ZH
        else:
            user_prompt = (
                f"Original user input: {source_text}\n"
                f"Structured input: {structured.model_dump_json()}\n"
                f"Risk result: {risk.model_dump_json()}\n"
                "Provide a brief, calm explanation of these rule-based results in plain text only. "
                "Mention the flags in plain language."
            )
            instructions = SYSTEM_PROMPT

        client = self._get_client()
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=instructions,
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
