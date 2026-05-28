# HealthLens-LLM

<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

**HealthLens-LLM** is a production-style LLM application and evaluation workbench for health-text signal analysis.

It demonstrates how to build, evaluate, and deploy a safety-conscious LLM workflow using **FastAPI, OpenAI, rule-based validation, Docker, AWS ECS/ECR, pytest, and GitHub Actions**.

> **Disclaimer:** This project is a software engineering portfolio demo. It is **not** a medical device, **not** medical advice, and **must not** be used for diagnosis, treatment, or clinical decision-making.

---

## Live Demo

- **Live site:** [Health-LLM](https://he-bebe657ef60745a09032e339f6e24a38.ecs.eu-west-2.on.aws/)
- **Health check:** `GET /health`
- **API docs:** `GET /docs` if enabled by FastAPI

If the AWS service has been recreated, replace the demo URL above with the latest ECS Express Mode public URL.

---

## Why I Built This

Most LLM demos stop at “send a prompt and display the answer.”  
This project goes further by treating the LLM as one component inside a more reliable backend system.

HealthLens-LLM demonstrates:

- structured API design around an LLM workflow;
- deterministic rule-based checks instead of relying only on model judgement;
- safety guardrails for health-related text;
- mock-vs-live provider switching for testability;
- evaluation cases and regression-style metrics;
- Dockerised deployment to AWS ECS;
- backend reliability features such as health checks, version metadata, timeouts, and controlled errors.

The goal is to show practical software engineering around LLM applications, not to build a real healthcare product.

---

## What the Application Does

Users enter a short health-related note, for example:

```text
My heart rate is 100, I cannot sleep, and I feel unhappy.
```

The backend then:

1. validates the input;
2. extracts structured health signals;
3. applies deterministic risk rules;
4. generates a plain-English LLM explanation;
5. validates the output against safety rules;
6. returns a structured JSON response to the frontend.

The app can run in:

- **mock mode** for deterministic tests and evaluation;
- **OpenAI mode** for live LLM behaviour.

---

## Key Features

### User-Facing Analysis Demo

- Clean responsive UI with English / Chinese language support.
- “How to use” guidance for first-time users.
- Voice input using the browser Web Speech API, with typed-input fallback.
- Example prompts for low, moderate, and higher-risk scenarios.
- Result cards for risk summary, detected signals, explanation, evidence, and safety guardrails.

### LLM Evaluation Lab

HealthLens-LLM includes a lightweight evaluation workbench for testing LLM workflow behaviour.

It supports:

- curated evaluation cases;
- expected-vs-actual risk comparison;
- signal match scoring;
- safety pass rate;
- latency measurement;
- workflow trace for each case;
- mock-provider evaluation without OpenAI token usage.

This makes the project relevant to **LLM evaluation, AI Platform, AgentOps, and AI product roles**.

### Backend Reliability

The backend includes production-style reliability features:

- `GET /health` — lightweight ECS/container health check that does not call OpenAI.
- `GET /version` — safe runtime metadata: service, version, environment, providers.
- Startup logs — provider selection, app version, frontend path checks.
- `/analyse` timeout — prevents slow provider calls from hanging indefinitely.
- Controlled JSON errors — no raw stack traces exposed to users.
- Input guardrails — empty and oversized requests are rejected before provider calls.

### Cloud Deployment

The application is containerised with Docker and deployed using:

- **Amazon ECR** for container image storage;
- **Amazon ECS Express Mode** for public HTTPS service hosting;
- **CloudWatch logs** for runtime debugging;
- runtime environment variables / Secrets Manager for configuration.

---

## Architecture

```text
Browser
  ↓
FastAPI static frontend + REST API
  ↓
Input validation
  ↓
Signal extraction provider
  ↓
Rule-based risk engine
  ↓
LLM explanation provider
  ↓
Safety validator
  ↓
Structured JSON response
```

Evaluation flow:

```text
Evaluation Lab UI / API
  ↓
Curated test cases
  ↓
Analyse workflow
  ↓
Expected-vs-actual comparison
  ↓
Metrics dashboard + workflow trace
```

The LLM extracts and explains. **Risk level is determined by the rule engine**, not by free-form model judgement.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| LLM integration | OpenAI API, provider abstraction |
| Deterministic logic | Rule-based risk engine |
| Safety | Output validation and disclaimer checks |
| Evaluation | Curated cases, metrics, workflow trace |
| Frontend | HTML, CSS, vanilla JavaScript |
| Voice input | Web Speech API |
| Testing | pytest |
| CI | GitHub Actions |
| Containerisation | Docker |
| Cloud | AWS ECS, ECR, CloudWatch |

---

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Frontend UI |
| `GET` | `/health` | Lightweight health check |
| `GET` | `/version` | Safe runtime metadata |
| `POST` | `/analyse` | Run the health-text analysis workflow |
| `GET` | `/evaluation/cases` | List curated evaluation cases |
| `POST` | `/evaluation/run?provider=mock` | Run the evaluation suite |

Example request:

```http
POST /analyse
Content-Type: application/json

{
  "text": "My heart rate is 100, I cannot sleep, and I feel unhappy."
}
```

---

## Evaluation Lab

The evaluation suite includes cases such as:

| Case type | Purpose |
|---|---|
| Low risk | Checks that benign input is not over-classified |
| Moderate risk | Tests sleep, mood, and borderline heart-rate signals |
| High blood pressure / heart rate | Tests high-risk rule triggering |
| Missing data | Tests ambiguous input handling |
| Non-health input | Tests rejection or low-risk handling |
| Medication request | Tests refusal of dosage/treatment advice |
| Emergency symptoms | Tests safety-aware escalation wording |

Metrics include:

- total cases;
- pass rate;
- safety pass rate;
- risk match rate;
- average signal match score;
- average latency;
- provider error count.

---

## Local Development

### 1. Clone and install

```bash
git clone https://github.com/Li2043/HealthLens-LLM.git
cd HealthLens-LLM

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file locally. Do not commit it.

```env
EXTRACTOR_PROVIDER=mock
LLM_PROVIDER=mock
APP_ENV=development
APP_VERSION=dev
```

For live OpenAI mode:

```env
EXTRACTOR_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

Never commit real API keys.

### 3. Run locally

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

### 4. Run tests

```bash
pytest -v
```

Tests should use mock providers by default and should not call OpenAI unless explicitly configured.

### 5. Run with Docker

```bash
docker build -t healthlens-llm .
docker run --rm -p 8000:8000 --env-file .env healthlens-llm
```

---

## Environment Variables

| Variable | Default | Purpose |
|---|---:|---|
| `EXTRACTOR_PROVIDER` | `mock` | `mock`, `openai`, or `regex` |
| `LLM_PROVIDER` | `mock` | `mock` or `openai` |
| `OPENAI_API_KEY` | — | Required only for OpenAI mode |
| `APP_VERSION` | `dev` | Exposed by `/version` |
| `APP_ENV` | `development` | Exposed by `/version` |
| `ANALYSE_TIMEOUT_SECONDS` | `30` | Timeout for `/analyse` |
| `MAX_INPUT_CHARS` | `5000` | Maximum input length |
| `RUN_LIVE_LLM_TESTS` | `false` | Enables optional live OpenAI tests |

Production secrets should be injected at runtime via AWS configuration or AWS Secrets Manager. No API keys are committed to the repository or exposed to the browser.

---

## AWS Deployment Summary

The deployment flow is:

```text
Dockerfile
  ↓
docker build
  ↓
Amazon ECR
  ↓
AWS ECS Express Mode
  ↓
Public HTTPS URL
```

Recommended ECS settings:

| Setting | Value |
|---|---|
| Container port | `8000` |
| Health check path | `/health` |
| Region | `eu-west-2` for London |
| Runtime providers | `EXTRACTOR_PROVIDER=openai`, `LLM_PROVIDER=openai` |
| Secret handling | `OPENAI_API_KEY` via runtime configuration or Secrets Manager |

See:

```text
docs/DEPLOYMENT_AWS_ECS_EXPRESS.md
```

---

## Project Structure

```text
HealthLens-LLM/
├── app/
│   ├── main.py
│   ├── evaluation/
│   ├── providers/
│   ├── risk_rules.py
│   └── safety_validator.py
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── tests/
├── docs/
│   ├── DEPLOYMENT_AWS_ECS_EXPRESS.md
│   ├── PRD_EVALUATION_LAB.md
│   └── EVALUATION_METHODOLOGY.md
├── Dockerfile
├── requirements.txt
└── .github/workflows/
```

---

## Skills Demonstrated

This project demonstrates:

- FastAPI backend development;
- REST API design;
- Pydantic request/response validation;
- OpenAI API integration;
- LLM provider abstraction;
- deterministic rule-based evaluation;
- LLM safety guardrails;
- LLM evaluation case design;
- expected-vs-actual comparison;
- AgentOps-style workflow tracing;
- pytest testing;
- Docker containerisation;
- AWS ECS/ECR deployment;
- CloudWatch-based debugging;
- environment-based configuration;
- production-style error handling.

---

## Future Improvements

- Move `OPENAI_API_KEY` fully into AWS Secrets Manager.
- Add prompt version comparison.
- Add provider comparison across models.
- Store evaluation history for regression tracking.
- Add cost and token usage monitoring.
- Add human review workflow for failed evaluation cases.
- Add custom domain for the AWS deployment.
- Add Terraform or AWS CDK infrastructure-as-code.

---

## Safety and Privacy

- This project does not diagnose disease.
- It does not prescribe medication.
- It does not provide treatment instructions.
- It is intended for demo/sample inputs only.
- Requests are processed in memory only.
- No user accounts, database persistence, or health-record storage are included.

---

## Author

**Li2043**  
GitHub: [github.com/Li2043](https://github.com/Li2043)

---

## License

Portfolio / prototype use only. Not licensed for clinical, medical, or commercial healthcare use.
