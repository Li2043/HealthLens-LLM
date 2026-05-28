# Evaluation Methodology

## Test case selection

The Evaluation Lab uses a small curated suite of 10 cases covering:

- Low, moderate, and high risk vitals
- Ambiguous or missing data
- Non-health scope input
- Safety-sensitive medication requests
- Emergency-style symptom wording
- Input length guardrails
- Partial or qualitative blood pressure mentions

Cases are defined in code (`app/evaluation/cases.py`) so they are easy to inspect and version.

## Expected outputs

Each case defines:

- Expected risk level (with optional acceptable alternatives)
- Expected signals such as rule flags or semantic markers
- Expected safety behaviour
- Notes explaining the intent of the case

Expected outputs describe engineering expectations for the current rule engine and safety validator, not clinical truth.

## Risk match scoring

A case passes risk matching when the actual risk level equals the expected level, or falls within the case's acceptable risk list when provided.

## Signal match score

Signal match score is calculated as:

`matched expected signals / total expected signals`

Some expected signals are semantic markers such as `no_health_signals` or `no_medication_advice`. The runner treats these with lightweight compatibility rules so the score reflects intent rather than exact string equality only.

## Safety evaluation

Safety pass uses the existing `validate_llm_output()` result plus case-specific requirements such as:

- No medication advice in the generated explanation
- Professional help wording for emergency-style cases

## Mock provider mode

Mock provider mode is the default because it is:

- Deterministic
- Free of OpenAI token usage
- Suitable for CI and regression testing
- Easier to explain in a portfolio setting

OpenAI mode can be enabled with `?provider=openai` when `OPENAI_API_KEY` is configured, but tests and default UI use mock mode.

## Workflow trace

Each evaluated case records simple step timings for:

1. Input validation
2. Signal extraction
3. Risk rules
4. LLM explanation
5. Safety validation
6. Response formatting

This helps reviewers see where a case succeeded or stopped.

## Limitations

- The rule engine is vitals-focused and does not fully model all symptom language
- Signal scoring is intentionally simple
- The suite is small and curated, not a production benchmark dataset
- Evaluation does not replace human review for real AI product release decisions
