# AquaTrak Production Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the AquaTrak AI-GIS Water Risk Monitoring Platform in production environments using Docker and Kubernetes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Security Configuration](#security-configuration)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: Minimum 4 cores, Recommended 8+ cores
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 100GB SSD, Recommended 500GB+
- **OS**: Ubuntu 20.04+, CentOS 8+, or RHEL 8+

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Kubernetes**: 1.24+ (for K8s deployment)
- **kubectl**: Latest version
- **Git**: 2.30+

### Network Requirements

- **Ports**: 80, 443, 8000, 5432, 6379, 9090, 3000
- **SSL Certificate**: Valid SSL certificate for domain
- **Firewall**: Configured to allow required ports

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/aquatrak.git
cd aquatrak
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp env.production.example .env.production
```

Edit `.env.production` with your production values:

```bash
# Application Configuration
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=your-super-secret-production-key

# Database Configuration
DATABASE_URL=postgresql://aquatrak:secure-password@postgres:5432/aquatrak
POSTGRES_PASSWORD=secure-password

# Redis Configuration
REDIS_URL=redis://redis:6379

# API Configuration
ALLOWED_HOSTS=aquatrak.com,www.aquatrak.com
CORS_ORIGINS=https://aquatrak.com,https://www.aquatrak.com
```

### 3. SSL Certificate Setup

For production, obtain a valid SSL certificate:

```bash
# Using Let's Encrypt
sudo certbot certonly --standalone -d aquatrak.com -d www.aquatrak.com

# Copy certificates to Docker SSL directory
sudo cp /etc/letsencrypt/live/aquatrak.com/fullchain.pem docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/aquatrak.com/privkey.pem docker/ssl/key.pem
```

## Docker Deployment

### 1. Production Build

Build the production Docker image:

```bash
docker build -f Dockerfile.prod -t aquatrak:latest .
```

### 2. Deploy with Docker Compose

```bash
# Deploy all services
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Using Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh production

# Check deployment status
./scripts/deploy.sh --status
```

### 4. Service Management

```bash
# Start services
docker-compose -f docker-compose.prod.yml start

# Stop services
docker-compose -f docker-compose.prod.yml stop

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

### 1. Cluster Preparation

Ensure your Kubernetes cluster is ready:

```bash
# Check cluster status
kubectl cluster-info

# Create namespace
kubectl apply -f k8s/namespace.yml
```

### 2. Secrets and ConfigMaps

```bash
# Apply configuration
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secret.yml
```

### 3. Deploy Infrastructure

```bash
# Deploy persistent volumes
kubectl apply -f k8s/persistent-volumes.yml

# Deploy database and cache
kubectl apply -f k8s/postgres-deployment.yml
kubectl apply -f k8s/redis-deployment.yml
```

### 4. Deploy Application

```bash
# Deploy application
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml
```

### 5. Using K8s Deployment Script

```bash
# Make script executable
chmod +x scripts/k8s-deploy.sh

# Deploy to production
./scripts/k8s-deploy.sh production

# Check status
./scripts/k8s-deploy.sh --status

# Rollback if needed
./scripts/k8s-deploy.sh --rollback
```

## CI/CD Pipeline

### 1. GitHub Actions Setup

The CI/CD pipeline is configured in `.github/workflows/ci-cd.yml` and includes:

- **Code Quality**: Linting, type checking, security scanning
- **Testing**: Unit tests, integration tests, performance tests
- **Building**: Docker image building and pushing
- **Deployment**: Automated deployment to staging and production

### 2. Pipeline Stages

1. **Lint and Test**: Code quality checks and testing
2. **Security Scan**: Vulnerability scanning with Trivy
3. **Build and Push**: Docker image building and registry push
4. **Deploy Staging**: Automatic deployment to staging environment
5. **Deploy Production**: Manual deployment to production (on release)

### 3. Environment Secrets

Configure the following secrets in GitHub:

- `DOCKER_REGISTRY_TOKEN`: Docker registry authentication
- `KUBECONFIG`: Kubernetes cluster configuration
- `PRODUCTION_ENV`: Production environment variables

## Monitoring and Logging

### 1. Prometheus Monitoring

Access Prometheus at `http://your-domain:9090`

Key metrics monitored:
- API response times
- Request rates
- Database connections
- Redis memory usage
- Celery task metrics
- System resources

### 2. Grafana Dashboards

