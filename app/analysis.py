"""Health text analysis pipeline."""

from app.errors import AnalysisPipelineError, ProviderConfigurationError
from app.extractor import get_extractor
from app.llm_service import get_llm_provider_name, get_llm_service
from app.risk_rules import evaluate_risk
from app.safety_validator import validate_llm_output
from app.schemas import AnalysisResponse


def run_analysis(text: str) -> AnalysisResponse:
    """
    Run extraction, rule-based risk, LLM explanation, and safety validation.

    Raises ProviderConfigurationError or AnalysisPipelineError on provider failures.
    """
    try:
        extractor, extractor_provider, provider_warning = get_extractor()
        structured = extractor.extract(text)
        risk_result = evaluate_risk(structured, text)

        llm = get_llm_service()
        explanation = llm.generate_explanation(structured, risk_result, text)
        safety_check = validate_llm_output(explanation)

        return AnalysisResponse(
            structured_input=structured,
            risk_result=risk_result,
            explanation=explanation,
            safety_check=safety_check,
            extractor_provider=extractor_provider,
            llm_provider=get_llm_provider_name(),
            provider_warning=provider_warning,
        )
    except ProviderConfigurationError:
        raise
    except Exception as exc:
        raise AnalysisPipelineError from exc
