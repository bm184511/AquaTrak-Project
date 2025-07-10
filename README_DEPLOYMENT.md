# AquaTrak Production Deployment Setup

## 🚀 Quick Start

This repository contains a comprehensive production deployment setup for the AquaTrak AI-GIS Water Risk Monitoring Platform with Docker, Kubernetes, and CI/CD pipeline.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Deployment](#quick-deployment)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

AquaTrak is a comprehensive AI-GIS platform for predictive water risk monitoring and urban resilience. This deployment setup provides:

- **Multi-stage Docker builds** for optimized production images
- **Kubernetes manifests** for scalable container orchestration
- **CI/CD pipeline** with GitHub Actions
- **Comprehensive monitoring** with Prometheus, Grafana, and ELK stack
- **Production-ready security** configurations
- **Automated backup and recovery** procedures

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Ingress/Nginx │    │   AquaTrak API  │
│   (SSL/TLS)     │───▶│   (Reverse Proxy)│───▶│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │   Prometheus    │    │   PostgreSQL    │
│   (Monitoring)  │◀───│   (Metrics)     │◀───│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kibana        │    │   Elasticsearch │    │   Redis         │
│   (Logs)        │◀───│   (Log Storage) │◀───│   (Cache)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Celery Beat   │    │   Celery Worker │    │   Filebeat      │
│   (Scheduler)   │───▶│   (Tasks)       │───▶│   (Log Agent)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ⚡ Quick Deployment

### Docker Compose (Recommended for small to medium deployments)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/aquatrak.git
cd aquatrak

# 2. Configure environment
cp env.production.example .env.production
# Edit .env.production with your values

# 3. Deploy
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# 4. Check status
docker-compose -f docker-compose.prod.yml ps
```

### Kubernetes (Recommended for large-scale deployments)

```bash
# 1. Deploy to Kubernetes cluster
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/

# 2. Or use the deployment script
chmod +x scripts/k8s-deploy.sh
./scripts/k8s-deploy.sh production
```

## 🔧 Detailed Setup

### Prerequisites

#### System Requirements
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: 100GB+ SSD
- **OS**: Ubuntu 20.04+, CentOS 8+, RHEL 8+

#### Software Requirements
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install kubectl (for Kubernetes deployment)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### Environment Configuration

#### 1. Basic Configuration
```bash
# Copy and edit environment file
cp env.production.example .env.production

# Essential variables to configure:
DEBUG=false
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=postgresql://aquatrak:password@postgres:5432/aquatrak
REDIS_URL=redis://redis:6379
ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-domain.com
```

#### 2. SSL Certificate Setup
```bash
# Using Let's Encrypt
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/key.pem
```

#### 3. Database Setup
```bash
# Initialize database
docker-compose -f docker-compose.prod.yml exec postgres psql -U aquatrak -d aquatrak -f /docker-entrypoint-initdb.d/init-db.sql
docker-compose -f docker-compose.prod.yml exec postgres psql -U aquatrak -d aquatrak -f /docker-entrypoint-initdb.d/complete-db-schema.sql
```

### Deployment Options

#### Option 1: Docker Compose (Simple)
```bash
# Deploy all services
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale aquatrak-api=3
```

#### Option 2: Kubernetes (Scalable)
```bash
# Create namespace
kubectl apply -f k8s/namespace.yml

# Deploy infrastructure
kubectl apply -f k8s/persistent-volumes.yml
kubectl apply -f k8s/postgres-deployment.yml
kubectl apply -f k8s/redis-deployment.yml

# Deploy application
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml

# Deploy monitoring
kubectl apply -f k8s/monitoring/
```

#### Option 3: Automated Scripts
```bash
# Docker deployment
chmod +x scripts/deploy.sh
./scripts/deploy.sh production

# Kubernetes deployment
chmod +x scripts/k8s-deploy.sh
./scripts/k8s-deploy.sh production
```

## ⚙️ Configuration

### Docker Configuration

#### Production Dockerfile
- **Multi-stage build** for optimized images
- **Security hardening** with non-root user
- **Health checks** for container monitoring
- **Resource limits** for performance control

#### Docker Compose Services
- **API**: FastAPI application with Gunicorn
- **Database**: PostgreSQL with persistent storage
- **Cache**: Redis with persistence
- **Proxy**: Nginx with SSL termination
- **Worker**: Celery for background tasks
- **Monitoring**: Prometheus, Grafana, ELK stack

### Kubernetes Configuration

#### Namespace and RBAC
```yaml
# Isolated namespace
apiVersion: v1
kind: Namespace
metadata:
  name: aquatrak
```

#### Persistent Storage
```yaml
# Database storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: aquatrak-postgres-pvc
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Gi
```

#### Ingress Configuration
```yaml
# SSL termination and routing
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

## 📊 Monitoring

### Prometheus Metrics
- **API Metrics**: Response times, request rates, error rates
- **Database Metrics**: Connections, query performance
- **System Metrics**: CPU, memory, disk usage
- **Custom Metrics**: Business logic metrics

### Grafana Dashboards
- **System Overview**: Overall platform health
- **API Performance**: Response times and throughput
- **Database Performance**: Query performance and connections
- **Resource Usage**: CPU, memory, and disk utilization

### Log Aggregation
- **Application Logs**: Structured logging with correlation IDs
- **Access Logs**: Nginx access logs with rate limiting
- **Error Logs**: Error tracking and alerting
- **Audit Logs**: Security and compliance logging

### Health Checks
```bash
# API Health
curl -f https://your-domain.com/health

# Database Health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U aquatrak

# Redis Health
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

## 🔒 Security

### Network Security
- **SSL/TLS**: End-to-end encryption
- **Rate Limiting**: Protection against DDoS
- **CORS**: Proper cross-origin configuration
- **Firewall**: Network-level protection

### Application Security
- **Input Validation**: All inputs validated
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Content Security Policy
- **CSRF Protection**: Cross-site request forgery protection

### Container Security
- **Non-root User**: Containers run as non-root
- **Image Scanning**: Regular vulnerability scanning
- **Resource Limits**: CPU and memory limits
- **Network Policies**: Kubernetes network isolation

### Secret Management
```bash
# Docker secrets
echo "your-secret" | docker secret create db_password -

# Kubernetes secrets
kubectl create secret generic aquatrak-secrets \
  --from-literal=SECRET_KEY=your-secret-key \
  --from-literal=DB_PASSWORD=your-db-password
```

## 🚨 Troubleshooting

### Common Issues

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

# Check connection pool
docker-compose -f docker-compose.prod.yml exec postgres psql -U aquatrak -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Check Celery workers
docker-compose -f docker-compose.prod.yml exec aquatrak-api celery -A src.common_utils.celery_app inspect active

# Check Redis memory
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory
```

### Recovery Procedures

#### Service Recovery
```bash
# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service-name]

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

#### Data Recovery
```bash
# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U aquatrak aquatrak < backup.sql

# Restore uploads
tar -xzf uploads-backup.tar.gz
```

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
docker-compose -f docker-compose.prod.yml up -d

# View detailed logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

## 📚 Additional Resources

### Documentation
- [API Documentation](docs/API.md)
- [Admin Panel Guide](docs/ADMIN_PANEL.md)
- [Database Schema](docs/DATABASE_INTEGRATION.md)
- [Testing Guide](docs/TEST_RESULTS.md)

### Scripts
- `scripts/deploy.sh`: Docker deployment script
- `scripts/k8s-deploy.sh`: Kubernetes deployment script
- `scripts/backup.sh`: Backup and recovery script
- `scripts/monitor.sh`: Monitoring and health check script

### Configuration Files
- `docker-compose.prod.yml`: Production Docker Compose
- `Dockerfile.prod`: Production Dockerfile
- `k8s/`: Kubernetes manifests
- `.github/workflows/`: CI/CD pipeline

## 🤝 Support

For support and questions:
- **Issues**: [GitHub Issues](https://github.com/your-org/aquatrak/issues)
- **Documentation**: [Project Wiki](https://github.com/your-org/aquatrak/wiki)
- **Email**: support@aquatrak.com

## 📄 License

This project is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

---

**AquaTrak** - AI-GIS Platform for Predictive Water Risk and Urban Resilience 