# HealthLens-LLM Evaluation Lab

## 1. Background

HealthLens-LLM already demonstrates a user-facing health text analysis workflow. The Evaluation Lab extends the project into a lightweight LLM evaluation workbench suitable for portfolio review, regression testing, and safety inspection.

## 2. Target users

- LLM application developer
- AI product manager
- Safety reviewer
- Platform evaluator

## 3. User problems

- Hard to know if prompt or provider changes improve or degrade output
- Hard to compare expected vs actual LLM behaviour
- Hard to evaluate safety compliance consistently
- Hard to identify which workflow step failed

## 4. Product goals

- Provide curated evaluation cases
- Run repeatable mock-provider evaluation
- Show pass/fail metrics
- Show safety guardrail results
- Show workflow trace per case

## 5. Non-goals

- Not a real medical risk tool
- Not a clinical decision system
- Not a large-scale benchmarking platform

## 6. Metrics

- Pass rate
- Safety pass rate
- Risk match rate
- Signal match score
- Average latency
- Error rate

## 7. MVP scope

- Curated case library in code
- `GET /evaluation/cases`
- `POST /evaluation/run?provider=mock`
- Summary metrics and per-case results
- Workflow trace per case
- Evaluation Lab tab in the frontend

## 8. Future improvements

- Human review workflow
- Prompt version comparison
- Provider comparison
- Cost tracking
- Dataset upload
- Regression history over time

## 9. Safety and privacy considerations

- Evaluation uses demo text only
- Mock provider mode is the default
- No personal health data is stored
- OpenAI mode is optional and requires explicit configuration
- Medical disclaimer remains visible in the product demo
