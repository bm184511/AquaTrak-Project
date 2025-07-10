#!/bin/bash

# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

# =============================================================================
# PRODUCTION ENTRYPOINT SCRIPT FOR AQUATRAK PLATFORM
# =============================================================================

set -e

echo "Starting AquaTrak Production Platform..."

# Function to wait for database
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('Database is ready')
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
" 2>/dev/null; do
        echo "Database not ready, waiting..."
        sleep 5
    done
    echo "Database is ready!"
}

# Function to wait for Redis
wait_for_redis() {
    echo "Waiting for Redis to be ready..."
    while ! python -c "
import redis
import os
try:
    r = redis.from_url(os.environ['REDIS_URL'])
    r.ping()
    print('Redis is ready')
except Exception as e:
    print(f'Redis not ready: {e}')
    exit(1)
" 2>/dev/null; do
        echo "Redis not ready, waiting..."
        sleep 5
    done
    echo "Redis is ready!"
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    cd /app
    python -c "
import sys
sys.path.append('/app')
from src.config.database import init_database
init_database()
print('Database initialized successfully')
"
}

# Function to create SSL certificates if they don't exist
setup_ssl() {
    if [ ! -f /etc/nginx/ssl/cert.pem ] || [ ! -f /etc/nginx/ssl/key.pem ]; then
        echo "Generating self-signed SSL certificates..."
        mkdir -p /etc/nginx/ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/key.pem \
            -out /etc/nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=AquaTrak/CN=localhost"
        echo "SSL certificates generated"
    fi
}

# Function to set proper permissions
set_permissions() {
    echo "Setting proper permissions..."
    chown -R aquatrak:aquatrak /app
    chmod -R 755 /app
    chmod 600 /etc/nginx/ssl/*.pem 2>/dev/null || true
}

# Function to start supervisor
start_supervisor() {
    echo "Starting supervisor..."
    exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
}

# Main execution
main() {
    echo "Initializing AquaTrak Production Environment..."
    
    # Set permissions
    set_permissions
    
    # Setup SSL certificates
    setup_ssl
    
    # Wait for dependencies
    wait_for_db
    wait_for_redis
    
    # Run migrations
    run_migrations
    
    # Start supervisor
    start_supervisor
}

# Handle signals
trap 'echo "Received signal, shutting down..."; exit 0' SIGTERM SIGINT

# Run main function
main "$@" 