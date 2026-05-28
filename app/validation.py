"""Shared request validation helpers."""

from app import config
from app.errors import EMPTY_INPUT_ERROR, INPUT_TOO_LARGE_ERROR


def validate_analysis_input(text: str):
    if not text.strip():
        return EMPTY_INPUT_ERROR
    if len(text) > config.MAX_INPUT_CHARS:
        return INPUT_TOO_LARGE_ERROR
    return None
