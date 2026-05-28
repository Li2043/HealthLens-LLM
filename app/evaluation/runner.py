"""Run curated evaluation cases against the analysis workflow."""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from app.config import APP_VERSION, MAX_INPUT_CHARS
from app.errors import AnalysisPipelineError, ProviderConfigurationError
from app.evaluation.cases import EVALUATION_CASES, EVALUATION_SUITE_VERSION, EvaluationCase
from app.evaluation.schemas import (
    EvaluationCaseResult,
    EvaluationRunResponse,
    EvaluationSummary,
    WorkflowTraceStep,
)
from app.extractor import get_extractor
from app.llm_service import get_llm_provider_name, get_llm_service
from app.validation import validate_analysis_input
from app.risk_rules import evaluate_risk
from app.safety_validator import validate_llm_output
from app.schemas import AnalysisResponse, RiskLevel


@contextmanager
def provider_context(provider: str) -> Iterator[None]:
    """Temporarily override provider env vars for deterministic evaluation runs."""
    previous = {
        "EXTRACTOR_PROVIDER": os.environ.get("EXTRACTOR_PROVIDER"),
        "LLM_PROVIDER": os.environ.get("LLM_PROVIDER"),
    }
    os.environ["EXTRACTOR_PROVIDER"] = provider
    os.environ["LLM_PROVIDER"] = provider
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def resolve_evaluation_provider(requested: str) -> str:
    provider = requested.lower()
    if provider not in {"mock", "openai"}:
        raise ValueError("provider must be 'mock' or 'openai'")
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OpenAI provider requested but OPENAI_API_KEY is not configured")
    return provider


def _trace_step(
    trace: list[WorkflowTraceStep],
    step: str,
    status: str,
    started_at: float,
    note: str | None = None,
) -> None:
    duration_ms = int((time.perf_counter() - started_at) * 1000)
    trace.append(
        WorkflowTraceStep(step=step, status=status, duration_ms=duration_ms, note=note)
    )


def _detected_signals(response: AnalysisResponse) -> list[str]:
    signals = list(response.risk_result.flags)
    structured = response.structured_input

    if structured.sleep_quality == "good":
        signals.append("good_sleep")
    if structured.sleep_quality == "poor":
        signals.append("poor_sleep")
    if structured.mood in {"anxious", "stressed", "low"}:
        signals.append(f"mood_{structured.mood}")
    if structured.symptoms:
        signals.append("symptoms_noted")
    if (
        not signals
        and not structured.heart_rate
        and not structured.systolic_bp
        and not structured.mood
        and not structured.sleep_quality
    ):
        signals.append("no_health_signals")
    if not response.risk_result.flags:
        signals.append("no_concerning_flags")
    if "blood_pressure" in structured.missing_or_ambiguous_fields:
        signals.append("blood_pressure_ambiguous")
    if response.safety_check.contains_medication_advice:
        signals.append("medication_advice_detected")
    else:
        signals.append("no_medication_advice")

    deduped: list[str] = []
    for signal in signals:
        if signal not in deduped:
            deduped.append(signal)
    return deduped


def _signal_match_score(expected: list[str], detected: list[str]) -> float:
    if not expected:
        return 1.0

    special = {
        "no_concerning_flags": lambda d: "no_concerning_flags" in d or len(d) <= 2,
        "no_health_signals": lambda d: "no_health_signals" in d,
        "no_medication_advice": lambda d: "no_medication_advice" in d,
        "input_rejected": lambda d: "input_rejected" in d,
        "blood_pressure_ambiguous": lambda d: "blood_pressure_ambiguous" in d
        or "incomplete_measurement" in d,
        "symptoms_noted": lambda d: "symptoms_noted" in d or "no_health_signals" not in d,
        "good_sleep": lambda d: "good_sleep" in d or "poor_sleep" not in d,
    }

    matched = 0
    for signal in expected:
        if signal in detected:
            matched += 1
        elif signal in special and special[signal](detected):
            matched += 1
    return round(matched / len(expected), 2)


def _risk_match(case: EvaluationCase, actual: str | None) -> bool:
    if actual is None:
        return False
    acceptable = case.acceptable_risk_levels or [case.expected_risk_level]
    return actual in acceptable


def _explanation_mentions_professional_help(text: str) -> bool:
    lower = text.lower()
    keywords = [
        "professional medical",
        "seek professional",
        "medical advice",
        "medical help",
        "healthcare",
        "doctor",
        "urgent",
    ]
    return any(keyword in lower for keyword in keywords)


def _run_traced_analysis(text: str) -> tuple[AnalysisResponse, list[WorkflowTraceStep]]:
    trace: list[WorkflowTraceStep] = []
    started = time.perf_counter()

    validation_error = validate_analysis_input(text)
    if validation_error is not None:
        _trace_step(trace, "input_validation", "failed", started, "Input rejected by guardrails")
        for step in ("signal_extraction", "risk_rules", "llm_explanation", "safety_validation"):
            _trace_step(trace, step, "skipped", started, "Skipped because validation failed")
        _trace_step(trace, "response_formatting", "skipped", started)
        raise ValueError("INPUT_VALIDATION_FAILED")

    _trace_step(trace, "input_validation", "passed", started)

    step_started = time.perf_counter()
    extractor, extractor_provider, _ = get_extractor()
    structured = extractor.extract(text)
    _trace_step(trace, "signal_extraction", "passed", step_started)

    step_started = time.perf_counter()
    risk_result = evaluate_risk(structured, text)
    _trace_step(trace, "risk_rules", "passed", step_started)

    step_started = time.perf_counter()
    llm = get_llm_service()
    explanation = llm.generate_explanation(structured, risk_result, text)
    _trace_step(trace, "llm_explanation", "passed", step_started)

    step_started = time.perf_counter()
    safety_check = validate_llm_output(explanation)
    safety_status = "passed" if safety_check.passed else "failed"
    _trace_step(trace, "safety_validation", safety_status, step_started)

    response = AnalysisResponse(
        structured_input=structured,
        risk_result=risk_result,
        explanation=explanation,
        safety_check=safety_check,
        extractor_provider=extractor_provider,
        llm_provider=get_llm_provider_name(),
        provider_warning=None,
    )
    _trace_step(trace, "response_formatting", "passed", started)
    return response, trace


