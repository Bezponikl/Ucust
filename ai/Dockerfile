# ==============================================================================
# UCust AI Production & Development Base Dockerfile
# Multi-stage build with Python 3.11, system libraries, and secure execution.
# ==============================================================================

# --- Stage 1: Build & Dependencies ---
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install

COPY requirements.txt .

# Install dependencies into temporary directory
RUN pip install --prefix=/install/deps -r requirements.txt


# --- Stage 2: Final Production Runtime ---
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/install/deps/bin:${PATH}"

# Install runtime system libraries (libpq for PostgreSQL, ffmpeg for media processing, libgl1 for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install/deps /usr/local

# Create non-root system user and application directories
RUN groupadd -r ucust && useradd -r -g ucust -d /app -s /sbin/nologin ucust \
    && mkdir -p /app/output/photos /app/storage /app/logs \
    && chown -R ucust:ucust /app

WORKDIR /app

# Copy application source code
COPY --chown=ucust:ucust . /app

# Switch to non-root user
USER ucust

# Expose default HTTP port
EXPOSE 8000

# Default health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/ai/health || exit 1

# Default Command: Start FastAPI Service Gateway
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
