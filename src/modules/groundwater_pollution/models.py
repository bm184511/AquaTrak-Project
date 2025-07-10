"""
Groundwater Pollution Analysis Models
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


class PollutionType(str, Enum):
    """Types of groundwater pollution"""
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    RADIOACTIVE = "radioactive"
    NUTRIENT = "nutrient"
    HEAVY_METAL = "heavy_metal"
    ORGANIC = "organic"
    MICROPLASTIC = "microplastic"


class ContaminantCategory(str, Enum):
    """Contaminant categories"""
    PESTICIDES = "pesticides"
    FERTILIZERS = "fertilizers"
    INDUSTRIAL_CHEMICALS = "industrial_chemicals"
    PETROLEUM_PRODUCTS = "petroleum_products"
    HEAVY_METALS = "heavy_metals"
    PATHOGENS = "pathogens"
    PHARMACEUTICALS = "pharmaceuticals"
    RADIONUCLIDES = "radionuclides"


class RiskLevel(str, Enum):
    """Risk levels for groundwater pollution"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SamplingMethod(str, Enum):
    """Groundwater sampling methods"""
    GRAB_SAMPLE = "grab_sample"
    COMPOSITE_SAMPLE = "composite_sample"
    CONTINUOUS_MONITORING = "continuous_monitoring"
    PASSIVE_SAMPLING = "passive_sampling"


class PollutionAnalysisRequest(BaseModel):
    """Request model for groundwater pollution analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_name: str = Field(..., description="Name of the monitoring site")
    coordinates: Dict[str, float] = Field(..., description="Site coordinates")
    aquifer_type: str = Field(..., description="Type of aquifer")
    depth_to_water: float = Field(..., ge=0, description="Depth to water table in meters")
    sampling_method: SamplingMethod = Field(..., description="Sampling method used")
    contaminants_of_concern: List[ContaminantCategory] = Field(..., description="Contaminants to analyze")
    sampling_data: Dict[str, Any] = Field(..., description="Sampling data and measurements")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical pollution data")
    land_use_data: Optional[Dict[str, Any]] = Field(None, description="Land use information")
    hydrogeological_data: Optional[Dict[str, Any]] = Field(None, description="Hydrogeological parameters")
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


class PollutionModel(BaseModel):
    """Groundwater pollution model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of pollution model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContaminantMeasurement(BaseModel):
    """Individual contaminant measurement"""
    contaminant: str = Field(..., description="Contaminant name")
    concentration: float = Field(..., ge=0, description="Concentration value")
    unit: str = Field(..., description="Concentration unit")
    detection_limit: Optional[float] = Field(None, ge=0, description="Detection limit")
    measurement_date: datetime = Field(..., description="Date of measurement")
    sample_id: str = Field(..., description="Sample identifier")


class PollutionResult(BaseModel):
    """Groundwater pollution analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    contaminant_levels: Dict[str, ContaminantMeasurement] = Field(..., description="Contaminant measurements")
    risk_assessment: Dict[str, RiskLevel] = Field(..., description="Risk assessment by contaminant")
    overall_risk: RiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")
    plume_extent: Optional[float] = Field(None, ge=0, description="Contaminant plume extent in square meters")
    migration_rate: Optional[float] = Field(None, description="Contaminant migration rate")
    health_risk: Dict[str, Any] = Field(default_factory=dict, description="Human health risk assessment")
    environmental_impact: Dict[str, Any] = Field(default_factory=dict, description="Environmental impact assessment")
    remediation_recommendations: List[str] = Field(default_factory=list, description="Remediation recommendations")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PollutionAlert(BaseModel):
    """Groundwater pollution alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_name: str = Field(..., description="Monitoring site name")
    contaminant: str = Field(..., description="Contaminant of concern")
    threshold_concentration: float = Field(..., ge=0, description="Concentration threshold")
    threshold_risk: RiskLevel = Field(..., description="Risk threshold for alert")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PollutionReport(BaseModel):
    """Groundwater pollution analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    regulatory_compliance: Dict[str, Any] = Field(default_factory=dict, description="Regulatory compliance assessment")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class WaterQualityStandard(BaseModel):
    """Water quality standards for contaminants"""
    contaminant: str = Field(..., description="Contaminant name")
    standard_type: str = Field(..., description="Type of standard (drinking water, environmental, etc.)")
    maximum_concentration: float = Field(..., ge=0, description="Maximum allowable concentration")
    unit: str = Field(..., description="Concentration unit")
    jurisdiction: str = Field(..., description="Jurisdiction or authority")
    effective_date: datetime = Field(..., description="Effective date of standard")
    source: str = Field(..., description="Source of the standard")


class RemediationAction(BaseModel):
    """Remediation action recommendation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = Field(..., description="Type of remediation action")
    description: str = Field(..., description="Action description")
    priority: str = Field(..., description="Priority level")
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated cost")
    timeline: Optional[str] = Field(None, description="Estimated timeline")
    effectiveness: Optional[float] = Field(None, ge=0, le=100, description="Expected effectiveness percentage")
    requirements: List[str] = Field(default_factory=list, description="Requirements for implementation") 