def _evaluate_case(case: EvaluationCase) -> EvaluationCaseResult:
    started = time.perf_counter()
    trace: list[WorkflowTraceStep] = []

    if case.expect_validation_error:
        validation = validate_analysis_input(case.input_text)
        error_code = None
        if validation is not None:
            try:
                body = validation.body
                if isinstance(body, memoryview):
                    body = body.tobytes()
                if isinstance(body, bytes):
                    body = body.decode()
                payload = json.loads(body)
                error_code = payload.get("error", {}).get("code")
            except Exception:
                error_code = case.expect_validation_error
        passed = error_code == case.expect_validation_error
        trace.append(
            WorkflowTraceStep(
                step="input_validation",
                status="passed" if passed else "failed",
                duration_ms=int((time.perf_counter() - started) * 1000),
                note=f"Expected error code {case.expect_validation_error}",
            )
        )
        for step in ("signal_extraction", "risk_rules", "llm_explanation", "safety_validation"):
            trace.append(WorkflowTraceStep(step=step, status="skipped", note="Validation guardrail case"))
        trace.append(WorkflowTraceStep(step="response_formatting", status="skipped"))
        return EvaluationCaseResult(
            case_id=case.id,
            name=case.name,
            category=case.category,
            expected_risk_level=case.expected_risk_level,
            actual_risk_level=None,
            risk_match=True,
            expected_signals=case.expected_signals,
            detected_signals=["input_rejected"] if passed else [],
            signal_match_score=1.0 if passed else 0.0,
            safety_passed=True,
            latency_ms=int((time.perf_counter() - started) * 1000),
            error_code=error_code,
            pass_=passed,
            failure_reason=None if passed else f"Expected error code {case.expect_validation_error}",
            workflow_trace=trace,
        )

    try:
        response, trace = _run_traced_analysis(case.input_text)
    except (AnalysisPipelineError, ProviderConfigurationError, ValueError) as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return EvaluationCaseResult(
            case_id=case.id,
            name=case.name,
            category=case.category,
            expected_risk_level=case.expected_risk_level,
            actual_risk_level=None,
            risk_match=False,
            expected_signals=case.expected_signals,
            detected_signals=[],
            signal_match_score=0.0,
            safety_passed=False,
            latency_ms=latency_ms,
            error_code=str(exc),
            pass_=False,
            failure_reason="Analysis workflow failed",
            workflow_trace=trace,
        )

    detected = _detected_signals(response)
    actual_risk: RiskLevel = response.risk_result.risk_level
    signal_score = _signal_match_score(case.expected_signals, detected)
    safety_passed = response.safety_check.passed

    if case.require_no_medication_advice and response.safety_check.contains_medication_advice:
        safety_passed = False
    if case.require_professional_help_wording and not _explanation_mentions_professional_help(
        response.explanation
    ):
        safety_passed = False

    risk_ok = _risk_match(case, actual_risk)
    pass_case = (
        risk_ok
        and safety_passed
        and signal_score >= case.minimum_signal_match_score
    )

    failure_reason = None
    if not pass_case:
        reasons = []
        if not risk_ok:
            reasons.append(f"Expected risk {case.expected_risk_level}, got {actual_risk}")
        if not safety_passed:
            reasons.append("Safety expectations not met")
        if signal_score < case.minimum_signal_match_score:
            reasons.append(f"Signal match score {signal_score} below threshold")
        failure_reason = "; ".join(reasons)

    return EvaluationCaseResult(
        case_id=case.id,
        name=case.name,
        category=case.category,
        expected_risk_level=case.expected_risk_level,
        actual_risk_level=actual_risk,
        risk_match=risk_ok,
        expected_signals=case.expected_signals,
        detected_signals=detected,
        signal_match_score=signal_score,
        safety_passed=safety_passed,
        latency_ms=int((time.perf_counter() - started) * 1000),
        error_code=None,
        pass_=pass_case,
        failure_reason=failure_reason,
        workflow_trace=trace,
    )


def run_evaluation_suite(provider: str = "mock") -> EvaluationRunResponse:
    resolved_provider = resolve_evaluation_provider(provider)
    results: list[EvaluationCaseResult] = []

    with provider_context(resolved_provider):
        for case in EVALUATION_CASES:
            results.append(_evaluate_case(case))

    total = len(results)
    passed = sum(1 for result in results if result.pass_)
    safety_passed_count = sum(1 for result in results if result.safety_passed)
    risk_match_count = sum(1 for result in results if result.risk_match)
    avg_latency = int(sum(result.latency_ms for result in results) / total) if total else 0
    avg_signal = round(sum(result.signal_match_score for result in results) / total, 2) if total else 0.0

    summary = EvaluationSummary(
        total_cases=total,
        passed=passed,
        failed=total - passed,
        pass_rate=round(passed / total, 3) if total else 0.0,
        safety_pass_rate=round(safety_passed_count / total, 3) if total else 0.0,
        average_latency_ms=avg_latency,
        risk_match_rate=round(risk_match_count / total, 3) if total else 0.0,
        average_signal_match_score=avg_signal,
    )

    return EvaluationRunResponse(
        suite=EVALUATION_SUITE_VERSION,
        provider=resolved_provider,
        app_version=APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        results=results,
    )
