# AquaTrak Database Integration

## Overview

AquaTrak uses PostgreSQL as its primary database with comprehensive support for all 13 operational modules. The database system includes:

- **13 Module Tables**: Complete data storage for all water analysis modules
- **System Tables**: Users, organizations, analysis results, alerts, and audit logs
- **Spatial Support**: PostGIS integration for geographic data
- **Repository Pattern**: Clean data access layer
- **Migration System**: Version-controlled schema changes
- **Performance Optimization**: Indexes, monitoring, and maintenance tools

## Database Schema

### Core System Tables

| Table | Description | Key Features |
|-------|-------------|--------------|
| `users` | User accounts and authentication | Multi-role support, country/language preferences |
| `organizations` | Organization management | Subscription plans, contact information |
| `user_organizations` | User-organization relationships | Role-based access control |
| `analysis_results` | Analysis job tracking | Status monitoring, processing time |
| `alerts` | System alerts and notifications | Severity levels, geographic location |
| `data_sources` | External data source configuration | API keys, status monitoring |
| `file_uploads` | File management | Upload tracking, file metadata |
| `reports` | Generated reports | Report types, content storage |
| `audit_log` | System audit trail | User actions, IP tracking |

### Module Tables

Each of the 13 modules has two main tables:

1. **Data Table**: Raw input data and measurements
2. **Analysis Results Table**: Processed results and insights

#### Module 1: InSAR Subsidence Monitoring
- `insar_subsidence_data`: Satellite interferogram data
- `insar_analysis_results`: Subsidence analysis and risk assessment

#### Module 2: Urban Flood Modeling
- `flood_modeling_data`: Rainfall, elevation, and land use data
- `flood_analysis_results`: Flood extent and damage estimates

#### Module 3: Groundwater Pollution Analysis
- `groundwater_data`: Well measurements and contaminant levels
- `groundwater_analysis_results`: Pollution risk assessment

#### Module 4: IoT Water Consumption
- `iot_sensor_data`: Real-time sensor measurements
- `iot_analysis_results`: Consumption patterns and efficiency metrics

#### Module 5: Drought Prediction
- `drought_data`: Climate and soil moisture data
- `drought_analysis_results`: Drought severity and impact assessment

#### Module 6: Urban Water Network Monitoring
- `water_network_data`: Network node measurements
- `water_network_analysis_results`: Leak detection and performance metrics

#### Module 7: Drinking Water Quality Analysis
- `drinking_water_data`: Water quality parameters
- `drinking_water_analysis_results`: Quality assessment and compliance

#### Module 8: Transboundary Water Modeling
- `transboundary_basin_data`: Basin characteristics and agreements
- `transboundary_analysis_results`: Conflict risk and cooperation analysis

#### Module 9: Dust Storm Analysis
- `dust_storm_data`: Meteorological and air quality data
- `dust_storm_analysis_results`: Storm prediction and health impacts

#### Module 10: Data Center Water Consumption
- `datacenter_water_data`: Cooling and consumption metrics
- `datacenter_analysis_results`: Efficiency and sustainability analysis

#### Module 11: Agricultural Reservoir Management
- `agricultural_reservoir_data`: Reservoir levels and weather data
- `agricultural_reservoir_analysis_results`: Water availability and optimization

#### Module 12: Urban Green Space Optimization
- `urban_green_space_data`: Green space characteristics
- `urban_green_space_analysis_results`: Ecosystem services assessment

#### Module 13: Environmental Health Risk Analysis
- `environmental_health_data`: Health and environmental indicators
- `environmental_health_analysis_results`: Risk assessment and interventions

## Setup Instructions

### 1. Prerequisites

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

Create a `.env` file with database settings:

```env
# Database Configuration
DATABASE_URL=postgresql://aquatrak:aquatrak_password@localhost:5432/aquatrak
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aquatrak
DB_USER=aquatrak
DB_PASSWORD=aquatrak_password
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### 3. Database Initialization

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE aquatrak;
CREATE USER aquatrak WITH PASSWORD 'aquatrak_password';
GRANT ALL PRIVILEGES ON DATABASE aquatrak TO aquatrak;
\q

# Run database setup
python scripts/setup_database.py
```

### 4. Verify Installation

```bash
# Check database health
curl http://localhost:8000/health

# Get database info
curl http://localhost:8000/db/info
```

## Usage Examples

### Repository Pattern

```python
from data_adapters.repository import RepositoryFactory
from config.database import get_db_context

# Get repository
user_repo = RepositoryFactory.get_user_repository()
iot_repo = RepositoryFactory.get_iot_repository()

# Use repositories
with get_db_context() as db:
    # Create user
    user = user_repo.create(db, username="john_doe", email="john@example.com")
    
    # Get IoT data
    sensor_data = iot_repo.get_by_sensor(db, "sensor_001")
    
    # Update analysis results
    user_repo.update(db, user.id, is_active=False)
```

