"""
Drinking Water Quality Analysis Models
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


class QualityParameter(str, Enum):
    """Drinking water quality parameters"""
    PH = "ph"
    TURBIDITY = "turbidity"
    CHLORINE = "chlorine"
    FLUORIDE = "fluoride"
    NITRATE = "nitrate"
    NITRITE = "nitrite"
    ARSENIC = "arsenic"
    LEAD = "lead"
    MERCURY = "mercury"
    CADMIUM = "cadmium"
    CHROMIUM = "chromium"
    BACTERIA_TOTAL = "bacteria_total"
    BACTERIA_FECAL = "bacteria_fecal"
    E_COLI = "e_coli"
    TOTAL_DISSOLVED_SOLIDS = "total_dissolved_solids"
    HARDNESS = "hardness"
    ALKALINITY = "alkalinity"
    CONDUCTIVITY = "conductivity"
    TEMPERATURE = "temperature"
    DISSOLVED_OXYGEN = "dissolved_oxygen"


class ComplianceStatus(str, Enum):
    """Water quality compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    MARGINAL = "marginal"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthRiskLevel(str, Enum):
    """Health risk levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SamplingPoint(str, Enum):
    """Types of sampling points"""
    TREATMENT_PLANT = "treatment_plant"
    DISTRIBUTION_SYSTEM = "distribution_system"
    CONSUMER_TAP = "consumer_tap"
    RESERVOIR = "reservoir"
    WELL = "well"
    SPRING = "spring"


class QualityAnalysisRequest(BaseModel):
    """Request model for drinking water quality analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    water_system_name: str = Field(..., description="Water system name")
    sampling_location: Dict[str, float] = Field(..., description="Sampling location coordinates")
    sampling_point: SamplingPoint = Field(..., description="Type of sampling point")
    parameters: List[QualityParameter] = Field(..., description="Quality parameters to analyze")
    sampling_data: Dict[str, Any] = Field(..., description="Sampling data and measurements")
    regulatory_standards: Optional[Dict[str, Any]] = Field(None, description="Applicable regulatory standards")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical quality data")
    treatment_process: Optional[Dict[str, Any]] = Field(None, description="Water treatment process information")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(..., description="User requesting the analysis")

    @validator('sampling_location')
    def validate_sampling_location(cls, v):
        required_keys = ['lat', 'lon']
        if not all(key in v for key in required_keys):
            raise ValueError("Sampling location must contain 'lat' and 'lon'")
        if not (-90 <= v['lat'] <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= v['lon'] <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class QualityModel(BaseModel):
    """Water quality analysis model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Quality model name")
    model_type: str = Field(..., description="Type of quality model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QualityMeasurement(BaseModel):
    """Individual quality parameter measurement"""
    parameter: QualityParameter = Field(..., description="Quality parameter")
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Measurement unit")
    detection_limit: Optional[float] = Field(None, ge=0, description="Detection limit")
    measurement_date: datetime = Field(..., description="Date of measurement")
    sample_id: str = Field(..., description="Sample identifier")
    laboratory: Optional[str] = Field(None, description="Laboratory that performed analysis")
    method: Optional[str] = Field(None, description="Analytical method used")
    quality_flag: Optional[str] = Field(None, description="Data quality flag")


class RegulatoryStandard(BaseModel):
    """Regulatory standard for quality parameter"""
    parameter: QualityParameter = Field(..., description="Quality parameter")
    standard_type: str = Field(..., description="Type of standard")
    maximum_concentration: float = Field(..., ge=0, description="Maximum allowable concentration")
    unit: str = Field(..., description="Concentration unit")
    jurisdiction: str = Field(..., description="Regulatory jurisdiction")
    effective_date: datetime = Field(..., description="Effective date of standard")
    source: str = Field(..., description="Source of the standard")
    health_basis: Optional[str] = Field(None, description="Health basis for standard")


class QualityResult(BaseModel):
    """Drinking water quality analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    measurements: Dict[str, QualityMeasurement] = Field(..., description="Quality measurements")
    compliance_assessment: Dict[str, ComplianceStatus] = Field(..., description="Compliance assessment by parameter")
    overall_compliance: ComplianceStatus = Field(..., description="Overall compliance status")
    health_risk_assessment: Dict[str, HealthRiskLevel] = Field(..., description="Health risk assessment")
    overall_health_risk: HealthRiskLevel = Field(..., description="Overall health risk level")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")
    trend_analysis: Dict[str, List[float]] = Field(..., description="Quality trend analysis")
    treatment_recommendations: List[str] = Field(default_factory=list, description="Treatment recommendations")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    regulatory_reporting: Dict[str, Any] = Field(..., description="Regulatory reporting requirements")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QualityAlert(BaseModel):
    """Water quality alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    water_system_name: str = Field(..., description="Water system name")
    parameter: QualityParameter = Field(..., description="Quality parameter")
    threshold_value: float = Field(..., ge=0, description="Threshold value")
    condition: str = Field(..., description="Alert condition")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QualityReport(BaseModel):
    """Drinking water quality analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    regulatory_compliance: Dict[str, Any] = Field(default_factory=dict, description="Regulatory compliance assessment")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file") 