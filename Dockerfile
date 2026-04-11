# ============================================================================
# MULTI-STAGE BUILD for optimized production image
# ============================================================================

# ============================================================================
# Stage 1: Builder
# ============================================================================

FROM python:3.11-slim AS builder

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy only deps (cache optimization)
COPY pyproject.toml poetry.lock* ./

# Export dependencies → requirements.txt
RUN poetry export -f requirements.txt --without-hashes --output requirements.txt

# ============================================================================
# Stage 2: Runtime
# ============================================================================

FROM python:3.11-slim

WORKDIR /app

# Runtime deps
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY services /app/services

# ENV
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Permissions
RUN chown -R appuser:appuser /app

USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001

# Run application
CMD ["python", "-m", "uvicorn", "services.ingestion.app.main:app", "--host", "0.0.0.0", "--port", "8001"]