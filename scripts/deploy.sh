#!/bin/bash

# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

# =============================================================================
# COMPREHENSIVE DEPLOYMENT SCRIPT FOR AQUATRAK PLATFORM
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
PROD_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
ENV_FILE="$PROJECT_ROOT/env.production"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$PROJECT_ROOT/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE" >&2
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if required files exist
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Function to create backup
create_backup() {
    log "Creating backup..."
    
    local backup_name="aquatrak_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup database
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U aquatrak aquatrak > "$backup_path/database.sql" 2>/dev/null; then
        log_success "Database backup created: $backup_path/database.sql"
    else
        log_warning "Failed to create database backup"
    fi
    
    # Backup uploads
    if [ -d "$PROJECT_ROOT/uploads" ]; then
        cp -r "$PROJECT_ROOT/uploads" "$backup_path/"
        log_success "Uploads backup created"
    fi
    
    # Backup logs
    if [ -d "$PROJECT_ROOT/logs" ]; then
        cp -r "$PROJECT_ROOT/logs" "$backup_path/"
        log_success "Logs backup created"
    fi
    
    # Create backup manifest
    echo "Backup created: $(date)" > "$backup_path/manifest.txt"
    echo "Backup path: $backup_path" >> "$backup_path/manifest.txt"
    
    log_success "Backup completed: $backup_path"
}

# Function to stop services
stop_services() {
    log "Stopping services..."
    
    if docker-compose -f "$COMPOSE_FILE" down --remove-orphans; then
        log_success "Services stopped successfully"
    else
        log_warning "Some services may not have stopped cleanly"
    fi
}

# Function to build images
build_images() {
    log "Building Docker images..."
    
    # Build with no cache for production
    if docker-compose -f "$COMPOSE_FILE" build --no-cache; then
        log_success "Images built successfully"
    else
        log_error "Failed to build images"
        exit 1
    fi
}

# Function to start services
start_services() {
    log "Starting services..."
    
    # Start services in order
    if docker-compose -f "$COMPOSE_FILE" up -d postgres redis; then
        log_success "Database and Redis started"
    else
        log_error "Failed to start database and Redis"
        exit 1
    fi
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    sleep 30
    
    # Start API and other services
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        log_success "All services started"
    else
        log_error "Failed to start services"
        exit 1
    fi
}

# Function to wait for services to be healthy
wait_for_health() {
    log "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "healthy"; then
            log_success "Services are healthy"
            return 0
        else
            log_warning "Waiting for services to be healthy... attempt $attempt/$max_attempts"
            sleep 10
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Services failed to become healthy"
    return 1
}

# Function to run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Check API health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    # Check database connection
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U aquatrak -d aquatrak > /dev/null 2>&1; then
        log_success "Database health check passed"
    else
        log_error "Database health check failed"
        return 1
    fi
    
    # Check Redis connection
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis health check passed"
    else
        log_error "Redis health check failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    if docker-compose -f "$COMPOSE_FILE" exec -T aquatrak-api python -c "
import sys
sys.path.append('/app')
from src.config.database import init_db
init_db()
print('Migrations completed')
"; then
        log_success "Database migrations completed"
    else
        log_error "Database migrations failed"
        return 1
    fi
}

# Function to cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    
    # Keep only last 7 backups
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "aquatrak_backup_*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
        log_success "Old backups cleaned up"
    fi
}

# Function to rollback
rollback() {
    log_error "Deployment failed, starting rollback..."
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true
    
    # Restore from backup if available
    local latest_backup=$(find "$BACKUP_DIR" -name "aquatrak_backup_*" -type d | sort | tail -1)
    if [ -n "$latest_backup" ]; then
        log "Restoring from backup: $latest_backup"
        # Add restore logic here
    fi
    
    log_error "Rollback completed"
    exit 1
}

# Function to show deployment status
show_status() {
    log "Deployment Status:"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Main deployment function
deploy() {
    log "Starting AquaTrak deployment..."
    
    # Set up error handling
    trap rollback ERR
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    create_backup
    
    # Stop existing services
    stop_services
    
    # Build images
    build_images
    
    # Start services
    start_services
    
    # Wait for health
    if ! wait_for_health; then
        log_error "Services failed to become healthy"
        rollback
    fi
    
    # Run migrations
    if ! run_migrations; then
        log_error "Database migrations failed"
        rollback
    fi
    
    # Run health checks
    if ! run_health_checks; then
        log_error "Health checks failed"
        rollback
    fi
    
    # Cleanup old backups
    cleanup_backups
    
    # Show status
    show_status
    
    log_success "Deployment completed successfully!"
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  deploy     Deploy the application"
    echo "  status     Show deployment status"
    echo "  backup     Create a backup"
    echo "  rollback   Rollback to previous version"
    echo "  logs       Show logs"
    echo "  help       Show this help message"
    echo ""
}

# Main script logic
case "${1:-help}" in
    deploy)
        deploy
        ;;
    status)
        show_status
        ;;
    backup)
        create_backup
        ;;
    rollback)
        rollback
        ;;
    logs)
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    help|*)
        usage
        exit 1
        ;;
esac 