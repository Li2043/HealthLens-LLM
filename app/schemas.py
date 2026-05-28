from typing import Literal, Optional

from pydantic import BaseModel, Field

MoodValue = Literal["anxious", "stressed", "low", "calm", "unknown"]
SleepQualityValue = Literal["good", "poor", "unknown"]
ExtractionConfidence = Literal["high", "medium", "low"]
MeasurementStatus = Literal["absent", "partial", "complete", "ambiguous"]
RiskLevel = Literal["low", "moderate", "high"]


class HealthInputRequest(BaseModel):
    text: str = Field(..., description="Free-text health input (demo/sample only)")


class FieldEvidence(BaseModel):
    field: str
    value: Optional[str] = None
    evidence: Optional[str] = None
    status: MeasurementStatus


class StructuredHealthInput(BaseModel):
    heart_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    mood: Optional[MoodValue] = None
    sleep_quality: Optional[SleepQualityValue] = None
    symptoms: list[str] = Field(default_factory=list)
    extraction_confidence: ExtractionConfidence = "low"
    missing_or_ambiguous_fields: list[str] = Field(default_factory=list)
    extraction_notes: Optional[str] = None
    extraction_evidence: list[FieldEvidence] = Field(default_factory=list)


class RiskResult(BaseModel):
    risk_level: RiskLevel
    flags: list[str]
    rule_explanation: str


class SafetyCheck(BaseModel):
    contains_disclaimer: bool
    contains_diagnostic_language: bool
    contains_medication_advice: bool
    passed: bool


class AnalysisResponse(BaseModel):
    structured_input: StructuredHealthInput
    risk_result: RiskResult
    explanation: str
    safety_check: SafetyCheck
    extractor_provider: str
    llm_provider: str
    provider_warning: Optional[str] = None
