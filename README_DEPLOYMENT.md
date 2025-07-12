# AquaTrak Platform - Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the AquaTrak AI-GIS Water Risk Monitoring Platform in production using Docker and Docker Compose.

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended) or Windows Server 2019+
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 100GB+ available space
- **Network**: Stable internet connection for external API access

### Software Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- curl (for health checks)

### Security Requirements

- Firewall configured to allow ports 80, 443, 8000, 5432, 6379, 9090, 3000
- SSL certificates for HTTPS
- Strong passwords for all services
- Regular security updates

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AquaTrak-Project
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.production.example env.production

# Edit environment variables
nano env.production
```

**Critical Environment Variables:**

```bash
# Security (CHANGE THESE IMMEDIATELY)
SECRET_KEY=your-super-secret-production-key
POSTGRES_PASSWORD=your-secure-database-password
REDIS_PASSWORD=your-secure-redis-password
GRAFANA_ADMIN_PASSWORD=your-secure-grafana-password

# Database
DATABASE_URL=postgresql://aquatrak:your-secure-password@postgres:5432/aquatrak

# Redis
REDIS_URL=redis://redis:6379

# Domain Configuration
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 3. Deploy with Script

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Deploy the application
./scripts/deploy.sh deploy
```

### 4. Verify Deployment

```bash
# Check service status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Run health checks
curl http://localhost:8000/health
```

## Manual Deployment

### 1. Build Images

```bash
# Build all services
docker-compose build --no-cache

# Or build specific service
docker-compose build aquatrak-api
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Start services in order
docker-compose up -d postgres redis
sleep 30
docker-compose up -d aquatrak-api celery-worker celery-beat
docker-compose up -d nginx prometheus grafana
```

### 3. Run Migrations

```bash
# Run database migrations
docker-compose exec aquatrak-api python -c "
import sys
sys.path.append('/app')
from src.config.database import init_db
init_db()
"
```

## Production Configuration

### SSL/TLS Setup

1. **Obtain SSL Certificates:**
   ```bash
   # Using Let's Encrypt
   certbot certonly --standalone -d your-domain.com
   ```

2. **Configure Nginx SSL:**
   ```bash
   # Copy certificates
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/cert.pem
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/key.pem
   ```

3. **Update Nginx Configuration:**
   Edit `docker/nginx.conf` to use your domain name.

### Database Configuration

1. **PostgreSQL Optimization:**
   ```bash
   # Add to docker-compose.yml postgres service
   environment:
     - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
   ```

2. **Connection Pooling:**
   ```bash
   # Configure in env.production
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=30
   DB_POOL_TIMEOUT=30
   ```

### Redis Configuration

1. **Memory Management:**
   ```bash
   # Add to docker-compose.yml redis service
   command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
   ```

2. **Persistence:**
   ```bash
   # Configure backup strategy
   volumes:
     - redis_data:/data:rw
   ```

### Monitoring Setup

1. **Prometheus Configuration:**
   - Edit `docker/monitoring/prometheus.yml`
   - Configure alerting rules
   - Set up retention policies

2. **Grafana Dashboards:**
   - Access Grafana at `http://your-domain:3000`
   - Default credentials: admin/admin
   - Import dashboards from `docker/monitoring/grafana/dashboards/`

## Security Hardening

### 1. Network Security

```bash
# Configure firewall
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

### 2. Container Security

```bash
# Add to docker-compose.yml services
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp:noexec,nosuid,size=100m
```

### 3. Secrets Management

```bash
# Use Docker secrets for sensitive data
echo "your-secret-password" | docker secret create postgres_password -
```

### 4. Regular Updates

```bash
# Update base images
docker-compose pull
docker-compose build --no-cache
```

## Backup and Recovery

### Automated Backups

```bash
# Create backup
./scripts/deploy.sh backup

# Restore from backup
docker-compose exec postgres psql -U aquatrak -d aquatrak < backup.sql
```

### Manual Backup

```bash
# Database backup
docker-compose exec postgres pg_dump -U aquatrak aquatrak > backup.sql

