"""Controlled API error responses."""

from fastapi.responses import JSONResponse


class ProviderConfigurationError(Exception):
    """Raised when a configured provider is not properly set up."""


class AnalysisPipelineError(Exception):
    """Raised when the analysis pipeline fails in a provider-dependent way."""


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


EMPTY_INPUT_ERROR = error_response(
    "EMPTY_INPUT",
    "Please enter some health-related text to analyse.",
    400,
)

INPUT_TOO_LARGE_ERROR = error_response(
    "INPUT_TOO_LARGE",
    "The input is too long. Please shorten it and try again.",
    413,
)

ANALYSIS_TIMEOUT_ERROR = error_response(
    "ANALYSIS_TIMEOUT",
    "The analysis request timed out. Please try again with a shorter input.",
    504,
)

ANALYSIS_FAILED_ERROR = error_response(
    "ANALYSIS_FAILED",
    "The analysis service is temporarily unavailable. Please try again later.",
    503,
)

PROVIDER_CONFIGURATION_ERROR = error_response(
    "PROVIDER_CONFIGURATION_ERROR",
    "The analysis service is not fully configured.",
    503,
)
