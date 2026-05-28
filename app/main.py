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
    MAX_INPUT_CHARS,
    SERVICE_NAME,
    is_openai_provider_misconfigured,
)
from app.errors import (
    ANALYSIS_FAILED_ERROR,
    ANALYSIS_TIMEOUT_ERROR,
    EMPTY_INPUT_ERROR,
    INPUT_TOO_LARGE_ERROR,
    PROVIDER_CONFIGURATION_ERROR,
    AnalysisPipelineError,
    ProviderConfigurationError,
)
from app.schemas import HealthInputRequest

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


def validate_analysis_input(text: str) -> JSONResponse | None:
    if not text.strip():
        return EMPTY_INPUT_ERROR
    if len(text) > MAX_INPUT_CHARS:
        return INPUT_TOO_LARGE_ERROR
    return None


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
            asyncio.to_thread(run_analysis, request.text.strip()),
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
