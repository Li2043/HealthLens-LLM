"""Health text analysis pipeline."""

from app.errors import AnalysisPipelineError, ProviderConfigurationError
from app.extractor import get_extractor
from app.localization import localize_provider_warning, localize_structured_input
from app.llm_service import get_llm_provider_name, get_llm_service
from app.risk_rules import evaluate_risk
from app.safety_validator import validate_llm_output
from app.schemas import AnalysisResponse, Language


def run_analysis(text: str, language: Language = "en") -> AnalysisResponse:
    """
    Run extraction, rule-based risk, LLM explanation, and safety validation.

    Raises ProviderConfigurationError or AnalysisPipelineError on provider failures.
    """
    try:
        extractor, extractor_provider, provider_warning = get_extractor()
        structured = localize_structured_input(extractor.extract(text), language)
        risk_result = evaluate_risk(structured, text, language=language)

        llm = get_llm_service()
        explanation = llm.generate_explanation(structured, risk_result, text, language=language)
        safety_check = validate_llm_output(explanation)

        return AnalysisResponse(
            structured_input=structured,
            risk_result=risk_result,
            explanation=explanation,
            safety_check=safety_check,
            extractor_provider=extractor_provider,
            llm_provider=get_llm_provider_name(),
            provider_warning=localize_provider_warning(provider_warning, language),
        )
    except ProviderConfigurationError:
        raise
    except Exception as exc:
        raise AnalysisPipelineError from exc
