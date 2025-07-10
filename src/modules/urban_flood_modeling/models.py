"""
Urban Flood Modeling Models
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class FloodModelType(str, Enum):
    """Types of flood models supported"""
    HYDROLOGICAL = "hydrological"
    HYDRAULIC = "hydraulic"
    COMBINED = "combined"
    URBAN_DRAINAGE = "urban_drainage"


class RainfallIntensity(str, Enum):
    """Rainfall intensity categories"""
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    EXTREME = "extreme"


class FloodSeverity(str, Enum):
    """Flood severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"


class FloodAnalysisRequest(BaseModel):
    """Request model for flood analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    area_name: str = Field(..., description="Name of the urban area")
    coordinates: Dict[str, float] = Field(..., description="Area coordinates")
    model_type: FloodModelType = Field(..., description="Type of flood model to use")
    rainfall_intensity: RainfallIntensity = Field(..., description="Expected rainfall intensity")
    duration_hours: int = Field(..., ge=1, le=168, description="Duration of rainfall in hours")
    return_period: int = Field(..., ge=2, le=1000, description="Return period in years")
    urban_parameters: Dict[str, Any] = Field(default_factory=dict, description="Urban development parameters")
    elevation_data_path: Optional[str] = Field(None, description="Path to elevation data")
    land_use_data_path: Optional[str] = Field(None, description="Path to land use data")
    drainage_data_path: Optional[str] = Field(None, description="Path to drainage network data")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(..., description="User requesting the analysis")

    @validator('coordinates')
    def validate_coordinates(cls, v):
        required_keys = ['lat', 'lon']
        if not all(key in v for key in required_keys):
            raise ValueError("Coordinates must contain 'lat' and 'lon'")
        if not (-90 <= v['lat'] <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= v['lon'] <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class FloodModel(BaseModel):
    """Flood model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: FloodModelType = Field(..., description="Type of flood model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FloodResult(BaseModel):
    """Flood analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    flood_depth_map: Dict[str, float] = Field(..., description="Flood depth at different locations")
    flood_extent: float = Field(..., ge=0, description="Total flood extent in square meters")
    max_depth: float = Field(..., ge=0, description="Maximum flood depth in meters")
    affected_area: float = Field(..., ge=0, description="Affected area in square meters")
    severity: FloodSeverity = Field(..., description="Flood severity level")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")
    evacuation_zones: List[Dict[str, Any]] = Field(default_factory=list, description="Recommended evacuation zones")
    infrastructure_impact: Dict[str, Any] = Field(default_factory=dict, description="Impact on infrastructure")
    economic_loss_estimate: float = Field(..., ge=0, description="Estimated economic loss")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FloodAlert(BaseModel):
    """Flood alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    area_name: str = Field(..., description="Area name")
    threshold_depth: float = Field(..., ge=0, description="Depth threshold for alert")
    threshold_severity: FloodSeverity = Field(..., description="Severity threshold for alert")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FloodReport(BaseModel):
    """Flood analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file") 