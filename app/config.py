"""Application configuration from environment variables."""

import os

SERVICE_NAME = "healthlens-llm"

APP_VERSION = os.getenv("APP_VERSION", "dev")
APP_ENV = os.getenv("APP_ENV", "development")

EXTRACTOR_PROVIDER = os.getenv("EXTRACTOR_PROVIDER", "mock").lower()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()

ANALYSE_TIMEOUT_SECONDS = float(os.getenv("ANALYSE_TIMEOUT_SECONDS", "30"))
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "5000"))


def is_openai_provider_misconfigured() -> bool:
    """True when OpenAI is requested but no API key is available."""
    if not os.getenv("OPENAI_API_KEY"):
        return EXTRACTOR_PROVIDER == "openai" or LLM_PROVIDER == "openai"
    return False
