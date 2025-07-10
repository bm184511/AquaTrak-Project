# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

# Multi-stage build for AquaTrak
FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p logs uploads static

# Create non-root user
RUN useradd --create-home --shell /bin/bash aquatrak && \
    chown -R aquatrak:aquatrak /app

USER aquatrak

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "src/main.py"] 