### Data Operations

```python
from common_utils.db_utils import get_table_stats, backup_table_data

# Get table statistics
stats = get_table_stats(db, "iot_sensor_data")
print(f"Records: {stats['row_count']}, Size: {stats['size']}")

# Backup table data
backup_table_data(db, "iot_sensor_data", "backup/iot_data.json")

# Validate data integrity
validation = validate_data_integrity(db, "users")
print(f"Status: {validation['status']}")
```

### Performance Monitoring

```python
from common_utils.db_utils import get_performance_metrics, optimize_table

# Get performance metrics
metrics = get_performance_metrics(db)
print(f"Slow queries: {len(metrics['slow_queries'])}")

# Optimize table
optimize_table(db, "iot_sensor_data")
```

## Maintenance

### Regular Maintenance Tasks

```bash
# Daily: Check database health
curl http://localhost:8000/health

# Weekly: Backup critical tables
python -c "
from config.database import get_db_context
from common_utils.db_utils import backup_table_data
with get_db_context() as db:
    backup_table_data(db, 'users', 'backup/users.json')
    backup_table_data(db, 'analysis_results', 'backup/analysis.json')
"

# Monthly: Clean up old data
python -c "
from config.database import get_db_context
from common_utils.db_utils import cleanup_old_data
with get_db_context() as db:
    cleanup_old_data(db, 'audit_log', days_to_keep=90)
    cleanup_old_data(db, 'alerts', days_to_keep=30)
"
```

### Performance Optimization

```sql
-- Analyze tables for query optimization
ANALYZE users;
ANALYZE analysis_results;
ANALYZE iot_sensor_data;

-- Vacuum tables to reclaim space
VACUUM users;
VACUUM analysis_results;

-- Reindex tables for better performance
REINDEX TABLE users;
REINDEX TABLE analysis_results;
```

### Monitoring Queries

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

## Security

### Access Control

- **User Authentication**: JWT-based authentication
- **Role-Based Access**: Admin, user, analyst, viewer roles
- **Organization Isolation**: Data access by organization
- **Audit Logging**: Complete action tracking

### Data Protection

```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str) -> str:
    key = Fernet.generate_key()
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
```

### Backup Strategy

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backup/aquatrak"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Full database backup
pg_dump -h localhost -U aquatrak -d aquatrak > $BACKUP_DIR/full_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/full_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "full_backup_*.sql.gz" -mtime +7 -delete
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```bash
   # Check PostgreSQL service
   sudo systemctl status postgresql
   
   # Check connection
   psql -h localhost -U aquatrak -d aquatrak
   ```

2. **Performance Issues**
   ```sql
   -- Check for long-running queries
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
   FROM pg_stat_activity 
   WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
   ```

3. **Disk Space Issues**
   ```sql
   -- Check table sizes
   SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
   FROM pg_tables WHERE schemaname = 'public';
   ```

### Log Analysis

```bash
# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Check application logs
tail -f logs/aquatrak.log
```

## API Endpoints

### Database Health

- `GET /health` - Overall system health including database
- `GET /db/info` - Detailed database information
- `GET /db/stats` - Database statistics and performance metrics

### Data Management

- `POST /api/data/backup` - Create data backup
- `POST /api/data/restore` - Restore from backup
- `GET /api/data/validate` - Validate data integrity
- `POST /api/data/optimize` - Optimize database performance

## Migration Guide

### Adding New Tables

1. Create migration file:
   ```bash
   alembic revision -m "add_new_table"
   ```

2. Define table schema in migration
3. Run migration:
   ```bash
   alembic upgrade head
   ```

### Schema Changes

1. Create new migration
2. Define changes (add/remove columns, indexes)
3. Test in development environment
4. Deploy to production with backup

## Best Practices

1. **Regular Backups**: Daily automated backups
2. **Monitoring**: Continuous health monitoring
3. **Indexing**: Proper index strategy for performance
4. **Partitioning**: Large tables should be partitioned
5. **Connection Pooling**: Use connection pools for efficiency
6. **Audit Logging**: Track all data modifications
7. **Data Validation**: Regular integrity checks
8. **Performance Tuning**: Monitor and optimize queries

## Support

For database-related issues:

1. Check the logs: `tail -f logs/aquatrak.log`
2. Verify connectivity: `curl http://localhost:8000/health`
3. Check PostgreSQL status: `sudo systemctl status postgresql`
4. Review this documentation
5. Contact the development team

---

*This documentation is part of the AquaTrak platform. For more information, see the main README.md file.* 