from app.llm_service import MockLLMService
from app.schemas import RiskResult, StructuredHealthInput


def test_mock_llm_returns_deterministic_text():
    service = MockLLMService()
    structured = StructuredHealthInput(heart_rate=110)
    risk = RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate"],
        rule_explanation="Rule engine detected 1 flag(s): heart rate above 100 bpm. Overall risk level is moderate.",
    )

    result1 = service.explain(structured, risk)
    result2 = service.explain(structured, risk)

    assert result1 == result2
    assert len(result1) > 0


def test_mock_llm_includes_disclaimer():
    service = MockLLMService()
    structured = StructuredHealthInput()
    risk = RiskResult(
        risk_level="low",
        flags=[],
        rule_explanation="No rule-based flags were triggered. Overall risk level is low.",
    )

    result = service.explain(structured, risk)
    assert "not a medical diagnosis" in result.lower()


def test_mock_llm_returns_chinese_explanation():
    service = MockLLMService()
    structured = StructuredHealthInput(heart_rate=110)
    risk = RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate"],
        rule_explanation="规则引擎检测到 1 个标志：心率超过 100 次/分。总体风险等级为中。",
    )

    result = service.generate_explanation(structured, risk, language="zh")

    assert "根据示例输入" in result
    assert "这不是医疗诊断" in result
