"""
Dust Storm Analysis Models
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


class StormIntensity(str, Enum):
    """Dust storm intensity levels"""
    LIGHT = "light"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class StormType(str, Enum):
    """Types of dust storms"""
    HABOOB = "haboob"
    DUST_DEVIL = "dust_devil"
    SANDSTORM = "sandstorm"
    DUST_PLUME = "dust_plume"
    ASH_STORM = "ash_storm"


class ImpactCategory(str, Enum):
    """Categories of dust storm impact"""
    AIR_QUALITY = "air_quality"
    WATER_QUALITY = "water_quality"
    AGRICULTURE = "agriculture"
    INFRASTRUCTURE = "infrastructure"
    HEALTH = "health"
    TRANSPORTATION = "transportation"


class DustStormAnalysisRequest(BaseModel):
    """Request model for dust storm analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_name: str = Field(..., description="Region name for analysis")
    coordinates: Dict[str, float] = Field(..., description="Region coordinates")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    storm_characteristics: Dict[str, Any] = Field(..., description="Storm characteristics")
    meteorological_data: Optional[Dict[str, Any]] = Field(None, description="Meteorological data")
    satellite_data: Optional[Dict[str, Any]] = Field(None, description="Satellite imagery data")
    ground_station_data: Optional[Dict[str, Any]] = Field(None, description="Ground station measurements")
    water_bodies: List[str] = Field(default_factory=list, description="Affected water bodies")
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


class DustStormModel(BaseModel):
    """Dust storm analysis model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of dust storm model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StormEvent(BaseModel):
    """Individual dust storm event"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_name: str = Field(..., description="Event name")
    storm_type: StormType = Field(..., description="Type of dust storm")
    intensity: StormIntensity = Field(..., description="Storm intensity")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    duration_hours: float = Field(..., ge=0, description="Duration in hours")
    affected_area: float = Field(..., ge=0, description="Affected area in square kilometers")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    visibility: float = Field(..., ge=0, description="Visibility in meters")
    dust_concentration: float = Field(..., ge=0, description="Dust concentration in μg/m³")
    source_location: Dict[str, float] = Field(..., description="Source location coordinates")
    trajectory: List[Dict[str, float]] = Field(default_factory=list, description="Storm trajectory")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('source_location')
    def validate_source_location(cls, v):
        required_keys = ['lat', 'lon']
        if not all(key in v for key in required_keys):
            raise ValueError("Source location must contain 'lat' and 'lon'")
        return v


class WaterQualityImpact(BaseModel):
    """Water quality impact from dust storm"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    water_body_id: str = Field(..., description="Water body identifier")
    storm_event_id: str = Field(..., description="Related storm event")
    impact_date: datetime = Field(..., description="Impact date")
    turbidity_increase: float = Field(..., ge=0, description="Turbidity increase in NTU")
    sediment_load: float = Field(..., ge=0, description="Sediment load in mg/L")
    ph_change: float = Field(..., description="pH change")
    dissolved_oxygen_change: float = Field(..., description="Dissolved oxygen change in mg/L")
    nutrient_enrichment: Dict[str, float] = Field(default_factory=dict, description="Nutrient enrichment")
    contamination_risk: str = Field(..., description="Contamination risk level")
    recovery_time_days: Optional[int] = Field(None, ge=0, description="Estimated recovery time")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EnvironmentalImpact(BaseModel):
    """Environmental impact assessment"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    impact_category: ImpactCategory = Field(..., description="Impact category")
    severity: str = Field(..., description="Impact severity")
    description: str = Field(..., description="Impact description")
    affected_area: float = Field(..., ge=0, description="Affected area")
    economic_loss: Optional[float] = Field(None, ge=0, description="Economic loss estimate")
    duration_days: int = Field(..., ge=0, description="Impact duration in days")
    mitigation_measures: List[str] = Field(default_factory=list, description="Mitigation measures")
    assessment_date: datetime = Field(..., description="Assessment date")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DustStormResult(BaseModel):
    """Dust storm analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    storm_events: List[StormEvent] = Field(..., description="Identified storm events")
    water_quality_impacts: List[WaterQualityImpact] = Field(default_factory=list, description="Water quality impacts")
    environmental_impacts: List[EnvironmentalImpact] = Field(default_factory=list, description="Environmental impacts")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    prediction_model: Dict[str, Any] = Field(..., description="Prediction model results")
    mitigation_recommendations: List[str] = Field(default_factory=list, description="Mitigation recommendations")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DustStormAlert(BaseModel):
    """Dust storm alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_name: str = Field(..., description="Region name")
    alert_type: str = Field(..., description="Type of alert")
    intensity_threshold: StormIntensity = Field(..., description="Intensity threshold for alert")
    visibility_threshold: float = Field(..., ge=0, description="Visibility threshold in meters")
    dust_concentration_threshold: float = Field(..., ge=0, description="Dust concentration threshold")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DustStormReport(BaseModel):
    """Dust storm analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    seasonal_analysis: Dict[str, Any] = Field(default_factory=dict, description="Seasonal analysis")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class MeteorologicalData(BaseModel):
    """Meteorological data for dust storm analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    station_id: str = Field(..., description="Weather station identifier")
    timestamp: datetime = Field(..., description="Data timestamp")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction in degrees")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    pressure: float = Field(..., ge=0, description="Atmospheric pressure in hPa")
    visibility: float = Field(..., ge=0, description="Visibility in meters")
    dust_concentration: Optional[float] = Field(None, ge=0, description="Dust concentration in μg/m³")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PredictionModel(BaseModel):
    """Dust storm prediction model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = Field(..., description="Model name")
    prediction_type: str = Field(..., description="Type of prediction")
    forecast_period: int = Field(..., ge=1, description="Forecast period in hours")
    confidence_level: float = Field(..., ge=0, le=100, description="Confidence level percentage")
    accuracy_score: float = Field(..., ge=0, le=1, description="Model accuracy score")
    input_parameters: List[str] = Field(default_factory=list, description="Input parameters")
    output_variables: List[str] = Field(default_factory=list, description="Output variables")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 