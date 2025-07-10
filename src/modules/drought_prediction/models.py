"""
Drought Prediction Models
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid


class DroughtIndex(str, Enum):
    """Types of drought indices"""
    SPI = "spi"  # Standardized Precipitation Index
    SPEI = "spei"  # Standardized Precipitation Evapotranspiration Index
    PDSI = "pdsi"  # Palmer Drought Severity Index
    NDVI = "ndvi"  # Normalized Difference Vegetation Index
    VCI = "vci"  # Vegetation Condition Index
    TCI = "tci"  # Temperature Condition Index
    VHI = "vhi"  # Vegetation Health Index


class DroughtSeverity(str, Enum):
    """Drought severity levels"""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    EXCEPTIONAL = "exceptional"


class ClimateVariable(str, Enum):
    """Climate variables for drought analysis"""
    PRECIPITATION = "precipitation"
    TEMPERATURE = "temperature"
    EVAPOTRANSPIRATION = "evapotranspiration"
    SOIL_MOISTURE = "soil_moisture"
    STREAMFLOW = "streamflow"
    GROUNDWATER = "groundwater"
    VEGETATION = "vegetation"


class PredictionTimeframe(str, Enum):
    """Drought prediction timeframes"""
    SHORT_TERM = "short_term"  # 1-3 months
    MEDIUM_TERM = "medium_term"  # 3-6 months
    LONG_TERM = "long_term"  # 6-12 months
    SEASONAL = "seasonal"  # Seasonal forecasts


class DroughtAnalysisRequest(BaseModel):
    """Request model for drought analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_name: str = Field(..., description="Region name for analysis")
    coordinates: Dict[str, float] = Field(..., description="Region coordinates")
    analysis_period: Dict[str, datetime] = Field(..., description="Analysis period")
    prediction_timeframe: PredictionTimeframe = Field(..., description="Prediction timeframe")
    drought_indices: List[DroughtIndex] = Field(..., description="Drought indices to calculate")
    climate_variables: List[ClimateVariable] = Field(..., description="Climate variables to include")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical climate data")
    land_use_data: Optional[Dict[str, Any]] = Field(None, description="Land use information")
    soil_data: Optional[Dict[str, Any]] = Field(None, description="Soil characteristics")
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


class DroughtModel(BaseModel):
    """Drought prediction model configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of drought model")
    algorithm: str = Field(..., description="Prediction algorithm")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    training_data_period: Dict[str, datetime] = Field(..., description="Training data period")
    validation_metrics: Optional[Dict[str, float]] = Field(None, description="Validation metrics")
    accuracy_score: Optional[float] = Field(None, ge=0, le=1, description="Model accuracy score")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DroughtIndexValue(BaseModel):
    """Individual drought index value"""
    index_type: DroughtIndex = Field(..., description="Type of drought index")
    value: float = Field(..., description="Index value")
    severity: DroughtSeverity = Field(..., description="Drought severity")
    percentile: float = Field(..., ge=0, le=100, description="Percentile rank")
    date: datetime = Field(..., description="Date of calculation")
    confidence_interval: Optional[Dict[str, float]] = Field(None, description="Confidence interval")


class DroughtPrediction(BaseModel):
    """Drought prediction result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_name: str = Field(..., description="Region name")
    prediction_date: datetime = Field(..., description="Date of prediction")
    forecast_period: Dict[str, datetime] = Field(..., description="Forecast period")
    predicted_severity: DroughtSeverity = Field(..., description="Predicted drought severity")
    confidence_level: float = Field(..., ge=0, le=100, description="Prediction confidence level")
    index_predictions: Dict[str, List[DroughtIndexValue]] = Field(..., description="Index predictions")
    probability_distribution: Dict[str, float] = Field(..., description="Severity probability distribution")
    uncertainty_metrics: Dict[str, float] = Field(..., description="Uncertainty metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DroughtResult(BaseModel):
    """Drought analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis request")
    current_drought_status: DroughtSeverity = Field(..., description="Current drought status")
    drought_indices: Dict[str, List[DroughtIndexValue]] = Field(..., description="Calculated drought indices")
    historical_trend: Dict[str, List[float]] = Field(..., description="Historical drought trend")
    predictions: List[DroughtPrediction] = Field(default_factory=list, description="Drought predictions")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    impact_analysis: Dict[str, Any] = Field(..., description="Impact analysis")
    adaptation_recommendations: List[str] = Field(default_factory=list, description="Adaptation recommendations")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DroughtAlert(BaseModel):
    """Drought alert configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_name: str = Field(..., description="Region name")
    alert_type: str = Field(..., description="Type of drought alert")
    severity_threshold: DroughtSeverity = Field(..., description="Severity threshold for alert")
    index_threshold: float = Field(..., description="Index threshold value")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    recipients: List[str] = Field(default_factory=list, description="Alert recipients")
    is_active: bool = Field(default=True, description="Whether alert is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DroughtReport(BaseModel):
    """Drought analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = Field(..., description="ID of the analysis")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Charts and visualizations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    seasonal_analysis: Dict[str, Any] = Field(default_factory=dict, description="Seasonal analysis")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = Field(None, description="Path to generated report file")


class ClimateData(BaseModel):
    """Climate data model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_name: str = Field(..., description="Region name")
    variable: ClimateVariable = Field(..., description="Climate variable")
    value: float = Field(..., description="Data value")
    unit: str = Field(..., description="Measurement unit")
    date: datetime = Field(..., description="Date of measurement")
    source: str = Field(..., description="Data source")
    quality_flag: Optional[str] = Field(None, description="Data quality flag")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DroughtImpact(BaseModel):
    """Drought impact assessment"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    region_name: str = Field(..., description="Region name")
    impact_category: str = Field(..., description="Impact category")
    severity: DroughtSeverity = Field(..., description="Impact severity")
    description: str = Field(..., description="Impact description")
    economic_loss: Optional[float] = Field(None, ge=0, description="Economic loss estimate")
    affected_population: Optional[int] = Field(None, ge=0, description="Affected population")
    affected_area: Optional[float] = Field(None, ge=0, description="Affected area in square km")
    assessment_date: datetime = Field(..., description="Assessment date")
    created_at: datetime = Field(default_factory=datetime.utcnow) 