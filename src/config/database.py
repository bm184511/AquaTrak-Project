"""
Database configuration and connection management for AquaTrak
"""

import os
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from .settings import get_settings

logger = logging.getLogger(__name__)

# Database configuration
settings = get_settings()

# Database URL construction
def get_database_url() -> str:
    """Construct database URL from environment variables"""
    if settings.database_url:
        return settings.database_url
    
    # Construct from individual components
    user = settings.db_user or "aquatrak"
    password = settings.db_password or "aquatrak_password"
    host = settings.db_host or "localhost"
    port = settings.db_port or 5432
    database = settings.db_name or "aquatrak"
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Create database engine
engine = create_engine(
    get_database_url(),
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Session:
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they are registered
        try:
            from ..modules.insar_subsidence.models import InsarSubsidenceData
        except ImportError:
            pass
        
        try:
            from ..modules.urban_flood_modeling.models import FloodModelingData
        except ImportError:
            pass
        
        try:
            from ..modules.groundwater_pollution.models import GroundwaterData
        except ImportError:
            pass
        
        try:
            from ..modules.iot_water_consumption.models import IoTWaterData
        except ImportError:
            pass
        
        try:
            from ..modules.drought_prediction.models import DroughtData
        except ImportError:
            pass
        
        try:
            from ..modules.urban_water_network.models import WaterNetworkData
        except ImportError:
            pass
        
        try:
            from ..modules.drinking_water_quality.models import DrinkingWaterData
        except ImportError:
            pass
        
        try:
            from ..modules.transboundary_water.models import TransboundaryBasinData
        except ImportError:
            pass
        
        try:
            from ..modules.dust_storm_analysis.models import DustStormData
        except ImportError:
            pass
        
        try:
            from ..modules.data_center_water.models import DataCenterWaterData
        except ImportError:
            pass
        
        try:
            from ..modules.agricultural_reservoir.models import AgriculturalReservoirData
        except ImportError:
            pass
        
        try:
            from ..modules.urban_green_space.models import GreenSpaceData
        except ImportError:
            pass
        
        try:
            from ..modules.environmental_health.models import EnvironmentalHealthData
        except ImportError:
            pass
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def check_db_connection() -> bool:
    """Check database connection"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_db_info() -> Dict[str, Any]:
    """Get database information"""
    try:
        with engine.connect() as connection:
            # Get database version
            version_result = connection.execute("SELECT version()")
            version = version_result.scalar()
            
            # Get table count
            table_count_result = connection.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = table_count_result.scalar()
            
            # Get database size
            size_result = connection.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            db_size = size_result.scalar()
            
            return {
                "version": version,
                "table_count": table_count,
                "database_size": db_size,
                "connection_status": "connected"
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "connection_status": "disconnected",
            "error": str(e)
        }

def execute_sql_file(file_path: str) -> bool:
    """Execute SQL file"""
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()
        
        with engine.connect() as connection:
            connection.execute(sql_content)
            connection.commit()
        
        logger.info(f"SQL file {file_path} executed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute SQL file {file_path}: {e}")
        return False

def backup_database(backup_path: str) -> bool:
    """Create database backup"""
    try:
        import subprocess
        
        db_url = get_database_url()
        # Extract components from URL
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        cmd = [
            'pg_dump',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:],  # Remove leading slash
            '-f', backup_path,
            '--no-password'
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_path}")
            return True
        else:
            logger.error(f"Backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        return False

def restore_database(backup_path: str) -> bool:
    """Restore database from backup"""
    try:
        import subprocess
        
        db_url = get_database_url()
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        cmd = [
            'psql',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:],
            '-f', backup_path,
            '--no-password'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Database restored from: {backup_path}")
            return True
        else:
            logger.error(f"Restore failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to restore database: {e}")
        return False

# Database health check
def health_check() -> Dict[str, Any]:
    """Comprehensive database health check"""
    health_status = {
        "database": {
            "status": "unknown",
            "connection": False,
            "tables": 0,
            "size": "unknown"
        },
        "modules": {}
    }
    
    # Check connection
    if check_db_connection():
        health_status["database"]["connection"] = True
        health_status["database"]["status"] = "connected"
        
        # Get database info
        db_info = get_db_info()
        health_status["database"].update(db_info)
        
        # Check module tables
        module_tables = [
            "insar_subsidence_data", "flood_modeling_data", "groundwater_data",
            "iot_sensor_data", "drought_data", "water_network_data",
            "drinking_water_data", "transboundary_basin_data", "dust_storm_data",
            "datacenter_water_data", "agricultural_reservoir_data",
            "urban_green_space_data", "environmental_health_data"
        ]
        
        try:
            with engine.connect() as connection:
                for table in module_tables:
                    try:
                        result = connection.execute(f"SELECT COUNT(*) FROM {table}")
                        count = result.scalar()
                        health_status["modules"][table] = {
                            "status": "exists",
                            "record_count": count
                        }
                    except Exception:
                        health_status["modules"][table] = {
                            "status": "missing",
                            "record_count": 0
                        }
        except Exception as e:
            health_status["database"]["status"] = f"error: {e}"
    else:
        health_status["database"]["status"] = "disconnected"
    
    return health_status 