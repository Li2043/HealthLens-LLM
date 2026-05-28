# HealthLens-LLM

**HealthLens-LLM** is a portfolio-ready software engineering prototype that demonstrates how to build a safe health-input workflow with LLM assistance. It parses free-text health signals, applies transparent rule-based checks, generates LLM explanations, validates output safety, and ships with automated tests, Docker, and CI/CD.

> **Disclaimer:** This is **not** a medical device, **not** medical advice, and **must not** be used for real clinical decisions. Use demo/sample inputs only. No personal health data is stored.

---

## Live Demo

Live demo: [pending AWS ECS Express Mode deployment](https://he-bebe657ef60745a09032e339f6e24a38.ecs.eu-west-2.on.aws/)

---

## Architecture

```
Browser -> FastAPI frontend/API -> OpenAI extraction/explanation -> rule engine -> safety validator -> JSON response
```

Detailed pipeline:

1. **Extract** — LLM or mock provider converts free text into structured JSON
2. **Evaluate** — rule engine calculates risk flags and risk level
3. **Explain** — LLM describes rule-based results in plain language
4. **Validate** — safety checks block diagnostic or medication language

The LLM extracts and explains. **Risk level is always determined by the rule engine.**

All processing happens **in memory only**. Nothing is persisted to a database or disk.

---

## Portfolio Skills Demonstrated

- Python
- FastAPI
- Pydantic
- REST API design
- Docker
- AWS ECS / ECR
- CI with GitHub Actions
- Testing with pytest
- Environment-based configuration
- LLM safety validation

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, Pydantic |
| Extraction | MockLLMExtractor, OpenAILLMExtractor, RegexFallbackExtractor |
| Risk engine | Rule-based flags (`risk_rules.py`) |
| Explanation | MockLLMService, OpenAILLMService |
| Safety | Regex phrase validation (`safety_validator.py`) |
| Frontend | HTML, CSS, vanilla JavaScript served by FastAPI |
| Voice input | Browser-based speech-to-text via Web Speech API (typed-input fallback) |
| Container | Docker |
| Testing | pytest |
| CI/CD | GitHub Actions |

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Li2043/HealthLens----LLM.git
cd HealthLens----LLM
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the web demo

```bash
uvicorn app.main:app --reload --env-file .env
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

Browser-based speech-to-text input using the Web Speech API, with typed-input fallback for unsupported browsers. Click the microphone button near the text area to dictate demo input in the browser. No audio is sent to the backend.

### 3. Run tests

```bash
pytest -v
```

### 4. Run with Docker

```bash
docker build -t healthlens-llm .
docker run --rm -p 8000:8000 --env-file .env healthlens-llm
```

Health check:

```bash
curl http://localhost:8000/health
```

---

## AWS Deployment

See [docs/DEPLOYMENT_AWS_ECS_EXPRESS.md](docs/DEPLOYMENT_AWS_ECS_EXPRESS.md) for:

- Docker build and local test commands
- pushing the image to Amazon ECR
- running the app with ECS Express Mode over HTTPS
- setting runtime environment variables safely in AWS

---

## Environment Variables

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `EXTRACTOR_PROVIDER` | `mock` | `mock`, `openai`, or `regex` |
| `LLM_PROVIDER` | `mock` | `mock` or `openai` |
| `OPENAI_API_KEY` | — | Required for OpenAI providers; set in AWS for production |
| `APP_VERSION` | `dev` | Release label exposed by `/version` |
| `APP_ENV` | `development` | Environment label exposed by `/version` |
| `ANALYSE_TIMEOUT_SECONDS` | `30` | Max seconds before `/analyse` returns HTTP 504 |
| `MAX_INPUT_CHARS` | `5000` | Maximum accepted input length for `/analyse` |
| `RUN_LIVE_LLM_TESTS` | `false` | Set `true` to run optional live OpenAI tests |

Never commit `.env` or real API keys.

---

## Backend reliability

Production-style deployment improvements for observability and safer failure handling:

- **`GET /health`** — Lightweight container health check for ECS and load balancers. Returns static JSON only; does not call OpenAI, run the analysis pipeline, or check external APIs.
- **`GET /version`** — Exposes safe runtime metadata: service name, `APP_VERSION`, `APP_ENV`, and configured extractor/LLM providers. Never includes secrets such as `OPENAI_API_KEY`.
- **Startup logs** — On container start, logs app version, environment, provider selection, and whether the frontend index file exists (including the static directory path). Logs go to stdout for AWS CloudWatch. Secrets are never logged.
- **`POST /analyse` timeout** — Controlled by `ANALYSE_TIMEOUT_SECONDS` (default 30). Slow provider calls return HTTP 504 with a stable JSON error instead of hanging indefinitely.
- **Provider failure handling** — OpenAI/provider exceptions are logged server-side with stack traces but return controlled JSON errors (`ANALYSIS_FAILED`, `PROVIDER_CONFIGURATION_ERROR`) without exposing raw exception text to clients.
- **Input guardrails** — Empty or whitespace-only input returns HTTP 400 (`EMPTY_INPUT`). Input longer than `MAX_INPUT_CHARS` returns HTTP 413 (`INPUT_TOO_LARGE`).

These changes support production-style deployment, observability, and safer failure handling while keeping successful mock-provider analysis behaviour compatible with the existing frontend.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Frontend UI |
| `GET` | `/health` | Lightweight container health check (no OpenAI calls) |
| `GET` | `/version` | Safe runtime metadata (version, environment, providers) |
| `POST` | `/analyse` | Run extraction, rules, explanation, and safety validation |

**Example**

```http
POST /analyse
Content-Type: application/json

{
  "text": "My blood pressure is 200"
}
```

---

## Example Demo Scenarios

| Input | Extracted | Risk | Key flags |
|-------|-----------|------|-----------|
| `My blood pressure is 200` | systolic 200 | **high** | very_high_systolic_bp, incomplete_measurement |
| `My heart rate is 100, I can not sleep, I am unhappy` | HR 100, mood low, sleep poor | **moderate** | borderline_heart_rate, low_mood, poor_sleep |
| `My heart rate is 125, blood pressure is 150/95, I feel anxious and I cannot sleep` | full vitals + mood/sleep | **high** | very_elevated_heart_rate, elevated BP, anxiety, poor_sleep |

---

## Project Structure

```
HealthLens-LLM/
├── app/
├── frontend/
├── tests/
├── docs/
│   └── DEPLOYMENT_AWS_ECS_EXPRESS.md
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── .github/workflows/ci.yml
```

---

## Safety & Privacy

- Does **not** diagnose disease or prescribe medication
- Always includes *"This is not a medical diagnosis"* in explanations
- Processes requests **in memory only** — no database, no user accounts, no history
- Intended for **demo/sample inputs** in portfolio and engineering contexts

---

## Author

**Li2043** — [github.com/Li2043](https://github.com/Li2043)

---

## License

Prototype / portfolio use only. Not licensed for clinical or medical use.
