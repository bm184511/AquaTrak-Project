"""
IoT Water Consumption Models
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


class DeviceType(str, Enum):
    """Types of IoT water monitoring devices"""
    FLOW_METER = "flow_meter"
    PRESSURE_SENSOR = "pressure_sensor"
    QUALITY_SENSOR = "quality_sensor"
    LEVEL_SENSOR = "level_sensor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    PH_SENSOR = "ph_sensor"
    TURBIDITY_SENSOR = "turbidity_sensor"


class IndustryType(str, Enum):
    """Types of industrial facilities"""
    MANUFACTURING = "manufacturing"
    CHEMICAL = "chemical"
    FOOD_BEVERAGE = "food_beverage"
    PHARMACEUTICAL = "pharmaceutical"
    TEXTILE = "textile"
    PAPER_PULP = "paper_pulp"
    MINING = "mining"
    POWER_GENERATION = "power_generation"


class ConsumptionPattern(str, Enum):
    """Water consumption patterns"""
    CONTINUOUS = "continuous"
    BATCH = "batch"
    SEASONAL = "seasonal"
    INTERMITTENT = "intermittent"
    PEAK_LOAD = "peak_load"


class OptimizationStatus(str, Enum):
    """Optimization implementation status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ON_HOLD = "on_hold"


class IoTDeviceData(BaseModel):
    """IoT device data model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = Field(..., description="Unique device identifier")
    device_type: DeviceType = Field(..., description="Type of IoT device")
    timestamp: datetime = Field(..., description="Data timestamp")
    location: Dict[str, float] = Field(..., description="Device location coordinates")
    measurements: Dict[str, float] = Field(..., description="Sensor measurements")
    status: str = Field(..., description="Device status")
    battery_level: Optional[float] = Field(None, ge=0, le=100, description="Battery level percentage")
    signal_strength: Optional[float] = Field(None, ge=0, le=100, description="Signal strength percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('location')
    def validate_location(cls, v):
        required_keys = ['lat', 'lon']
        if not all(key in v for key in required_keys):
            raise ValueError("Location must contain 'lat' and 'lon'")
        return v


class WaterConsumptionModel(BaseModel):
    """Water consumption analysis model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_name: str = Field(..., description="Industrial facility name")
    industry_type: IndustryType = Field(..., description="Type of industry")
    coordinates: Dict[str, float] = Field(..., description="Facility coordinates")
    total_consumption: float = Field(..., ge=0, description="Total water consumption in cubic meters")
    consumption_pattern: ConsumptionPattern = Field(..., description="Consumption pattern")
    efficiency_score: float = Field(..., ge=0, le=100, description="Water efficiency score")
    cost_per_unit: float = Field(..., ge=0, description="Cost per unit of water")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConsumptionAnalysisRequest(BaseModel):
    """Request model for water consumption analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str = Field(..., description="Facility identifier")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period start and end")
    device_ids: List[str] = Field(..., description="IoT device IDs to analyze")
    optimization_goals: List[str] = Field(default_factory=list, description="Optimization goals")
    cost_constraints: Optional[Dict[str, float]] = Field(None, description="Cost constraints")
    efficiency_targets: Optional[Dict[str, float]] = Field(None, description="Efficiency targets")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(..., description="User requesting the analysis")

    @validator('analysis_period')
    def validate_analysis_period(cls, v):
        required_keys = ['start', 'end']
        if not all(key in v for key in required_keys):
            raise ValueError("Analysis period must contain 'start' and 'end'")
        if v['start'] >= v['end']:
            raise ValueError("Start date must be before end date")
        return v


class ConsumptionResult(BaseModel):
    """Water consumption analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    total_consumption: float = Field(..., ge=0, description="Total consumption in cubic meters")
    average_daily_consumption: float = Field(..., ge=0, description="Average daily consumption")
    peak_consumption: float = Field(..., ge=0, description="Peak consumption value")
    consumption_trend: Dict[str, float] = Field(..., description="Consumption trend over time")
    efficiency_metrics: Dict[str, float] = Field(..., description="Efficiency metrics")
    cost_analysis: Dict[str, float] = Field(..., description="Cost analysis")
    optimization_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Optimization opportunities")
    savings_potential: float = Field(..., ge=0, description="Potential savings in currency units")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OptimizationRecommendation(BaseModel):
    """Water optimization recommendation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recommendation_type: str = Field(..., description="Type of optimization")
    description: str = Field(..., description="Recommendation description")
    priority: str = Field(..., description="Priority level")
    estimated_savings: float = Field(..., ge=0, description="Estimated savings")
    implementation_cost: float = Field(..., ge=0, description="Implementation cost")
    payback_period: Optional[float] = Field(None, ge=0, description="Payback period in months")
    efficiency_improvement: float = Field(..., ge=0, le=100, description="Expected efficiency improvement")
    requirements: List[str] = Field(default_factory=list, description="Implementation requirements")
    timeline: str = Field(..., description="Implementation timeline")


class DeviceAlert(BaseModel):
    """IoT device alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = Field(..., description="Device identifier")
    alert_type: str = Field(..., description="Type of alert")
    threshold_value: float = Field(..., description="Threshold value")
    condition: str = Field(..., description="Alert condition (above, below, equals)")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConsumptionReport(BaseModel):
    """Water consumption analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    cost_benefit_analysis: Dict[str, Any] = Field(default_factory=dict, description="Cost-benefit analysis")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class FacilityProfile(BaseModel):
    """Industrial facility profile"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Facility name")
    industry_type: IndustryType = Field(..., description="Industry type")
    location: Dict[str, float] = Field(..., description="Facility location")
    annual_production: Optional[float] = Field(None, ge=0, description="Annual production volume")
    employee_count: Optional[int] = Field(None, ge=0, description="Number of employees")
    water_sources: List[str] = Field(default_factory=list, description="Water sources")
    water_treatment_systems: List[str] = Field(default_factory=list, description="Water treatment systems")
    regulatory_compliance: Dict[str, Any] = Field(default_factory=dict, description="Regulatory compliance status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PerformanceMetric(BaseModel):
    """Water performance metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    facility_id: str = Field(..., description="Facility identifier")
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    benchmark: Optional[float] = Field(None, description="Industry benchmark")
    target: Optional[float] = Field(None, description="Target value")
    measurement_date: datetime = Field(..., description="Measurement date")
    trend: Optional[str] = Field(None, description="Trend direction")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IoTWaterData(Base):
    """IoT Water Consumption Data Model"""
    __tablename__ = "iot_water_data"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    consumption = Column(Float, nullable=False)
    flow_rate = Column(Float, default=0.0)
    pressure = Column(Float, default=0.0)
    temperature = Column(Float, default=0.0)
    quality_metrics = Column(JSON, default={})
    location = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 