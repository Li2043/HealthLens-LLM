# AWS ECS Express Mode Deployment Guide

This guide explains how to deploy **HealthLens-LLM** as a containerised portfolio web app on AWS using **Docker**, **Amazon ECR**, and **ECS Express Mode**.

> **Disclaimer:** HealthLens-LLM is a software engineering prototype. It is not a medical device and must not be used for real clinical decisions.

---

## Architecture Overview

```
Browser
  -> FastAPI (frontend + /analyse API)
  -> OpenAI extraction / explanation (optional)
  -> rule engine
  -> safety validator
  -> JSON response
```

The same Docker image serves:

- `GET /` — static frontend
- `GET /static/*` — CSS and JavaScript
- `GET /health` — container health check
- `POST /analyse` — analysis pipeline

---

## Container Overview

The app is packaged with a production-ready `Dockerfile`:

- Base image: `python:3.12-slim`
- Process: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Port: `8000`

Build locally:

```bash
docker build -t healthlens-llm .
```

Run locally with environment variables from `.env` (never commit this file):

```bash
docker run --rm -p 8000:8000 --env-file .env healthlens-llm
```

Open [http://localhost:8000](http://localhost:8000).

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok", "service": "healthlens-llm"}
```

---

## AWS Deployment Flow

### 1. Build and tag the image

```bash
docker build -t healthlens-llm .
```

### 2. Push to Amazon ECR

1. Create an ECR repository, for example `healthlens-llm`.
2. Authenticate Docker to ECR.
3. Tag the image with your ECR URI.
4. Push the image.

Example:

```bash
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-2.amazonaws.com

docker tag healthlens-llm:latest <account-id>.dkr.ecr.eu-west-2.amazonaws.com/healthlens-llm:latest

docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/healthlens-llm:latest
```

### Push Docker image to Amazon ECR from Windows PowerShell

If you are on Windows, use the helper script at `scripts/push_ecr.ps1` to automate the ECR push.

**Prerequisites**

- Docker Desktop installed and running
- AWS CLI v2 installed
- AWS credentials configured locally, for example with `aws configure` or an AWS SSO profile
- No secrets are stored in the script; it uses your existing local AWS identity

**Default settings used by the script**

| Setting | Default |
|---------|---------|
| AWS region | `eu-west-2` |
| ECR repository | `healthlens-llm` |
| Local Docker image | `healthlens-llm` |
| Image tag | `latest` |

You can override defaults with environment variables before running the script:

```powershell
$env:AWS_REGION = "eu-west-2"
$env:ECR_REPOSITORY = "healthlens-llm"
$env:DOCKER_IMAGE_NAME = "healthlens-llm"
$env:IMAGE_TAG = "latest"
```

**Run the script**

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/push_ecr.ps1
```

The script will:

1. Check that Docker and AWS CLI are installed
2. Check that Docker Engine is running
3. Verify your AWS account with `aws sts get-caller-identity`
4. Create the ECR repository if needed
5. Log Docker in to Amazon ECR
6. Build, tag, and push the image
7. Print the final ECR image URI for use in ECS Express Mode

Example output:

```text
ECR image URI:
123456789012.dkr.ecr.eu-west-2.amazonaws.com/healthlens-llm:latest
```

Use that URI when creating or updating your ECS Express Mode service.

**Note:** On Windows PowerShell, a missing ECR repository can write to stderr and look like an error even when the script continues correctly. The helper script handles this case and creates the repository automatically.

### 3. Run with ECS Express Mode

ECS Express Mode is suitable for a portfolio deployment because it:

- Runs the container as a public web service
- Exposes HTTPS automatically
- Avoids managing load balancers manually for a small demo app

High-level steps:

1. Open the AWS ECS console.
2. Create a service using **Express Mode**.
3. Select the ECR image.
4. Set container port `8000`.
5. Configure environment variables in AWS (not in Git).
6. Deploy the service and note the public HTTPS URL.

---

## Runtime Environment Variables

Set these in **AWS task/service configuration**. Never commit real secrets to GitHub.

### OpenAI mode (live demo)

```env
EXTRACTOR_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=<set in AWS Secrets Manager or task env>
```

### Safe demo fallback (no OpenAI billing)

```env
EXTRACTOR_PROVIDER=mock
LLM_PROVIDER=mock
```

If `EXTRACTOR_PROVIDER=openai` is set but `OPENAI_API_KEY` is missing, the app falls back to the mock extractor and returns a `provider_warning` in the API response.

Optional:

```env
RUN_LIVE_LLM_TESTS=false
```

---

## Recommended AWS Settings

| Setting | Value |
|---------|-------|
| Container port | `8000` |
| Health check path | `/health` |
| CPU / memory | Start small, e.g. 0.25 vCPU / 512 MB |
| Public access | Enabled for portfolio demo |
| Secrets | Store `OPENAI_API_KEY` in AWS Secrets Manager or encrypted task env |

ECS Express Mode and load balancers should use **`GET /health`** as the health check path. This endpoint is static and does not call OpenAI.

### Useful runtime environment variables

| Variable | Purpose |
|----------|---------|
| `APP_VERSION` | Release label returned by `/version` |
| `APP_ENV` | Environment label returned by `/version` |
| `EXTRACTOR_PROVIDER` | Extraction backend (`mock`, `openai`, `regex`) |
| `LLM_PROVIDER` | Explanation backend (`mock`, `openai`) |
| `ANALYSE_TIMEOUT_SECONDS` | Max seconds before `/analyse` returns HTTP 504 |
| `MAX_INPUT_CHARS` | Maximum accepted input length for `/analyse` |
| `OPENAI_API_KEY` | OpenAI credential — set only in AWS runtime configuration or Secrets Manager, never committed to Git |

---

## CI/CD Notes

GitHub Actions workflow `CI` currently:

- installs Python dependencies
- runs `pytest -v`
- builds the Docker image locally in CI

It does **not** push images to ECR yet. That keeps AWS credentials out of GitHub until you choose to add a deployment workflow.

---

## Manual Deployment Checklist

- [ ] Build Docker image locally and test with `docker run`
- [ ] Confirm `/health` returns `200`
- [ ] Confirm `/` loads the frontend
- [ ] Confirm `POST /analyse` works with mock providers
- [ ] Create ECR repository
- [ ] Push image to ECR (`scripts/push_ecr.ps1` on Windows, or manual AWS CLI commands)
- [ ] Create ECS Express Mode service
- [ ] Set runtime env vars in AWS
- [ ] Verify public HTTPS URL
- [ ] Update README live demo link

---

## Security Reminders

- Do not commit `.env`
- Do not hardcode `OPENAI_API_KEY`
- Use mock providers for public portfolio demos if you want zero API cost
- This app processes requests in memory only and stores no personal health data
