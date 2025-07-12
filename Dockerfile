# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

# =============================================================================
# OPTIMIZED MULTI-STAGE DOCKERFILE FOR AQUATRAK PLATFORM
# =============================================================================

# Stage 1: Frontend Build
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files for better layer caching
COPY src/frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy frontend source
COPY src/frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Backend Dependencies
FROM python:3.11-slim AS backend-deps

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directory
WORKDIR /app

# Copy requirements for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Production Runtime
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    libgdal30 \
    libgeos-c1v5 \
    libproj22 \
    gdal-bin \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user and group
RUN groupadd -r aquatrak && \
    useradd -r -g aquatrak -s /bin/bash -m aquatrak

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/static /app/temp /app/backups && \
    chown -R aquatrak:aquatrak /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=aquatrak:aquatrak src/ ./src/
COPY --chown=aquatrak:aquatrak scripts/ ./scripts/

# Copy frontend build
COPY --from=frontend-builder --chown=aquatrak:aquatrak /app/frontend/build ./static

# Copy configuration files
COPY --chown=aquatrak:aquatrak docker/nginx.conf /etc/nginx/nginx.conf
COPY --chown=aquatrak:aquatrak docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=aquatrak:aquatrak docker/entrypoint.sh /entrypoint.sh

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Create nginx directories and set permissions
RUN mkdir -p /var/log/nginx /var/cache/nginx && \
    chown -R aquatrak:aquatrak /var/log/nginx /var/cache/nginx

# Switch to non-root user
USER aquatrak

# Expose ports
EXPOSE 8000 80

# Health check with proper timeout and retries
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"] 