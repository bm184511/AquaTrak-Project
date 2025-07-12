#!/bin/bash

# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

# =============================================================================
# OPTIMIZED PRODUCTION ENTRYPOINT SCRIPT FOR AQUATRAK PLATFORM
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Function to wait for database with timeout
wait_for_db() {
    local max_attempts=30
    local attempt=1
    
    log "Waiting for database to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], connect_timeout=5)
    conn.close()
    print('Database is ready')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
" 2>/dev/null; then
            log_success "Database is ready!"
            return 0
        else
            log_warning "Database not ready, attempt $attempt/$max_attempts..."
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Database failed to become ready after $max_attempts attempts"
    return 1
}

# Function to wait for Redis with timeout
wait_for_redis() {
    local max_attempts=30
    local attempt=1
    
    log "Waiting for Redis to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import redis
import os
import sys
try:
    r = redis.from_url(os.environ['REDIS_URL'], socket_connect_timeout=5)
    r.ping()
    print('Redis is ready')
    sys.exit(0)
except Exception as e:
    print(f'Redis not ready: {e}')
    sys.exit(1)
" 2>/dev/null; then
            log_success "Redis is ready!"
            return 0
        else
            log_warning "Redis not ready, attempt $attempt/$max_attempts..."
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Redis failed to become ready after $max_attempts attempts"
    return 1
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd /app
    
    if python -c "
import sys
sys.path.append('/app')
try:
    from src.config.database import init_db
    init_db()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
    sys.exit(1)
"; then
        log_success "Database migrations completed successfully"
    else
        log_error "Database migrations failed"
        return 1
    fi
}

# Function to create SSL certificates if they don't exist
setup_ssl() {
    if [ ! -f /etc/nginx/ssl/cert.pem ] || [ ! -f /etc/nginx/ssl/key.pem ]; then
        log "Generating self-signed SSL certificates..."
        mkdir -p /etc/nginx/ssl
        
        if openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/key.pem \
            -out /etc/nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=AquaTrak/CN=localhost" 2>/dev/null; then
            log_success "SSL certificates generated successfully"
        else
            log_warning "Failed to generate SSL certificates, continuing without SSL"
        fi
    else
        log "SSL certificates already exist"
    fi
}

# Function to set proper permissions
set_permissions() {
    log "Setting proper permissions..."
    
    # Set ownership
    chown -R aquatrak:aquatrak /app 2>/dev/null || true
    
    # Set directory permissions
    find /app -type d -exec chmod 755 {} \; 2>/dev/null || true
    
    # Set file permissions
    find /app -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Set executable permissions for scripts
    find /app -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    
    # Set SSL certificate permissions
    chmod 600 /etc/nginx/ssl/*.pem 2>/dev/null || true
    
    log_success "Permissions set successfully"
}

# Function to check system resources
check_system_resources() {
    log "Checking system resources..."
    
    # Check available memory
    local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7*100/$2}')
    if [ "$available_mem" -lt 20 ]; then
        log_warning "Low memory available: ${available_mem}%"
    else
        log_success "Memory check passed: ${available_mem}% available"
    fi
    
    # Check disk space
    local disk_usage=$(df /app | awk 'NR==2{printf "%.0f", $5}')
    if [ "$disk_usage" -gt 90 ]; then
        log_warning "High disk usage: ${disk_usage}%"
    else
        log_success "Disk space check passed: ${disk_usage}% used"
    fi
}

# Function to start supervisor
start_supervisor() {
    log "Starting supervisor..."
    
    # Create supervisor log directory
    mkdir -p /app/logs
    
    # Start supervisor in foreground
    exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
}

# Function to cleanup on exit
cleanup() {
    log "Shutting down AquaTrak..."
    
    # Stop supervisor gracefully
    if [ -f /app/temp/supervisord.pid ]; then
        supervisorctl stop all 2>/dev/null || true
        supervisorctl shutdown 2>/dev/null || true
    fi
    
    log_success "AquaTrak shutdown complete"
    exit 0
}

# Main execution
main() {
    log "Initializing AquaTrak Production Environment..."
    
    # Set up signal handlers
    trap cleanup SIGTERM SIGINT
    
    # Check system resources
    check_system_resources
    
    # Set permissions
    set_permissions
    
    # Setup SSL certificates
    setup_ssl
    
    # Wait for dependencies
    if ! wait_for_db; then
        log_error "Failed to connect to database"
        exit 1
    fi
    
    if ! wait_for_redis; then
        log_error "Failed to connect to Redis"
        exit 1
    fi
    
    # Run migrations
    if ! run_migrations; then
        log_error "Failed to run database migrations"
        exit 1
    fi
    
    log_success "AquaTrak initialization completed successfully"
    
    # Start supervisor
    start_supervisor
}

# Run main function
main "$@" 