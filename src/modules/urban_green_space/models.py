"""
Urban Green Space Models
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
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from models.base import Base


class GreenSpaceType(str, Enum):
    """Types of urban green spaces"""
    PARK = "park"
    GARDEN = "garden"
    FOREST = "forest"
    WETLAND = "wetland"
    GREEN_ROOF = "green_roof"
    GREEN_WALL = "green_wall"
    URBAN_FARM = "urban_farm"
    COMMUNITY_GARDEN = "community_garden"


class VegetationType(str, Enum):
    """Types of vegetation"""
    TREES = "trees"
    SHRUBS = "shrubs"
    GRASS = "grass"
    FLOWERS = "flowers"
    CROPS = "crops"
    NATIVE_PLANTS = "native_plants"
    DROUGHT_RESISTANT = "drought_resistant"


class EcosystemService(str, Enum):
    """Ecosystem services provided by green spaces"""
    CARBON_SEQUESTRATION = "carbon_sequestration"
    AIR_PURIFICATION = "air_purification"
    WATER_FILTRATION = "water_filtration"
    FLOOD_CONTROL = "flood_control"
    URBAN_COOLING = "urban_cooling"
    BIODIVERSITY = "biodiversity"
    RECREATION = "recreation"
    NOISE_REDUCTION = "noise_reduction"


class GreenSpaceAnalysisRequest(BaseModel):
    """Request model for urban green space analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    green_space_name: str = Field(..., description="Green space name")
    coordinates: Dict[str, float] = Field(..., description="Green space coordinates")
    green_space_type: GreenSpaceType = Field(..., description="Type of green space")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    vegetation_data: Dict[str, Any] = Field(..., description="Vegetation information")
    water_management_data: Optional[Dict[str, Any]] = Field(None, description="Water management data")
    climate_data: Optional[Dict[str, Any]] = Field(None, description="Local climate data")
    soil_data: Optional[Dict[str, Any]] = Field(None, description="Soil characteristics")
    usage_data: Optional[Dict[str, Any]] = Field(None, description="Usage patterns")
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

    @validator('analysis_period')
    def validate_analysis_period(cls, v):
        required_keys = ['start', 'end']
        if not all(key in v for key in required_keys):
            raise ValueError("Analysis period must contain 'start' and 'end'")
        if v['start'] >= v['end']:
            raise ValueError("Start date must be before end date")
        return v


class GreenSpaceModel(BaseModel):
    """Urban green space model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of green space model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VegetationData(BaseModel):
    """Vegetation information and health data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    green_space_id: str = Field(..., description="Green space identifier")
    vegetation_type: VegetationType = Field(..., description="Type of vegetation")
    species_name: str = Field(..., description="Species name")
    area_coverage: float = Field(..., ge=0, description="Area coverage in square meters")
    density: float = Field(..., ge=0, description="Plant density per square meter")
    health_score: float = Field(..., ge=0, le=100, description="Health score percentage")
    water_requirement: float = Field(..., ge=0, description="Water requirement in liters per day")
    drought_tolerance: str = Field(..., description="Drought tolerance level")
    maintenance_needs: str = Field(..., description="Maintenance requirements")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WaterManagement(BaseModel):
    """Water management system data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    green_space_id: str = Field(..., description="Green space identifier")
    irrigation_system: str = Field(..., description="Type of irrigation system")
    water_source: str = Field(..., description="Water source")
    daily_consumption: float = Field(..., ge=0, description="Daily water consumption in liters")
    efficiency: float = Field(..., ge=0, le=100, description="Water use efficiency percentage")
    rainwater_harvesting: bool = Field(default=False, description="Rainwater harvesting system")
    storage_capacity: Optional[float] = Field(None, ge=0, description="Storage capacity in liters")
    recycling_system: bool = Field(default=False, description="Water recycling system")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EcosystemServiceAssessment(BaseModel):
    """Ecosystem service assessment"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    green_space_id: str = Field(..., description="Green space identifier")
    service_type: EcosystemService = Field(..., description="Type of ecosystem service")
    service_value: float = Field(..., ge=0, description="Service value")
    unit: str = Field(..., description="Value unit")
    assessment_date: datetime = Field(..., description="Assessment date")
    methodology: str = Field(..., description="Assessment methodology")
    confidence_level: float = Field(..., ge=0, le=100, description="Confidence level percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GreenSpaceResult(BaseModel):
    """Urban green space analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    green_space_summary: Dict[str, Any] = Field(..., description="Green space summary")
    vegetation_analysis: Dict[str, Any] = Field(..., description="Vegetation analysis")
    water_management_analysis: Dict[str, Any] = Field(..., description="Water management analysis")
    ecosystem_services: List[EcosystemServiceAssessment] = Field(default_factory=list, description="Ecosystem services assessment")
    optimization_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Optimization opportunities")
    sustainability_score: float = Field(..., ge=0, le=100, description="Sustainability score")
    water_efficiency_score: float = Field(..., ge=0, le=100, description="Water efficiency score")
    biodiversity_score: float = Field(..., ge=0, le=100, description="Biodiversity score")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GreenSpaceAlert(BaseModel):
    """Green space alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    green_space_name: str = Field(..., description="Green space name")
    alert_type: str = Field(..., description="Type of alert")
    vegetation_health_threshold: float = Field(..., ge=0, le=100, description="Vegetation health threshold")
    water_consumption_threshold: float = Field(..., ge=0, description="Water consumption threshold")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GreenSpaceReport(BaseModel):
    """Urban green space analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    seasonal_analysis: Dict[str, Any] = Field(default_factory=dict, description="Seasonal analysis")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class OptimizationStrategy(BaseModel):
    """Green space optimization strategy"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    green_space_id: str = Field(..., description="Green space identifier")
    strategy_name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    water_savings: float = Field(..., ge=0, description="Expected water savings")
    biodiversity_improvement: float = Field(..., ge=0, le=100, description="Expected biodiversity improvement")
    ecosystem_service_enhancement: Dict[str, float] = Field(default_factory=dict, description="Ecosystem service enhancements")
    implementation_cost: float = Field(..., ge=0, description="Implementation cost")
    payback_period: Optional[float] = Field(None, ge=0, description="Payback period in months")
    requirements: List[str] = Field(default_factory=list, description="Implementation requirements")
    timeline: str = Field(..., description="Implementation timeline")
    priority: str = Field(..., description="Implementation priority")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClimateImpact(BaseModel):
    """Climate impact on green space performance"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    green_space_id: str = Field(..., description="Green space identifier")
    analysis_date: datetime = Field(..., description="Analysis date")
    temperature_impact: float = Field(..., description="Temperature impact on vegetation")
    rainfall_impact: float = Field(..., description="Rainfall impact on water needs")
    drought_risk: float = Field(..., ge=0, le=100, description="Drought risk score")
    adaptation_measures: List[str] = Field(default_factory=list, description="Adaptation measures")
    resilience_score: float = Field(..., ge=0, le=100, description="Climate resilience score")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GreenSpaceData(Base):
    """Urban Green Space Data Model"""
    __tablename__ = "urban_green_space_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(JSON, nullable=False)
    green_space_type = Column(String(50), nullable=False)
    vegetation_data = Column(JSON, default={})
    ecosystem_services = Column(JSON, default={})
    accessibility = Column(JSON, default={})
    maintenance_status = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 