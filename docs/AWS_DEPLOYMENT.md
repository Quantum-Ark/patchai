# PatchPilot AI — AWS Production Deployment Guide

This guide details how to deploy **PatchPilot AI** onto Amazon Web Services (AWS) using containerized infrastructure with **AWS App Runner** or **AWS ECS Fargate**.

---

## Architecture Overview

PatchPilot AI is packaged as an OCI-compliant container featuring:
- **Web Workbench Interface:** Interactive UI served from `web/` on port `8080`.
- **Cloud Health Probes:** `/health` and `/healthz` endpoints returning HTTP 200 for ALB and App Runner health checkers.
- **Agent API:** `/api/status` for real-time telemetry diagnostics and `/api/repair` for autonomous defect resolution.
- **Zero-Privilege Security:** Runs as non-root user `patchpilot` (UID 1000).

```
                      ┌────────────────────────────────────────┐
                      │             User / Judges              │
                      └──────────────────┬─────────────────────┘
                                         │ HTTPS (Port 443)
                                         ▼
                      ┌────────────────────────────────────────┐
                      │   AWS App Runner / CloudFront + ALB    │
                      └──────────────────┬─────────────────────┘
                                         │ HTTP (Port 8080)
                                         ▼
                      ┌────────────────────────────────────────┐
                      │    PatchPilot AI Container (Fargate)    │
                      │  - Web Workbench (Static Assets)       │
                      │  - Health Check Endpoint (/health)     │
                      │  - Autonomous Agent & Telemetry Engine │
                      └──────────────────┬─────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     ┌───────────────────────┐                       ┌───────────────────────┐
     │ Neatlogs Ingest API   │                       │ Model Gateway / LLM   │
     │ (Telemetry & Spans)   │                       │ (OpenAI/Gemini/Groq)  │
     └───────────────────────┘                       └───────────────────────┘
```

---

## Method 1: Deploy with AWS App Runner (Recommended — Fastest & Easiest)

AWS App Runner provides fully managed container execution, automated TLS certificates, built-in load balancing, and zero infrastructure overhead.

### Step 1: Create an ECR Repository and Push Image
```bash
# 1. Authenticate Docker with Amazon ECR
aws ecr get-login-password --region <AWS_REGION> | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com

# 2. Create the ECR repository (if not already created)
aws ecr create-repository --repository-name patchpilot-ai --region <AWS_REGION>

# 3. Build the container image locally
docker build -t patchpilot-ai .

# 4. Tag the container image
docker tag patchpilot-ai:latest <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/patchpilot-ai:latest

# 5. Push to Amazon ECR
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/patchpilot-ai:latest
```

### Step 2: Create App Runner Service (via AWS Console)
1. Navigate to **AWS App Runner** in the AWS Console.
2. Click **Create service**.
3. Under **Source**:
   - Choose **Container registry** -> **Amazon ECR**.
   - Browse and select `patchpilot-ai:latest`.
   - Deployment settings: Select **Automatic** (deploys whenever a new image is pushed) or **Manual**.
4. Under **Configure service**:
   - **Service name:** `patchpilot-ai`
   - **Virtual CPU:** `1 vCPU`
   - **Memory:** `2 GB`
   - **Port:** `8080`
5. Under **Health check**:
   - **Protocol:** `HTTP`
   - **Path:** `/health`
   - **Interval:** `20 seconds`
   - **Timeout:** `5 seconds`
   - **Healthy threshold:** `1`
   - **Unhealthy threshold:** `5`
6. Under **Environment variables**, configure your credentials:
   - `MODEL`: `gpt-4o-mini` (or your preferred model)
   - `OPENAI_API_KEY`: `<your-openai-key>` (or `GEMINI_API_KEY` / `GROQ_API_KEY`)
   - `NEATLOGS_API_KEY`: `<your-neatlogs-api-key>`
   - `NEATLOGS_PROJECT_ID`: `b0860223-3c80-445d-a3f1-3002c0643197`
7. Click **Create & deploy**. Within ~3 minutes, AWS will generate a public URL (e.g., `https://xxxxxx.us-east-1.awsapprunner.com`).

---

## Method 2: Deploy with AWS ECS Fargate & CloudFormation

For enterprise deployments requiring dedicated VPCs, private subnets, and CloudFormation:

### Step 1: Deploy Infrastructure with CloudFormation
```bash
aws cloudformation deploy \
  --template-file aws/cloudformation.yaml \
  --stack-name patchpilot-production \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <AWS_REGION>
```

### Step 2: Register ECS Task Definition
Edit [`aws/ecs-task-definition.json`](../aws/ecs-task-definition.json) with your AWS Account ID and region, then register:
```bash
aws ecs register-task-definition \
  --cli-input-json file://aws/ecs-task-definition.json \
  --region <AWS_REGION>
```

### Step 3: Run Task or Create Service on Fargate
```bash
aws ecs create-service \
  --cluster patchpilot-cluster-production \
  --service-name patchpilot-service \
  --task-definition patchpilot-ai-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SECURITY_GROUP_ID>],assignPublicIp=ENABLED}" \
  --region <AWS_REGION>
```

---

## Method 3: Automated CI/CD with GitHub Actions

The repository includes [`.github/workflows/deploy-aws.yml`](../.github/workflows/deploy-aws.yml). Every push to `main` executes the 26-test verification suite and automatically deploys the image to AWS.

### Required GitHub Repository Secrets
Navigate to **Settings -> Secrets and variables -> Actions** in your GitHub repository and add:

| Secret Name | Description | Example |
| :--- | :--- | :--- |
| `AWS_ACCESS_KEY_ID` | IAM User Access Key with ECR & AppRunner permissions | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | IAM User Secret Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | Target AWS Region | `us-east-1` |
| `ECR_REPOSITORY` | Amazon ECR Repository Name | `patchpilot-ai` |
| `APP_RUNNER_SERVICE_ARN` | *(Optional)* App Runner Service ARN for auto-trigger | `arn:aws:apprunner:us-east-1:...` |
| `ECS_CLUSTER_NAME` | *(Optional)* ECS Cluster Name for Fargate deployments | `patchpilot-cluster-production` |
| `ECS_SERVICE_NAME` | *(Optional)* ECS Service Name for Fargate deployments | `patchpilot-service` |

---

## Health Check and Verification

Once deployed, verify that the instance is responding:
```bash
# Verify health probe
curl -f https://<YOUR-AWS-ENDPOINT>/health

# Expected JSON response:
# {
#   "status": "healthy",
#   "service": "patchpilot-ai",
#   "version": "0.1.0",
#   "model": "gpt-4o-mini",
#   "neatlogs_configured": true
# }
```
