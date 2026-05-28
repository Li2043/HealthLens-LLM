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
- [ ] Push image to ECR
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
