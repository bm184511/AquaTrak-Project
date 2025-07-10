"""
InSAR Subsidence Models
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from models.base import Base

class InsarSubsidenceData(Base):
    """InSAR Subsidence Data Model"""
    __tablename__ = "insar_subsidence_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    subsidence_rate = Column(Float, nullable=False)
    deformation_data = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now()) 