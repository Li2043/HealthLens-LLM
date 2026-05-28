"""HealthLens-LLM — FastAPI application."""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.analysis import run_analysis
from app.config import (
    ANALYSE_TIMEOUT_SECONDS,
    APP_ENV,
    APP_VERSION,
    EXTRACTOR_PROVIDER,
    LLM_PROVIDER,
    SERVICE_NAME,
    is_openai_provider_misconfigured,
)
from app.errors import (
    ANALYSIS_FAILED_ERROR,
    ANALYSIS_TIMEOUT_ERROR,
    PROVIDER_CONFIGURATION_ERROR,
    AnalysisPipelineError,
    ProviderConfigurationError,
)
from app.evaluation.cases import get_evaluation_cases
from app.evaluation.runner import resolve_evaluation_provider, run_evaluation_suite
from app.evaluation.schemas import EvaluationCasePublic
from app.schemas import HealthInputRequest
from app.validation import validate_analysis_input

logger = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def log_startup() -> None:
    index_exists = FRONTEND_INDEX.is_file()
    logger.info("HealthLens-LLM app started")
    logger.info("App version: %s", APP_VERSION)
    logger.info("Environment: %s", APP_ENV)
    logger.info("Extractor provider: %s", EXTRACTOR_PROVIDER)
    logger.info("LLM provider: %s", LLM_PROVIDER)
    logger.info("Frontend index exists: %s", index_exists)
    logger.info("Static frontend directory: %s", FRONTEND_DIR)
    if is_openai_provider_misconfigured():
        logger.warning(
            "OpenAI provider selected but OPENAI_API_KEY is not set; "
            "extractor/LLM may fall back to mock providers."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log_startup()
    yield


app = FastAPI(
    title="HealthLens-LLM",
    description="Prototype health-input workflow automation. Not medical advice.",
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Lightweight health check for load balancers and container orchestration."""
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/version")
async def version() -> dict[str, str]:
    """Safe runtime metadata for deployment visibility."""
    return {
        "service": SERVICE_NAME,
        "version": APP_VERSION,
        "environment": APP_ENV,
        "extractor_provider": EXTRACTOR_PROVIDER,
        "llm_provider": LLM_PROVIDER,
    }


@app.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_INDEX)


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.post("/analyse")
async def analyse(request: HealthInputRequest):
    """
    Analyse demo health text in memory only. No data is stored.

    Pipeline: extract -> rule-based risk -> LLM explanation -> safety validation.
    """
    validation_error = validate_analysis_input(request.text)
    if validation_error is not None:
        return validation_error

    if is_openai_provider_misconfigured() and APP_ENV.lower() in {"production", "prod"}:
        return PROVIDER_CONFIGURATION_ERROR

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(run_analysis, request.text.strip(), request.language),
            timeout=ANALYSE_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("Analysis request timed out after %s seconds", ANALYSE_TIMEOUT_SECONDS)
        return ANALYSIS_TIMEOUT_ERROR
    except ProviderConfigurationError:
        logger.exception("Analysis provider configuration error")
        return PROVIDER_CONFIGURATION_ERROR
    except AnalysisPipelineError:
        logger.exception("Analysis pipeline failed")
        return ANALYSIS_FAILED_ERROR
    except Exception:
        logger.exception("Unexpected analysis failure")
        return ANALYSIS_FAILED_ERROR


@app.get("/evaluation/cases")
async def list_evaluation_cases() -> list[EvaluationCasePublic]:
    """Return curated evaluation cases without running them."""
    return [
        EvaluationCasePublic(
            id=case.id,
            name=case.name,
            category=case.category,
            input_text=case.input_text,
            expected_risk_level=case.expected_risk_level,
            expected_signals=case.expected_signals,
            expected_safety_behaviour=case.expected_safety_behaviour,
            notes=case.notes,
        )
        for case in get_evaluation_cases()
    ]


@app.post("/evaluation/run")
async def run_evaluation(provider: str = "mock"):
    """
    Run the curated evaluation suite.

    Defaults to mock provider for repeatable, token-free evaluation.
    """
    try:
        resolve_evaluation_provider(provider)
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_PROVIDER", "message": str(exc)}},
        )

    try:
        return await asyncio.to_thread(run_evaluation_suite, provider)
    except Exception:
        logger.exception("Evaluation suite failed")
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "EVALUATION_FAILED",
                    "message": "The evaluation suite could not be completed.",
                }
            },
        )
