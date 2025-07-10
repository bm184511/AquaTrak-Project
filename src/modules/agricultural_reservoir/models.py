"""
Smart Agricultural Reservoir Management Models
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


class ReservoirType(str, Enum):
    """Types of agricultural reservoirs"""
    SURFACE_RESERVOIR = "surface_reservoir"
    UNDERGROUND_RESERVOIR = "underground_reservoir"
    FARM_POND = "farm_pond"
    CHECK_DAM = "check_dam"
    PERCOLATION_TANK = "percolation_tank"


class IrrigationMethod(str, Enum):
    """Types of irrigation methods"""
    DRIP_IRRIGATION = "drip_irrigation"
    SPRINKLER_IRRIGATION = "sprinkler_irrigation"
    FLOOD_IRRIGATION = "flood_irrigation"
    FURROW_IRRIGATION = "furrow_irrigation"
    CENTER_PIVOT = "center_pivot"
    MICRO_IRRIGATION = "micro_irrigation"


class CropType(str, Enum):
    """Types of agricultural crops"""
    CEREALS = "cereals"
    PULSES = "pulses"
    OILSEEDS = "oilseeds"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    CASH_CROPS = "cash_crops"
    FODDER = "fodder"


class ReservoirStatus(str, Enum):
    """Reservoir operational status"""
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    LOW_LEVEL = "low_level"
    OVERFLOW = "overflow"
    CONTAMINATED = "contaminated"


class ReservoirAnalysisRequest(BaseModel):
    """Request model for agricultural reservoir analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservoir_name: str = Field(..., description="Reservoir name")
    coordinates: Dict[str, float] = Field(..., description="Reservoir coordinates")
    reservoir_type: ReservoirType = Field(..., description="Type of reservoir")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    crop_data: List[Dict[str, Any]] = Field(..., description="Crop information")
    irrigation_data: Dict[str, Any] = Field(..., description="Irrigation system data")
    weather_data: Optional[Dict[str, Any]] = Field(None, description="Weather data")
    soil_data: Optional[Dict[str, Any]] = Field(None, description="Soil characteristics")
    water_quality_data: Optional[Dict[str, Any]] = Field(None, description="Water quality data")
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


