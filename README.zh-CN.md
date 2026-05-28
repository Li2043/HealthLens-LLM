# HealthLens-LLM

<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

**HealthLens-LLM** 是一个面向求职展示的 LLM 应用与评测工作台，用于演示如何围绕健康文本构建一个安全、可测试、可部署的 AI 工作流。

项目展示了 **FastAPI、OpenAI、规则引擎、安全校验、Docker、AWS ECS/ECR、pytest、GitHub Actions** 等软件工程能力。

> **免责声明：** 本项目仅用于软件工程作品集展示。它**不是**医疗设备，**不构成**医疗建议，不能用于诊断、治疗或任何真实临床决策。

---

## 在线演示

- **Live site:** [HealthLens](https://he-bebe657ef60745a09032e339f6e24a38.ecs.eu-west-2.on.aws/)
- **Health check:** `GET /health`
- **API docs:** 如果 FastAPI 文档开启，可访问 `GET /docs`

如果 AWS 服务被重新创建，请把上面的 URL 替换成最新的 ECS Express Mode 公开地址。

---

## 为什么做这个项目

很多 LLM demo 只是“把用户输入发给模型，然后显示回答”。  
这个项目的重点不是单纯调用大模型，而是把 LLM 放进一个更完整、更可靠的后端系统里。

HealthLens-LLM 展示了：

- 围绕 LLM 工作流设计结构化 API；
- 使用确定性规则引擎，而不是完全依赖模型判断；
- 对健康相关文本加入安全边界和输出校验；
- 支持 mock / OpenAI provider 切换，便于测试和部署；
- 设计评测样例、指标和 workflow trace；
- 使用 Docker 和 AWS ECS 完成云端部署；
- 加入健康检查、版本信息、超时控制、稳定错误响应等 backend reliability 能力。

目标是展示 LLM 应用背后的软件工程能力，而不是构建真实医疗产品。

---

## 应用做了什么

用户输入一段简短的健康相关描述，例如：

```text
My heart rate is 100, I cannot sleep, and I feel unhappy.
```

后端会执行：

1. 输入校验；
2. 提取结构化健康信号；
3. 使用规则引擎判断风险等级；
4. 生成安全的自然语言解释；
5. 对输出进行安全校验；
6. 将结构化 JSON 结果返回给前端。

应用支持两种模式：

- **mock mode**：用于确定性测试和评测，不消耗 OpenAI token；
- **OpenAI mode**：用于真实 LLM 行为测试和在线演示。

---

## 核心功能

### 用户分析 Demo

- 支持英文 / 中文界面切换。
- 有清晰的 “How to use / 如何使用” 引导。
- 支持浏览器语音输入；不支持时回退到手动输入。
- 提供低风险、中等风险、更高风险示例。
- 结果以卡片形式展示：风险总结、检测信号、解释、证据和安全提示。

### LLM Evaluation Lab

HealthLens-LLM 不只是一个 LLM demo，也包含一个轻量级评测工作台。

它支持：

- curated evaluation cases；
- expected-vs-actual 风险等级对比；
- signal match scoring；
- safety pass rate；
- latency measurement；
- 每个 case 的 workflow trace；
- mock-provider evaluation，避免消耗 OpenAI token。

这使项目更适配 **LLM Evaluation、AI Platform、AgentOps、AI 产品** 等岗位方向。

### Backend Reliability

后端加入了更接近生产环境的可靠性设计：

- `GET /health`：轻量健康检查，不调用 OpenAI。
- `GET /version`：暴露安全的运行时元信息，例如 service、version、environment、providers。
- Startup logs：记录 provider、版本、前端路径检查等信息。
- `/analyse` timeout：防止 provider 请求无限等待。
- Controlled JSON errors：错误返回稳定 JSON，不向用户暴露 stack trace。
- Input guardrails：空输入和超长输入会在调用 provider 前被拒绝。

### 云部署

项目使用 Docker 容器化，并部署到：

- **Amazon ECR**：存储 Docker image；
- **Amazon ECS Express Mode**：托管公开 HTTPS 服务；
- **CloudWatch logs**：查看运行日志和排查部署问题；
- 运行时环境变量或 Secrets Manager：管理 OpenAI key 和 provider 配置。

---

## 系统架构

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

评测流程：

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

LLM 负责提取和解释。**风险等级由规则引擎决定**，而不是由模型自由判断。

---

## 技术栈

| 层级 | 技术 |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| LLM 集成 | OpenAI API, provider abstraction |
| 确定性逻辑 | Rule-based risk engine |
| Safety | Output validation, disclaimer checks |
| Evaluation | Curated cases, metrics, workflow trace |
| Frontend | HTML, CSS, vanilla JavaScript |
| Voice input | Web Speech API |
| Testing | pytest |
| CI | GitHub Actions |
| Containerisation | Docker |
| Cloud | AWS ECS, ECR, CloudWatch |

---

## API Endpoints

| Method | Path | 用途 |
|---|---|---|
| `GET` | `/` | 前端页面 |
| `GET` | `/health` | 轻量健康检查 |
| `GET` | `/version` | 安全运行时元信息 |
| `POST` | `/analyse` | 执行健康文本分析工作流 |
| `GET` | `/evaluation/cases` | 查看评测样例 |
| `POST` | `/evaluation/run?provider=mock` | 运行评测套件并返回指标 |

示例请求：

```http
POST /analyse
Content-Type: application/json

{
  "text": "My heart rate is 100, I cannot sleep, and I feel unhappy."
}
```

---

## Evaluation Lab

评测套件包含以下类型：

| Case 类型 | 目的 |
|---|---|
| Low risk | 确认低风险输入不会被过度分类 |
| Moderate risk | 测试睡眠、情绪、边界心率等信号 |
| High BP / heart rate | 测试高风险规则触发 |
| Missing data | 测试模糊输入处理 |
| Non-health input | 测试非健康输入处理 |
| Medication request | 测试拒绝剂量或治疗建议 |
| Emergency symptoms | 测试安全升级提醒 |

评测指标包括：

- total cases；
- pass rate；
- safety pass rate；
- risk match rate；
- average signal match score；
- average latency；
- provider error count。

---

## 本地开发

### 1. 克隆并安装

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

### 2. 配置环境变量

本地创建 `.env` 文件，不要提交到 GitHub。

```env
EXTRACTOR_PROVIDER=mock
LLM_PROVIDER=mock
APP_ENV=development
APP_VERSION=dev
```

如果使用真实 OpenAI：

```env
EXTRACTOR_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

不要提交真实 API key。

### 3. 本地运行

```bash
uvicorn app.main:app --reload
```

打开：

```text
http://127.0.0.1:8000
```

### 4. 运行测试

```bash
pytest -v
```

默认测试应该使用 mock provider，不应调用真实 OpenAI。

### 5. Docker 运行

```bash
docker build -t healthlens-llm .
docker run --rm -p 8000:8000 --env-file .env healthlens-llm
```

---

## 环境变量

| 变量 | 默认值 | 用途 |
|---|---:|---|
| `EXTRACTOR_PROVIDER` | `mock` | `mock`, `openai`, `regex` |
| `LLM_PROVIDER` | `mock` | `mock` 或 `openai` |
| `OPENAI_API_KEY` | — | OpenAI 模式需要 |
| `APP_VERSION` | `dev` | `/version` 返回的版本 |
| `APP_ENV` | `development` | `/version` 返回的环境 |
| `ANALYSE_TIMEOUT_SECONDS` | `30` | `/analyse` 超时时间 |
| `MAX_INPUT_CHARS` | `5000` | 最大输入长度 |
| `RUN_LIVE_LLM_TESTS` | `false` | 是否开启真实 OpenAI 测试 |

生产环境密钥应通过 AWS runtime configuration 或 AWS Secrets Manager 注入。不要把 API key 提交到仓库，也不要暴露到浏览器端。

---

## AWS 部署概要

部署流程：

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

推荐 ECS 配置：

| 配置 | 值 |
|---|---|
| Container port | `8000` |
| Health check path | `/health` |
| Region | `eu-west-2` for London |
| Runtime providers | `EXTRACTOR_PROVIDER=openai`, `LLM_PROVIDER=openai` |
| Secret handling | `OPENAI_API_KEY` via runtime configuration or Secrets Manager |

详细文档见：

```text
docs/DEPLOYMENT_AWS_ECS_EXPRESS.md
```

---

## 项目结构

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

## 展示的能力

本项目展示：

- FastAPI 后端开发；
- REST API 设计；
- Pydantic 请求/响应校验；
- OpenAI API 集成；
- LLM provider abstraction；
- 确定性规则评估；
- LLM safety guardrails；
- LLM evaluation case design；
- expected-vs-actual comparison；
- AgentOps-style workflow tracing；
- pytest 测试；
- Docker 容器化；
- AWS ECS/ECR 部署；
- CloudWatch 调试；
- 环境变量配置；
- production-style error handling。

---

## 后续改进

- 将 `OPENAI_API_KEY` 完整迁移到 AWS Secrets Manager。
- 增加 prompt version comparison。
- 增加不同模型/provider 对比。
- 保存 evaluation history，用于 regression tracking。
- 加入 token cost 和 usage monitoring。
- 增加 human review workflow。
- 为 AWS 服务绑定 custom domain。
- 使用 Terraform 或 AWS CDK 管理基础设施。

---

## 安全与隐私

- 不诊断疾病。
- 不开药或给出剂量建议。
- 不提供治疗指令。
- 仅用于 demo/sample inputs。
- 请求仅在内存中处理。
- 不包含用户账号、数据库持久化或健康记录存储。

---

## 作者

**Li2043**  
GitHub: [github.com/Li2043](https://github.com/Li2043)

---

## License

仅用于作品集 / 原型展示。不得用于临床、医疗或商业医疗用途。
