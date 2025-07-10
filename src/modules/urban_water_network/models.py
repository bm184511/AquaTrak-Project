"""
Urban Water Network Models
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


class NetworkComponent(str, Enum):
    """Types of water network components"""
    PUMP_STATION = "pump_station"
    RESERVOIR = "reservoir"
    TREATMENT_PLANT = "treatment_plant"
    DISTRIBUTION_MAIN = "distribution_main"
    SERVICE_LINE = "service_line"
    VALVE = "valve"
    HYDRANT = "hydrant"
    METER = "meter"
    MANHOLE = "manhole"
    STORAGE_TANK = "storage_tank"


class ComponentStatus(str, Enum):
    """Component operational status"""
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    OFFLINE = "offline"
    EMERGENCY = "emergency"


class WaterQualityParameter(str, Enum):
    """Water quality parameters"""
    PH = "ph"
    TURBIDITY = "turbidity"
    CHLORINE = "chlorine"
    CONDUCTIVITY = "conductivity"
    TEMPERATURE = "temperature"
    DISSOLVED_OXYGEN = "dissolved_oxygen"
    TOTAL_DISSOLVED_SOLIDS = "total_dissolved_solids"
    BACTERIA = "bacteria"


class PressureZone(str, Enum):
    """Water pressure zones"""
    HIGH_PRESSURE = "high_pressure"
    MEDIUM_PRESSURE = "medium_pressure"
    LOW_PRESSURE = "low_pressure"
    VARIABLE_PRESSURE = "variable_pressure"


class NetworkAnalysisRequest(BaseModel):
    """Request model for water network analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    network_name: str = Field(..., description="Water network name")
    analysis_type: str = Field(..., description="Type of network analysis")
    components: List[str] = Field(..., description="Network components to analyze")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    monitoring_data: Dict[str, Any] = Field(..., description="Monitoring data")
    network_topology: Optional[Dict[str, Any]] = Field(None, description="Network topology data")
    hydraulic_model: Optional[Dict[str, Any]] = Field(None, description="Hydraulic model parameters")
    quality_parameters: List[WaterQualityParameter] = Field(default_factory=list, description="Quality parameters")
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


class NetworkModel(BaseModel):
    """Water network model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Network model name")
    model_type: str = Field(..., description="Type of network model")
    components: List[Dict[str, Any]] = Field(..., description="Network components")
    topology: Dict[str, Any] = Field(..., description="Network topology")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NetworkComponentData(BaseModel):
    """Individual network component data"""
    component_id: str = Field(..., description="Component identifier")
    component_type: NetworkComponent = Field(..., description="Component type")
    location: Dict[str, float] = Field(..., description="Component location")
    status: ComponentStatus = Field(..., description="Component status")
    measurements: Dict[str, float] = Field(..., description="Component measurements")
    timestamp: datetime = Field(..., description="Data timestamp")
    alerts: List[str] = Field(default_factory=list, description="Active alerts")
    maintenance_schedule: Optional[Dict[str, Any]] = Field(None, description="Maintenance schedule")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('location')
    def validate_location(cls, v):
        required_keys = ['lat', 'lon']
        if not all(key in v for key in required_keys):
            raise ValueError("Location must contain 'lat' and 'lon'")
        return v


class WaterQualityData(BaseModel):
    """Water quality monitoring data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    location_id: str = Field(..., description="Monitoring location")
    parameter: WaterQualityParameter = Field(..., description="Quality parameter")
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Measurement unit")
    timestamp: datetime = Field(..., description="Measurement timestamp")
    quality_flag: Optional[str] = Field(None, description="Data quality flag")
    regulatory_limit: Optional[float] = Field(None, description="Regulatory limit")
    compliance_status: Optional[str] = Field(None, description="Compliance status")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NetworkResult(BaseModel):
    """Water network analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    network_status: Dict[str, ComponentStatus] = Field(..., description="Network component status")
    performance_metrics: Dict[str, float] = Field(..., description="Network performance metrics")
    quality_assessment: Dict[str, Dict[str, Any]] = Field(..., description="Water quality assessment")
    pressure_analysis: Dict[str, float] = Field(..., description="Pressure analysis results")
    flow_analysis: Dict[str, float] = Field(..., description="Flow analysis results")
    efficiency_score: float = Field(..., ge=0, le=100, description="Network efficiency score")
    reliability_score: float = Field(..., ge=0, le=100, description="Network reliability score")
    maintenance_needs: List[Dict[str, Any]] = Field(default_factory=list, description="Maintenance requirements")
    optimization_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Optimization opportunities")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NetworkAlert(BaseModel):
    """Water network alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    network_name: str = Field(..., description="Network name")
    alert_type: str = Field(..., description="Type of alert")
    component_id: Optional[str] = Field(None, description="Component identifier")
    parameter: Optional[str] = Field(None, description="Monitored parameter")
    threshold_value: float = Field(..., description="Threshold value")
    condition: str = Field(..., description="Alert condition")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NetworkReport(BaseModel):
    """Water network analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    compliance_assessment: Dict[str, Any] = Field(default_factory=dict, description="Regulatory compliance")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class MaintenanceSchedule(BaseModel):
    """Maintenance schedule for network components"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component_id: str = Field(..., description="Component identifier")
    maintenance_type: str = Field(..., description="Type of maintenance")
    scheduled_date: datetime = Field(..., description="Scheduled maintenance date")
    estimated_duration: int = Field(..., ge=1, description="Estimated duration in hours")
    priority: str = Field(..., description="Maintenance priority")
    description: str = Field(..., description="Maintenance description")
    required_parts: List[str] = Field(default_factory=list, description="Required parts")
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated cost")
    assigned_technician: Optional[str] = Field(None, description="Assigned technician")
    status: str = Field(default="scheduled", description="Maintenance status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NetworkEfficiency(BaseModel):
    """Network efficiency metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    network_id: str = Field(..., description="Network identifier")
    metric_name: str = Field(..., description="Efficiency metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    benchmark: Optional[float] = Field(None, description="Industry benchmark")
    target: Optional[float] = Field(None, description="Target value")
    measurement_date: datetime = Field(..., description="Measurement date")
    trend: Optional[str] = Field(None, description="Trend direction")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LeakDetection(BaseModel):
    """Water leak detection result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    network_id: str = Field(..., description="Network identifier")
    leak_location: Dict[str, float] = Field(..., description="Estimated leak location")
    confidence_level: float = Field(..., ge=0, le=100, description="Detection confidence level")
    estimated_flow_rate: float = Field(..., ge=0, description="Estimated leak flow rate")
    severity: str = Field(..., description="Leak severity")
    detection_method: str = Field(..., description="Detection method used")
    detection_date: datetime = Field(..., description="Detection date")
    status: str = Field(default="detected", description="Leak status")
    repair_priority: str = Field(..., description="Repair priority")
    estimated_repair_cost: Optional[float] = Field(None, ge=0, description="Estimated repair cost")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WaterNetworkData(Base):
    """Urban Water Network Data Model"""
    __tablename__ = "water_network_data"
    
    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(String(100), nullable=False, index=True)
    location = Column(JSON, default={})
    timestamp = Column(DateTime, nullable=False, index=True)
    pressure = Column(Float, nullable=False)
    flow_rate = Column(Float, nullable=False)
    water_quality = Column(JSON, default={})
    infrastructure_status = Column(JSON, default={})
    performance_metrics = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 