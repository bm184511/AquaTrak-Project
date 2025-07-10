"""
Settings Configuration
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    database_url: str = Field(
        default="postgresql://aquatrak:aquatrak123@localhost:5432/aquatrak_db",
        description="Database connection URL"
    )
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    db_max_overflow: int = Field(default=20, description="Database max overflow")
    db_pool_timeout: int = Field(default=30, description="Database pool timeout")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=True, description="Debug mode")
    
    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiry")
    
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
    supported_countries: list = Field(default_factory=list, description="Supported countries")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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