# File backup
tar -czf uploads_backup.tar.gz uploads/
```

## Monitoring and Logging

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U aquatrak

# Redis health
docker-compose exec redis redis-cli ping
```

### Log Management

```bash
# View logs
docker-compose logs -f aquatrak-api

# Log rotation
docker-compose exec aquatrak-api logrotate /etc/logrotate.conf
```

### Performance Monitoring

```bash
# Resource usage
docker stats

# Prometheus metrics
curl http://localhost:9090/metrics

# Grafana dashboards
http://localhost:3000
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed:**
   ```bash
   # Check database status
   docker-compose ps postgres
   
   # Check logs
   docker-compose logs postgres
   
   # Restart database
   docker-compose restart postgres
   ```

2. **Redis Connection Failed:**
   ```bash
   # Check Redis status
   docker-compose ps redis
   
   # Check memory usage
   docker-compose exec redis redis-cli info memory
   ```

3. **API Not Responding:**
   ```bash
   # Check API logs
   docker-compose logs aquatrak-api
   
   # Check health endpoint
   curl http://localhost:8000/health
   
   # Restart API
   docker-compose restart aquatrak-api
   ```

4. **Nginx Issues:**
   ```bash
   # Check Nginx configuration
   docker-compose exec nginx nginx -t
   
   # Check Nginx logs
   docker-compose logs nginx
   ```

### Performance Issues

1. **High Memory Usage:**
   ```bash
   # Check memory usage
   docker stats
   
   # Adjust resource limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

2. **Slow Database Queries:**
   ```bash
   # Enable query logging
   docker-compose exec postgres psql -U aquatrak -c "SET log_statement = 'all';"
   
   # Check slow queries
   docker-compose logs postgres | grep "duration:"
   ```

3. **Celery Task Failures:**
   ```bash
   # Check Celery logs
   docker-compose logs celery-worker
   
   # Check task status
   docker-compose exec aquatrak-api celery -A src.common_utils.celery_app inspect active
   ```

## Scaling

### Horizontal Scaling

```bash
# Scale API instances
docker-compose up -d --scale aquatrak-api=3

# Scale Celery workers
docker-compose up -d --scale celery-worker=4
```

### Load Balancing

```bash
# Configure Nginx load balancing
upstream aquatrak_api {
    server aquatrak-api:8000;
    server aquatrak-api:8001;
    server aquatrak-api:8002;
}
```

## Maintenance

### Regular Maintenance Tasks

1. **Database Maintenance:**
   ```bash
   # Vacuum database
   docker-compose exec postgres psql -U aquatrak -c "VACUUM ANALYZE;"
   
   # Update statistics
   docker-compose exec postgres psql -U aquatrak -c "ANALYZE;"
   ```

2. **Log Rotation:**
   ```bash
   # Rotate logs
   docker-compose exec aquatrak-api logrotate /etc/logrotate.conf
   ```

3. **Backup Verification:**
   ```bash
   # Test backup restoration
   docker-compose exec postgres psql -U aquatrak -d aquatrak -c "SELECT COUNT(*) FROM information_schema.tables;"
   ```

### Update Procedures

1. **Application Updates:**
   ```bash
   # Pull latest code
   git pull origin main
   
   # Rebuild and deploy
   ./scripts/deploy.sh deploy
   ```

2. **Dependency Updates:**
   ```bash
   # Update requirements.txt
   pip freeze > requirements.txt
   
   # Rebuild images
   docker-compose build --no-cache
   ```

## Support

For deployment issues:

1. Check the logs: `./scripts/deploy.sh logs`
2. Verify configuration: `./scripts/deploy.sh status`
3. Review this documentation
4. Contact the development team

## Security Checklist

- [ ] Changed all default passwords
- [ ] Configured SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enabled security headers
- [ ] Configured backup strategy
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Access control configured
- [ ] Log monitoring enabled
- [ ] Incident response plan ready 