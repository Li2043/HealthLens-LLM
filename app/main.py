"""HealthSignal Workflow — FastAPI application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.extractor import get_extractor
from app.llm_service import get_llm_provider_name, get_llm_service
from app.risk_rules import evaluate_risk
from app.safety_validator import validate_llm_output
from app.schemas import AnalysisResponse, HealthInputRequest

app = FastAPI(
    title="HealthLens-LLM",
    description="Prototype health-input workflow automation. Not medical advice.",
    version="0.3.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/health")
async def health() -> dict[str, str]:
    """Lightweight health check for load balancers and container orchestration."""
    return {"status": "ok", "service": "healthlens-llm"}


@app.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.post("/analyse", response_model=AnalysisResponse)
async def analyse(request: HealthInputRequest) -> AnalysisResponse:
    """
    Analyse demo health text in memory only. No data is stored.

    Pipeline: extract -> rule-based risk -> LLM explanation -> safety validation.
    """
    extractor, extractor_provider, provider_warning = get_extractor()
    structured = extractor.extract(request.text)
    risk_result = evaluate_risk(structured, request.text)

    llm = get_llm_service()
    explanation = llm.generate_explanation(structured, risk_result, request.text)
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
