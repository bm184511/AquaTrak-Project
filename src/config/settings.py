"""
Settings Configuration
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application settings with Docker optimizations"""
    
    # Environment
    environment: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database settings
    database_url: str = Field(
        default="postgresql://aquatrak:aquatrak123@localhost:5432/aquatrak_db",
        description="Database connection URL"
    )
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    db_max_overflow: int = Field(default=20, description="Database max overflow")
    db_pool_timeout: int = Field(default=30, description="Database pool timeout")
    db_pool_recycle: int = Field(default=3600, description="Database pool recycle time")
    
    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # API settings
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    
    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiry")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiry days")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed hosts")
    
    # Data import settings
    max_import_workers: int = Field(default=4, description="Maximum import workers")
    import_batch_size: int = Field(default=1000, description="Import batch size")
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Maximum file size (100MB)")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # External API settings
    weather_api_key: Optional[str] = Field(default=None, description="Weather API key")
    satellite_api_key: Optional[str] = Field(default=None, description="Satellite API key")
    
    # Country configuration
    default_country: str = Field(default="US", description="Default country")
    supported_countries: List[str] = Field(default_factory=list, description="Supported countries")
    supported_languages: List[str] = Field(default_factory=lambda: ["en", "fa"], description="Supported languages")
    default_language: str = Field(default="en", description="Default language")
    
    # Celery settings
    celery_broker_url: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", description="Celery result backend")
    celery_worker_concurrency: int = Field(default=4, description="Celery worker concurrency")
    celery_task_time_limit: int = Field(default=3600, description="Celery task time limit")
    celery_task_soft_time_limit: int = Field(default=3000, description="Celery task soft time limit")
    
    # File storage settings
    upload_path: str = Field(default="/app/uploads", description="Upload directory path")
    static_path: str = Field(default="/app/static", description="Static files path")
    temp_path: str = Field(default="/app/temp", description="Temporary files path")
    
    # Monitoring settings
    prometheus_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    @validator('database_url', pre=True)
    def validate_database_url(cls, v):
        """Validate database URL"""
        if not v:
            raise ValueError("Database URL is required")
        return v
    
    @validator('secret_key', pre=True)
    def validate_secret_key(cls, v):
        """Validate secret key"""
        if v == "your-secret-key-change-in-production":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("Secret key must be changed in production")
        return v
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def update_settings(**kwargs) -> None:
    """Update application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    
    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)

def reset_settings() -> None:
    """Reset settings to default"""
    global _settings
    _settings = None 