Access Grafana at `http://your-domain:3000`

Default credentials:
- Username: `admin`
- Password: Set in environment variables

### 3. Log Aggregation

Logs are collected using Filebeat and stored in Elasticsearch:

- **Application Logs**: `/app/logs/`
- **Container Logs**: Docker container logs
- **Access Logs**: Nginx access logs

### 4. Health Checks

```bash
# API Health Check
curl -f https://aquatrak.com/health

# Database Health Check
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U aquatrak

# Redis Health Check
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

## Security Configuration

### 1. Network Security

- **Firewall**: Configure UFW or iptables
- **SSL/TLS**: Valid SSL certificates with strong ciphers
- **Rate Limiting**: Configured in Nginx
- **CORS**: Properly configured for production domains

### 2. Application Security

- **Secret Management**: Use Kubernetes secrets or Docker secrets
- **Input Validation**: All inputs validated and sanitized
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Content Security Policy headers

### 3. Container Security

- **Non-root User**: Containers run as non-root user
- **Image Scanning**: Regular vulnerability scanning
- **Resource Limits**: CPU and memory limits configured
- **Network Policies**: Kubernetes network policies

### 4. Database Security

- **Encryption**: Data encrypted at rest and in transit
- **Access Control**: Minimal required permissions
- **Backup Encryption**: Encrypted backups
- **Connection Security**: SSL/TLS connections

## Backup and Recovery

### 1. Automated Backups

Backups are automatically created before deployments:

```bash
# Manual backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U aquatrak aquatrak > backup.sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U aquatrak aquatrak < backup.sql
```

### 2. Backup Retention

- **Daily Backups**: Kept for 7 days
- **Weekly Backups**: Kept for 4 weeks
- **Monthly Backups**: Kept for 12 months

### 3. Disaster Recovery

```bash
# Full system backup
tar -czf aquatrak-backup-$(date +%Y%m%d).tar.gz \
    uploads/ logs/ backup.sql docker-compose.prod.yml .env.production

# System restore
tar -xzf aquatrak-backup-YYYYMMDD.tar.gz
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### 1. Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Check resource usage
docker stats

# Check disk space
df -h
```

#### Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U aquatrak

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres
```

#### API Not Responding
```bash
# Check API health
curl -f http://localhost:8000/health

# Check API logs
docker-compose -f docker-compose.prod.yml logs aquatrak-api

# Check Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx
```

### 2. Performance Issues

#### High CPU Usage
```bash
# Check container resource usage
docker stats

# Check process list
docker-compose -f docker-compose.prod.yml exec aquatrak-api top

# Check Celery workers
docker-compose -f docker-compose.prod.yml exec aquatrak-api celery -A src.common_utils.celery_app inspect active
```

#### High Memory Usage
```bash
# Check memory usage
free -h

# Check Redis memory
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory

# Check database connections
docker-compose -f docker-compose.prod.yml exec postgres psql -U aquatrak -c "SELECT count(*) FROM pg_stat_activity;"
```

### 3. Log Analysis

#### Application Logs
```bash
# View recent logs
docker-compose -f docker-compose.prod.yml logs --tail=100 aquatrak-api

# Search for errors
docker-compose -f docker-compose.prod.yml logs aquatrak-api | grep ERROR

# Follow logs in real-time
docker-compose -f docker-compose.prod.yml logs -f aquatrak-api
```

#### System Logs
```bash
# Check system logs
journalctl -u docker.service

# Check kernel logs
dmesg | tail

# Check disk I/O
iostat -x 1
```

### 4. Recovery Procedures

#### Service Recovery
```bash
# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service-name]

# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

#### Data Recovery
```bash
# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U aquatrak aquatrak < backup.sql

# Restore uploads
tar -xzf uploads-backup.tar.gz

# Restore logs
tar -xzf logs-backup.tar.gz
```

## Support and Maintenance

### 1. Regular Maintenance

- **Weekly**: Security updates, log rotation
- **Monthly**: Performance review, backup verification
- **Quarterly**: Full system audit, capacity planning

### 2. Monitoring Alerts

Configure alerts for:
- Service downtime
- High resource usage
- Error rate spikes
- Backup failures
- Security events

### 3. Documentation Updates

Keep this documentation updated with:
- Configuration changes
- New features
- Troubleshooting procedures
- Performance optimizations

---

For additional support, contact the AquaTrak development team or refer to the project repository issues. 