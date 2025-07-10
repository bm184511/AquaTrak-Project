"""
Data Center Water Consumption Models
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


class CoolingSystemType(str, Enum):
    """Types of data center cooling systems"""
    AIR_COOLED = "air_cooled"
    WATER_COOLED = "water_cooled"
    EVAPORATIVE = "evaporative"
    IMMERSION = "immersion"
    HYBRID = "hybrid"


class DataCenterTier(str, Enum):
    """Data center tier classifications"""
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    TIER_4 = "tier_4"


class EfficiencyMetric(str, Enum):
    """Data center efficiency metrics"""
    PUE = "pue"  # Power Usage Effectiveness
    WUE = "wue"  # Water Usage Effectiveness
    CUE = "cue"  # Carbon Usage Effectiveness
    ERE = "ere"  # Energy Reuse Effectiveness


class DataCenterAnalysisRequest(BaseModel):
    """Request model for data center water analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_name: str = Field(..., description="Data center facility name")
    coordinates: Dict[str, float] = Field(..., description="Facility coordinates")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    cooling_system_type: CoolingSystemType = Field(..., description="Primary cooling system type")
    data_center_tier: DataCenterTier = Field(..., description="Data center tier")
    it_load: float = Field(..., ge=0, description="IT load in kW")
    total_power: float = Field(..., ge=0, description="Total power consumption in kW")
    water_consumption_data: Dict[str, Any] = Field(..., description="Water consumption data")
    efficiency_metrics: Optional[Dict[str, float]] = Field(None, description="Current efficiency metrics")
    climate_data: Optional[Dict[str, Any]] = Field(None, description="Local climate data")
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


class DataCenterModel(BaseModel):
    """Data center water model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of data center model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CoolingSystem(BaseModel):
    """Cooling system configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    system_name: str = Field(..., description="System name")
    system_type: CoolingSystemType = Field(..., description="Cooling system type")
    capacity: float = Field(..., ge=0, description="Cooling capacity in kW")
    efficiency: float = Field(..., ge=0, le=100, description="System efficiency percentage")
    water_consumption_rate: float = Field(..., ge=0, description="Water consumption rate in L/kWh")
    energy_consumption: float = Field(..., ge=0, description="Energy consumption in kW")
    operating_hours: float = Field(..., ge=0, le=8760, description="Annual operating hours")
    maintenance_schedule: Optional[Dict[str, Any]] = Field(None, description="Maintenance schedule")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WaterConsumptionData(BaseModel):
    """Water consumption data point"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str = Field(..., description="Facility identifier")
    timestamp: datetime = Field(..., description="Data timestamp")
    total_consumption: float = Field(..., ge=0, description="Total water consumption in liters")
    cooling_consumption: float = Field(..., ge=0, description="Cooling system consumption")
    domestic_consumption: float = Field(..., ge=0, description="Domestic water consumption")
    fire_suppression: float = Field(..., ge=0, description="Fire suppression system consumption")
    humidity_control: float = Field(..., ge=0, description="Humidity control consumption")
    source: str = Field(..., description="Water source")
    quality_parameters: Optional[Dict[str, float]] = Field(None, description="Water quality parameters")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EfficiencyMetrics(BaseModel):
    """Data center efficiency metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str = Field(..., description="Facility identifier")
    measurement_date: datetime = Field(..., description="Measurement date")
    pue: float = Field(..., ge=1, description="Power Usage Effectiveness")
    wue: float = Field(..., ge=0, description="Water Usage Effectiveness in L/kWh")
    cue: float = Field(..., ge=0, description="Carbon Usage Effectiveness")
    ere: float = Field(..., ge=0, le=1, description="Energy Reuse Effectiveness")
    it_energy: float = Field(..., ge=0, description="IT energy consumption in kWh")
    cooling_energy: float = Field(..., ge=0, description="Cooling energy consumption in kWh")
    total_water: float = Field(..., ge=0, description="Total water consumption in liters")
    carbon_footprint: float = Field(..., ge=0, description="Carbon footprint in kg CO2")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SustainabilityAssessment(BaseModel):
    """Sustainability assessment for data center"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str = Field(..., description="Facility identifier")
    assessment_date: datetime = Field(..., description="Assessment date")
    sustainability_score: float = Field(..., ge=0, le=100, description="Overall sustainability score")
    water_efficiency_score: float = Field(..., ge=0, le=100, description="Water efficiency score")
    energy_efficiency_score: float = Field(..., ge=0, le=100, description="Energy efficiency score")
    carbon_efficiency_score: float = Field(..., ge=0, le=100, description="Carbon efficiency score")
    renewable_energy_usage: float = Field(..., ge=0, le=100, description="Renewable energy usage percentage")
    water_recycling_rate: float = Field(..., ge=0, le=100, description="Water recycling rate percentage")
    waste_heat_recovery: float = Field(..., ge=0, le=100, description="Waste heat recovery percentage")
    certifications: List[str] = Field(default_factory=list, description="Sustainability certifications")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DataCenterResult(BaseModel):
    """Data center water analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    facility_summary: Dict[str, Any] = Field(..., description="Facility summary")
    water_consumption_analysis: Dict[str, float] = Field(..., description="Water consumption analysis")
    efficiency_analysis: Dict[str, float] = Field(..., description="Efficiency analysis")
    sustainability_assessment: SustainabilityAssessment = Field(..., description="Sustainability assessment")
    optimization_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Optimization opportunities")
    cost_analysis: Dict[str, float] = Field(..., description="Cost analysis")
    environmental_impact: Dict[str, Any] = Field(..., description="Environmental impact assessment")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DataCenterAlert(BaseModel):
    """Data center water alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_name: str = Field(..., description="Facility name")
    alert_type: str = Field(..., description="Type of alert")
    water_consumption_threshold: float = Field(..., ge=0, description="Water consumption threshold")
    efficiency_threshold: float = Field(..., ge=0, description="Efficiency threshold")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataCenterReport(BaseModel):
    """Data center water analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    sustainability_metrics: Dict[str, Any] = Field(default_factory=dict, description="Sustainability metrics")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class OptimizationRecommendation(BaseModel):
    """Data center optimization recommendation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str = Field(..., description="Facility identifier")
    recommendation_type: str = Field(..., description="Type of optimization")
    description: str = Field(..., description="Recommendation description")
    priority: str = Field(..., description="Implementation priority")
    water_savings: float = Field(..., ge=0, description="Expected water savings in liters")
    energy_savings: float = Field(..., ge=0, description="Expected energy savings in kWh")
    cost_savings: float = Field(..., ge=0, description="Expected cost savings")
    implementation_cost: float = Field(..., ge=0, description="Implementation cost")
    payback_period: Optional[float] = Field(None, ge=0, description="Payback period in months")
    carbon_reduction: float = Field(..., ge=0, description="Expected carbon reduction in kg CO2")
    requirements: List[str] = Field(default_factory=list, description="Implementation requirements")
    timeline: str = Field(..., description="Implementation timeline")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClimateImpact(BaseModel):
    """Climate impact on data center water consumption"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str = Field(..., description="Facility identifier")
    analysis_date: datetime = Field(..., description="Analysis date")
    temperature_impact: float = Field(..., description="Temperature impact on consumption")
    humidity_impact: float = Field(..., description="Humidity impact on consumption")
    seasonal_variation: Dict[str, float] = Field(default_factory=dict, description="Seasonal variation")
    climate_risk_score: float = Field(..., ge=0, le=100, description="Climate risk score")
    adaptation_measures: List[str] = Field(default_factory=list, description="Adaptation measures")
    created_at: datetime = Field(default_factory=datetime.utcnow) 