# Single-Server Deployment Dockerfile for UCust.AI API (FastAPI + AI Agents + Saiga 3 Engine)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies (build tools, libpq for PostgreSQL, curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first for layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . /app

# Create output directory for media files
RUN mkdir -p /app/output

# Expose FastAPI application port
EXPOSE 8000

# Run FastAPI server via uvicorn
CMD ["uvicorn", "bridge.api_controller:app", "--host", "0.0.0.0", "--port", "8000"]
