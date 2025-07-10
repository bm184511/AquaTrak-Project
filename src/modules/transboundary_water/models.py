"""
Transboundary Water Modeling Models
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


class BasinType(str, Enum):
    """Types of transboundary basins"""
    RIVER = "river"
    LAKE = "lake"
    AQUIFER = "aquifer"
    ESTUARY = "estuary"
    DELTA = "delta"


class AgreementStatus(str, Enum):
    """Status of international water agreements"""
    ACTIVE = "active"
    EXPIRED = "expired"
    NEGOTIATING = "negotiating"
    DISPUTED = "disputed"
    NON_EXISTENT = "non_existent"


class ConflictLevel(str, Enum):
    """Levels of water conflict"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class WaterUse(str, Enum):
    """Types of water use in transboundary basins"""
    AGRICULTURE = "agriculture"
    DOMESTIC = "domestic"
    INDUSTRIAL = "industrial"
    HYDROPOWER = "hydropower"
    NAVIGATION = "navigation"
    ENVIRONMENTAL = "environmental"
    RECREATION = "recreation"


class TransboundaryAnalysisRequest(BaseModel):
    """Request model for transboundary water analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    basin_name: str = Field(..., description="Name of the transboundary basin")
    basin_type: BasinType = Field(..., description="Type of transboundary basin")
    countries: List[str] = Field(..., description="Countries sharing the basin")
    coordinates: Dict[str, float] = Field(..., description="Basin coordinates")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    water_uses: List[WaterUse] = Field(..., description="Water uses to analyze")
    agreement_data: Optional[Dict[str, Any]] = Field(None, description="International agreement data")
    hydrological_data: Optional[Dict[str, Any]] = Field(None, description="Hydrological data")
    population_data: Optional[Dict[str, Any]] = Field(None, description="Population data")
    economic_data: Optional[Dict[str, Any]] = Field(None, description="Economic data")
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


class TransboundaryModel(BaseModel):
    """Transboundary water model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of transboundary model")
    basin_id: str = Field(..., description="Basin identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InternationalAgreement(BaseModel):
    """International water agreement model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agreement_name: str = Field(..., description="Name of the agreement")
    basin_name: str = Field(..., description="Basin covered by agreement")
    signatory_countries: List[str] = Field(..., description="Countries that signed")
    signing_date: datetime = Field(..., description="Date of signing")
    effective_date: datetime = Field(..., description="Effective date")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date")
    status: AgreementStatus = Field(..., description="Current status")
    key_provisions: List[str] = Field(default_factory=list, description="Key provisions")
    water_allocation: Dict[str, float] = Field(default_factory=dict, description="Water allocation by country")
    dispute_resolution: Optional[str] = Field(None, description="Dispute resolution mechanism")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WaterAllocation(BaseModel):
    """Water allocation model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    basin_id: str = Field(..., description="Basin identifier")
    country: str = Field(..., description="Country name")
    water_use: WaterUse = Field(..., description="Type of water use")
    allocated_volume: float = Field(..., ge=0, description="Allocated volume in cubic meters")
    actual_use: float = Field(..., ge=0, description="Actual water use")
    efficiency: float = Field(..., ge=0, le=100, description="Use efficiency percentage")
    allocation_date: datetime = Field(..., description="Allocation date")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConflictAssessment(BaseModel):
    """Water conflict assessment model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    basin_id: str = Field(..., description="Basin identifier")
    conflict_level: ConflictLevel = Field(..., description="Level of conflict")
    conflict_type: str = Field(..., description="Type of conflict")
    affected_countries: List[str] = Field(..., description="Countries involved")
    conflict_factors: List[str] = Field(default_factory=list, description="Factors contributing to conflict")
    risk_score: float = Field(..., ge=0, le=100, description="Conflict risk score")
    economic_impact: Optional[float] = Field(None, ge=0, description="Economic impact estimate")
    resolution_recommendations: List[str] = Field(default_factory=list, description="Resolution recommendations")
    assessment_date: datetime = Field(..., description="Assessment date")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TransboundaryResult(BaseModel):
    """Transboundary water analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    basin_summary: Dict[str, Any] = Field(..., description="Basin summary information")
    water_balance: Dict[str, float] = Field(..., description="Water balance analysis")
    allocation_analysis: Dict[str, WaterAllocation] = Field(..., description="Water allocation analysis")
    conflict_assessment: ConflictAssessment = Field(..., description="Conflict assessment")
    agreement_analysis: Dict[str, Any] = Field(..., description="Agreement analysis")
    sustainability_score: float = Field(..., ge=0, le=100, description="Sustainability score")
    cooperation_index: float = Field(..., ge=0, le=100, description="Cooperation index")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TransboundaryAlert(BaseModel):
    """Transboundary water alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    basin_name: str = Field(..., description="Basin name")
    alert_type: str = Field(..., description="Type of alert")
    conflict_threshold: ConflictLevel = Field(..., description="Conflict threshold for alert")
    water_shortage_threshold: float = Field(..., ge=0, description="Water shortage threshold")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TransboundaryReport(BaseModel):
    """Transboundary water analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    policy_implications: Dict[str, Any] = Field(default_factory=dict, description="Policy implications")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class BasinProfile(BaseModel):
    """Transboundary basin profile"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Basin name")
    basin_type: BasinType = Field(..., description="Basin type")
    countries: List[str] = Field(..., description="Countries sharing the basin")
    area: float = Field(..., ge=0, description="Basin area in square kilometers")
    population: int = Field(..., ge=0, description="Total population")
    annual_flow: float = Field(..., ge=0, description="Annual flow in cubic meters")
    major_uses: List[WaterUse] = Field(default_factory=list, description="Major water uses")
    agreements: List[str] = Field(default_factory=list, description="Related agreements")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CooperationMetric(BaseModel):
    """Cooperation metrics for transboundary basins"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    basin_id: str = Field(..., description="Basin identifier")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    measurement_date: datetime = Field(..., description="Measurement date")
    trend: Optional[str] = Field(None, description="Trend direction")
    benchmark: Optional[float] = Field(None, description="Benchmark value")
    created_at: datetime = Field(default_factory=datetime.utcnow) 