import os

import pytest

from app.extractor import OpenAILLMExtractor


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_LLM_TESTS") != "true" or not os.getenv("OPENAI_API_KEY"),
    reason="Live OpenAI tests disabled unless RUN_LIVE_LLM_TESTS=true and OPENAI_API_KEY is set",
)
def test_openai_extractor_live():
    extractor = OpenAILLMExtractor(api_key=os.environ["OPENAI_API_KEY"])
    result = extractor.extract("My blood pressure is 200")

    assert result.systolic_bp == 200
    assert result.diastolic_bp is None