class ReservoirModel(BaseModel):
    """Agricultural reservoir model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of reservoir model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReservoirData(BaseModel):
    """Reservoir operational data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservoir_id: str = Field(..., description="Reservoir identifier")
    timestamp: datetime = Field(..., description="Data timestamp")
    water_level: float = Field(..., ge=0, description="Water level in meters")
    storage_capacity: float = Field(..., ge=0, description="Storage capacity in cubic meters")
    current_storage: float = Field(..., ge=0, description="Current storage in cubic meters")
    inflow_rate: float = Field(..., description="Inflow rate in cubic meters per hour")
    outflow_rate: float = Field(..., ge=0, description="Outflow rate in cubic meters per hour")
    evaporation_rate: float = Field(..., ge=0, description="Evaporation rate in cubic meters per day")
    seepage_rate: float = Field(..., ge=0, description="Seepage rate in cubic meters per day")
    water_temperature: Optional[float] = Field(None, description="Water temperature in Celsius")
    ph_level: Optional[float] = Field(None, ge=0, le=14, description="pH level")
    turbidity: Optional[float] = Field(None, ge=0, description="Turbidity in NTU")
    status: ReservoirStatus = Field(..., description="Reservoir status")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CropData(BaseModel):
    """Crop information and water requirements"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    crop_name: str = Field(..., description="Crop name")
    crop_type: CropType = Field(..., description="Crop type")
    area_hectares: float = Field(..., ge=0, description="Crop area in hectares")
    planting_date: datetime = Field(..., description="Planting date")
    harvesting_date: Optional[datetime] = Field(None, description="Expected harvesting date")
    growth_stage: str = Field(..., description="Current growth stage")
    water_requirement: float = Field(..., ge=0, description="Daily water requirement in mm")
    irrigation_efficiency: float = Field(..., ge=0, le=100, description="Irrigation efficiency percentage")
    stress_tolerance: str = Field(..., description="Drought stress tolerance")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IrrigationSchedule(BaseModel):
    """Irrigation scheduling data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservoir_id: str = Field(..., description="Reservoir identifier")
    crop_id: str = Field(..., description="Crop identifier")
    irrigation_method: IrrigationMethod = Field(..., description="Irrigation method")
    scheduled_date: datetime = Field(..., description="Scheduled irrigation date")
    duration_hours: float = Field(..., ge=0, description="Irrigation duration in hours")
    water_volume: float = Field(..., ge=0, description="Water volume in cubic meters")
    application_rate: float = Field(..., ge=0, description="Application rate in mm/hour")
    priority: str = Field(..., description="Irrigation priority")
    status: str = Field(default="scheduled", description="Irrigation status")
    actual_volume: Optional[float] = Field(None, ge=0, description="Actual water applied")
    efficiency: Optional[float] = Field(None, ge=0, le=100, description="Actual efficiency")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WaterBalance(BaseModel):
    """Water balance analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservoir_id: str = Field(..., description="Reservoir identifier")
    analysis_date: datetime = Field(..., description="Analysis date")
    total_inflow: float = Field(..., ge=0, description="Total inflow in cubic meters")
    total_outflow: float = Field(..., ge=0, description="Total outflow in cubic meters")
    evaporation_loss: float = Field(..., ge=0, description="Evaporation loss")
    seepage_loss: float = Field(..., ge=0, description="Seepage loss")
    irrigation_demand: float = Field(..., ge=0, description="Irrigation water demand")
    available_storage: float = Field(..., ge=0, description="Available storage")
    storage_efficiency: float = Field(..., ge=0, le=100, description="Storage efficiency percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReservoirResult(BaseModel):
    """Agricultural reservoir analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    reservoir_summary: Dict[str, Any] = Field(..., description="Reservoir summary")
    water_balance: WaterBalance = Field(..., description="Water balance analysis")
    crop_water_requirements: Dict[str, float] = Field(..., description="Crop water requirements")
    irrigation_schedule: List[IrrigationSchedule] = Field(default_factory=list, description="Optimized irrigation schedule")
    efficiency_analysis: Dict[str, float] = Field(..., description="Efficiency analysis")
    optimization_recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Optimization recommendations")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    sustainability_score: float = Field(..., ge=0, le=100, description="Sustainability score")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReservoirAlert(BaseModel):
    """Reservoir alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservoir_name: str = Field(..., description="Reservoir name")
    alert_type: str = Field(..., description="Type of alert")
    water_level_threshold: float = Field(..., ge=0, description="Water level threshold")
    storage_threshold: float = Field(..., ge=0, le=100, description="Storage threshold percentage")
    quality_threshold: Optional[float] = Field(None, description="Water quality threshold")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReservoirReport(BaseModel):
    """Agricultural reservoir analysis report"""
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
    """Reservoir optimization strategy"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservoir_id: str = Field(..., description="Reservoir identifier")
    strategy_name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    water_savings: float = Field(..., ge=0, description="Expected water savings")
    efficiency_improvement: float = Field(..., ge=0, le=100, description="Expected efficiency improvement")
    implementation_cost: float = Field(..., ge=0, description="Implementation cost")
    payback_period: Optional[float] = Field(None, ge=0, description="Payback period in months")
    requirements: List[str] = Field(default_factory=list, description="Implementation requirements")
    timeline: str = Field(..., description="Implementation timeline")
    priority: str = Field(..., description="Implementation priority")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WeatherImpact(BaseModel):
    """Weather impact on reservoir management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reservoir_id: str = Field(..., description="Reservoir identifier")
    analysis_date: datetime = Field(..., description="Analysis date")
    rainfall_impact: float = Field(..., description="Rainfall impact on storage")
    temperature_impact: float = Field(..., description="Temperature impact on evaporation")
    humidity_impact: float = Field(..., description="Humidity impact on crop water needs")
    wind_impact: float = Field(..., description="Wind impact on evaporation")
    seasonal_adjustment: Dict[str, float] = Field(default_factory=dict, description="Seasonal adjustments")
    created_at: datetime = Field(default_factory=datetime.utcnow) 