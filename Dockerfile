# ==============================================================================
# PatchPilot AI — Production Dockerfile for AWS App Runner & ECS Fargate
# neatHacks 2026 Submission
# ==============================================================================

FROM python:3.12-slim-bookworm AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    HOST=0.0.0.0 \
    DEBIAN_FRONTEND=noninteractive

# Install Git and Curl for repository inspection, diffing, and health probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Configure security: create a dedicated non-root application user
RUN useradd -m -u 1000 -s /bin/bash patchpilot

WORKDIR /app

# Install Python package dependencies first for layer caching
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code, web interface, benchmarks, and tests
COPY src/ ./src/
COPY web/ ./web/
COPY benchmarks/ ./benchmarks/
COPY tests/ ./tests/
COPY README.md SUBMISSION_EVIDENCE.md BUSINESS_PLAN.md ./

# Install patchpilot in editable/standard package mode
RUN pip install --no-cache-dir -e .

# Ensure storage directories are owned by patchpilot user
RUN mkdir -p /app/artifacts /app/.entire /app/data && \
    chown -R patchpilot:patchpilot /app

# Switch to non-root user
USER patchpilot

# Expose HTTP port for AWS App Runner / ALB / ECS
EXPOSE 8080

# Cloud healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Production server entrypoint
CMD ["python", "-m", "patchpilot.server", "--host", "0.0.0.0", "--port", "8080"]
