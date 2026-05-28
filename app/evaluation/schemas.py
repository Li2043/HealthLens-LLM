from typing import Literal, Optional

from pydantic import BaseModel, Field

TraceStatus = Literal["passed", "failed", "skipped"]


class WorkflowTraceStep(BaseModel):
    step: str
    status: TraceStatus
    duration_ms: int = 0
    note: Optional[str] = None


class EvaluationCasePublic(BaseModel):
    id: str
    name: str
    category: str
    input_text: str
    expected_risk_level: str
    expected_signals: list[str]
    expected_safety_behaviour: str
    notes: str


class EvaluationCaseResult(BaseModel):
    case_id: str
    name: str
    category: str
    expected_risk_level: str
    actual_risk_level: Optional[str] = None
    risk_match: bool = False
    expected_signals: list[str]
    detected_signals: list[str] = Field(default_factory=list)
    signal_match_score: float = 0.0
    safety_passed: bool = False
    latency_ms: int = 0
    error_code: Optional[str] = None
    pass_: bool = Field(alias="pass", default=False)
    failure_reason: Optional[str] = None
    workflow_trace: list[WorkflowTraceStep] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class EvaluationSummary(BaseModel):
    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    safety_pass_rate: float
    average_latency_ms: int
    risk_match_rate: float
    average_signal_match_score: float


class EvaluationRunResponse(BaseModel):
    suite: str
    provider: str
    app_version: str
    timestamp: str
    summary: EvaluationSummary
    results: list[EvaluationCaseResult]
