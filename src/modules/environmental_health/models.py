"""
Environmental Health Models
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from models.base import Base

class EnvironmentalHealthData(Base):
    """Environmental Health Data Model"""
    __tablename__ = "environmental_health_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    air_quality = Column(JSON, default={})
    water_quality = Column(JSON, default={})
    soil_quality = Column(JSON, default={})
    noise_levels = Column(JSON, default={})
    environmental_indicators = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 