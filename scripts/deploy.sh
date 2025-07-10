#!/bin/bash

# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

# =============================================================================
# PRODUCTION DEPLOYMENT SCRIPT FOR AQUATRAK PLATFORM
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/app/backups"
LOG_FILE="/app/logs/deploy.log"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check environment file
    if [ ! -f ".env.production" ]; then
        error "Production environment file (.env.production) not found"
    fi
    
    success "Prerequisites check passed"
}

# Function to create backup
create_backup() {
    log "Creating backup before deployment..."
    
    BACKUP_NAME="aquatrak-backup-$(date +%Y%m%d-%H%M%S)"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup database
    log "Backing up database..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_dump -U aquatrak aquatrak > "$BACKUP_PATH/database.sql" || warning "Database backup failed"
    
    # Backup uploads
    log "Backing up uploads..."
    tar -czf "$BACKUP_PATH/uploads.tar.gz" uploads/ 2>/dev/null || warning "Uploads backup failed"
    
    # Backup logs
    log "Backing up logs..."
    tar -czf "$BACKUP_PATH/logs.tar.gz" logs/ 2>/dev/null || warning "Logs backup failed"
    
    success "Backup created: $BACKUP_PATH"
}

# Function to deploy application
deploy_application() {
    log "Deploying AquaTrak application..."
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    # Build images if needed
    log "Building Docker images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Start services
    log "Starting services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "Application deployment completed"
}

# Function to run migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    sleep 30
    
    # Run migrations
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T aquatrak-api python -c "
import sys
sys.path.append('/app')
from src.config.database import init_database
init_database()
print('Database migrations completed')
" || error "Database migrations failed"
    
    success "Database migrations completed"
}

# Function to health check
health_check() {
    log "Performing health checks..."
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 60
    
    # Check API health
    log "Checking API health..."
    if curl -f http://localhost/health > /dev/null 2>&1; then
        success "API health check passed"
    else
        error "API health check failed"
    fi
    
    # Check database
    log "Checking database connection..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_isready -U aquatrak > /dev/null 2>&1; then
        success "Database health check passed"
    else
        error "Database health check failed"
    fi
    
    # Check Redis
    log "Checking Redis connection..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
        success "Redis health check passed"
    else
        error "Redis health check failed"
    fi
    
    success "All health checks passed"
}

# Function to cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    
    # Keep only last 7 days of backups
    find "$BACKUP_DIR" -name "aquatrak-backup-*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
    
    success "Backup cleanup completed"
}

# Function to show deployment status
show_status() {
    log "Deployment Status:"
    echo "=================="
    
    # Show running containers
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    # Show resource usage
    echo ""
    log "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Main deployment function
main() {
    log "Starting AquaTrak production deployment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    create_backup
    
    # Deploy application
    deploy_application
    
    # Run migrations
    run_migrations
    
    # Health check
    health_check
    
    # Cleanup old backups
    cleanup_backups
    
    # Show status
    show_status
    
    success "AquaTrak production deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [environment]"
        echo "  environment: production (default) or staging"
        exit 0
        ;;
    --status|-s)
        show_status
        exit 0
        ;;
    --rollback|-r)
        log "Rollback functionality not implemented yet"
        exit 1
        ;;
esac

# Run main function
main "$@" 