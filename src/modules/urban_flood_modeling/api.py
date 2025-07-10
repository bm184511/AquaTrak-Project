"""
Urban Flood Modeling API
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .models import (
    FloodAnalysisRequest, FloodResult, FloodAlert, FloodReport,
    FloodModel, FloodModelType, RainfallIntensity, FloodSeverity
)
from .processor import UrbanFloodProcessor
from ..security.auth import get_current_user, require_role
from ..common_utils.exceptions import ProcessingError, ValidationError
from ..common_utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/flood-modeling", tags=["Urban Flood Modeling"])

# Initialize processor
processor = UrbanFloodProcessor()


@router.post("/analyze", response_model=FloodResult)
async def analyze_flood(
    request: FloodAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Perform comprehensive flood analysis
    
    Analyzes urban flood risk using hydrological and hydraulic modeling.
    Supports multiple model types and provides detailed risk assessment.
    """
    try:
        # Set user ID from authenticated user
        request.user_id = current_user["user_id"]
        
        # Process analysis
        result = processor.process_flood_analysis(request)
        
        logger.info(f"Flood analysis completed for user {current_user['user_id']}")
        
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error in flood analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ProcessingError as e:
        logger.error(f"Processing error in flood analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in flood analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/results/{analysis_id}", response_model=FloodResult)
async def get_analysis_result(
    analysis_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get flood analysis result by ID"""
    try:
        result = processor.get_analysis_result(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis result not found")
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving flood analysis result: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/models", response_model=Dict[str, str])
async def create_model(
    model: FloodModel,
    current_user: Dict = Depends(require_role(["admin", "analyst"]))
):
    """Create a new flood model"""
    try:
        model_config = {
            "name": model.name,
            "model_type": model.model_type,
            "parameters": model.parameters,
            "calibration_data": model.calibration_data,
            "validation_metrics": model.validation_metrics,
            "created_by": current_user["user_id"]
        }
        
        model_id = processor.create_flood_model(model_config)
        
        logger.info(f"Flood model created by user {current_user['user_id']}")
        
        return {"model_id": model_id, "message": "Model created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating flood model: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models", response_model=List[Dict[str, Any]])
async def list_models(
    model_type: Optional[FloodModelType] = None,
    current_user: Dict = Depends(get_current_user)
):
    """List available flood models"""
    try:
        models = []
        for model_id, model_config in processor.models.items():
            if model_type is None or model_config.get("model_type") == model_type:
                models.append({
                    "id": model_id,
                    "name": model_config.get("name"),
                    "model_type": model_config.get("model_type"),
                    "created_by": model_config.get("created_by")
                })
        
        return models
        
    except Exception as e:
        logger.error(f"Error listing flood models: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/alerts", response_model=Dict[str, str])
async def create_alert(
    alert: FloodAlert,
    current_user: Dict = Depends(require_role(["admin", "analyst"]))
):
    """Create a new flood alert"""
    try:
        alert_id = processor.create_alert(alert)
        
        logger.info(f"Flood alert created by user {current_user['user_id']}")
        
        return {"alert_id": alert_id, "message": "Alert created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating flood alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/alerts", response_model=List[FloodAlert])
async def list_alerts(
    area_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: Dict = Depends(get_current_user)
):
    """List flood alerts"""
    try:
        alerts = []
        for alert in processor.alerts.values():
            if area_name and alert.area_name != area_name:
                continue
            if is_active is not None and alert.is_active != is_active:
                continue
            alerts.append(alert)
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error listing flood alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/alerts/{alert_id}")
async def update_alert(
    alert_id: str,
    alert_update: Dict[str, Any],
    current_user: Dict = Depends(require_role(["admin", "analyst"]))
):
    """Update flood alert"""
    try:
        if alert_id not in processor.alerts:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert = processor.alerts[alert_id]
        
        # Update allowed fields
        allowed_fields = ["threshold_depth", "threshold_severity", "notification_channels", "recipients", "is_active"]
        for field, value in alert_update.items():
            if field in allowed_fields:
                setattr(alert, field, value)
        
        alert.updated_at = datetime.utcnow()
        
        logger.info(f"Flood alert updated by user {current_user['user_id']}")
        
        return {"message": "Alert updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating flood alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: Dict = Depends(require_role(["admin"]))
):
    """Delete flood alert"""
    try:
        if alert_id not in processor.alerts:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        del processor.alerts[alert_id]
        
        logger.info(f"Flood alert deleted by user {current_user['user_id']}")
        
        return {"message": "Alert deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting flood alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/reports/{analysis_id}", response_model=FloodReport)
async def generate_report(
    analysis_id: str,
    report_type: str = "comprehensive",
    current_user: Dict = Depends(get_current_user)
):
    """Generate flood analysis report"""
    try:
        report = processor.generate_report(analysis_id, report_type)
        
        logger.info(f"Flood report generated by user {current_user['user_id']}")
        
        return report
        
    except ProcessingError as e:
        logger.warning(f"Error generating flood report: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating flood report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(
    current_user: Dict = Depends(get_current_user)
):
    """Get flood modeling statistics"""
    try:
        total_analyses = len(processor.results_cache)
        total_models = len(processor.models)
        total_alerts = len(processor.alerts)
        
        # Calculate severity distribution
        severity_counts = {}
        for result in processor.results_cache.values():
            severity = result.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate average risk score
        avg_risk_score = 0
        if processor.results_cache:
            avg_risk_score = sum(r.risk_score for r in processor.results_cache.values()) / len(processor.results_cache)
        
        statistics = {
            "total_analyses": total_analyses,
            "total_models": total_models,
            "total_alerts": total_alerts,
            "severity_distribution": severity_counts,
            "average_risk_score": round(avg_risk_score, 2),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error getting flood statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/model-types", response_model=List[Dict[str, str]])
async def get_model_types():
    """Get available flood model types"""
    return [
        {"value": model_type.value, "name": model_type.value.replace("_", " ").title()}
        for model_type in FloodModelType
    ]


@router.get("/rainfall-intensities", response_model=List[Dict[str, str]])
async def get_rainfall_intensities():
    """Get available rainfall intensity categories"""
    return [
        {"value": intensity.value, "name": intensity.value.title()}
        for intensity in RainfallIntensity
    ]


@router.get("/severity-levels", response_model=List[Dict[str, str]])
async def get_severity_levels():
    """Get available flood severity levels"""
    return [
        {"value": severity.value, "name": severity.value.title()}
        for severity in FloodSeverity
    ] 