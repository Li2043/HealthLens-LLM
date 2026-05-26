# HealthLens-LLM

**HealthLens-LLM** is a portfolio-ready software engineering prototype that demonstrates how to build a safe health-input workflow with LLM assistance. It parses free-text health signals, applies transparent rule-based checks, generates LLM explanations, validates output safety, and ships with automated tests and CI/CD.

> **Disclaimer:** This is **not** a medical device, **not** medical advice, and **must not** be used for real clinical decisions. Use demo/sample inputs only. No personal health data is stored.

---

## 项目简介 / Project Purpose

HealthLens-LLM 展示一种可测试、可演示的健康信息处理流水线：

1. **Extract（结构化提取）** — 使用 LLM（或 mock 提供者）将自由文本转换为结构化 JSON  
2. **Evaluate（规则评估）** — 透明规则引擎计算 risk flags 与 risk level  
3. **Explain（结果解释）** — LLM 用通俗语言解释规则结果  
4. **Validate（安全校验）** — 检查输出是否包含免责声明，是否出现诊断或用药建议  

**核心设计原则：** LLM 负责提取与解释；**风险判定始终由规则引擎完成**，LLM 不独立做医疗决策。

This project is designed for:

- Portfolio demonstrations of Python backend workflow automation  
- LLM safety testing patterns (disclaimer checks, prohibited phrase detection)  
- CI-friendly deterministic mock providers for reproducible demos and tests  

---

## Architecture

```
User input (free text)
        │
        ▼
┌───────────────────┐
│  Health Extractor │  mock | openai | regex fallback
└─────────┬─────────┘
          ▼
┌───────────────────┐
│   Rule Engine     │  flags + risk level (deterministic)
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  LLM Explanation  │  mock | openai
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Safety Validator  │  disclaimer + diagnostic/medication checks
└─────────┬─────────┘
          ▼
     JSON response
```

All processing happens **in memory only**. Nothing is persisted to a database or disk.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, Pydantic |
| Extraction | MockLLMExtractor, OpenAILLMExtractor, RegexFallbackExtractor |
| Risk engine | Rule-based flags (`risk_rules.py`) |
| Explanation | MockLLMService, OpenAILLMService |
| Safety | Regex phrase validation (`safety_validator.py`) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Testing | pytest (26 tests, live OpenAI tests optional) |
| CI/CD | GitHub Actions |

---

## Quick Start

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

### 2. Run the web demo

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and try the sample buttons (Low / Moderate / High / Single BP 200).

### 3. Run tests

```bash
pytest -v
```

---

## Environment Variables

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `EXTRACTOR_PROVIDER` | `mock` | `mock`, `openai`, or `regex` |
| `LLM_PROVIDER` | `mock` | `mock` or `openai` |
| `OPENAI_API_KEY` | — | Required for OpenAI providers |
| `RUN_LIVE_LLM_TESTS` | `false` | Set `true` to run optional live OpenAI tests |

If `EXTRACTOR_PROVIDER=openai` but the API key is missing, the app falls back to the mock extractor and returns a `provider_warning`.

---

## API Example

**Request**

```http
POST /analyse
Content-Type: application/json

{
  "text": "My blood pressure is 200"
}
```

**Response (abbreviated)**

```json
{
  "structured_input": {
    "systolic_bp": 200,
    "diastolic_bp": null,
    "missing_or_ambiguous_fields": ["diastolic_bp"],
    "extraction_confidence": "medium"
  },
  "risk_result": {
    "risk_level": "high",
    "flags": ["very_high_systolic_bp", "elevated_blood_pressure", "incomplete_measurement"]
  },
  "extractor_provider": "mock",
  "llm_provider": "mock"
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
│   ├── extractor.py        # LLM-assisted structured extraction
│   ├── risk_rules.py       # Rule-based risk engine
│   ├── llm_service.py      # LLM explanation layer
│   ├── safety_validator.py # Output safety checks
│   ├── parser.py           # Regex fallback parser
│   └── main.py             # FastAPI application
├── frontend/               # Static demo UI
├── tests/                  # pytest suite
├── .github/workflows/      # CI pipeline
├── requirements.txt
└── .env.example
```

---

## Safety & Privacy

- Does **not** diagnose disease or prescribe medication  
- Always includes *"This is not a medical diagnosis"* in explanations  
- Processes requests **in memory only** — no database, no user accounts, no history  
- Intended for **demo/sample inputs** in portfolio and engineering contexts  

---

## Roadmap

- Voice input  
- Secure user history  
- Encrypted database storage  
- Cloud deployment (e.g. AWS)  
- Stronger LLM evaluation / red-teaming  
- Frontend UX improvements  

---

## Author

**Li2043** — [github.com/Li2043](https://github.com/Li2043)

---

## License

Prototype / portfolio use only. Not licensed for clinical or medical use.
