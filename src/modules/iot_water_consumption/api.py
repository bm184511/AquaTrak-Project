"""
IoT Water Consumption API Endpoints
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from config.database import get_db
from models.system import User
from api.auth import get_current_user
from .processor import IoTWaterConsumptionProcessor
from common_utils.exceptions import ProcessingError

router = APIRouter(prefix="/iot", tags=["IoT Water Consumption"])

# Pydantic models
class IoTDataPoint(BaseModel):
    device_id: str
    timestamp: str
    consumption: float
    flow_rate: float
    pressure: float
    temperature: float
    quality_metrics: Dict[str, float]
    location: Dict[str, float]

class AnalysisRequest(BaseModel):
    device_ids: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    analysis_type: str = "comprehensive"
    parameters: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    created_at: str
    completed_at: Optional[str] = None

# API Endpoints
@router.get("/water-consumption")
async def get_iot_data(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get IoT water consumption data"""
    try:
        processor = IoTWaterConsumptionProcessor()
        
        # Parse date filters
        filters = {}
        if device_id:
            filters["device_id"] = device_id
        if start_date:
            filters["start_date"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            filters["end_date"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get data from database
        data = processor.get_data(db, filters=filters, limit=limit)
        
        return {
            "status": "success",
            "data": data,
            "count": len(data),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve IoT data: {str(e)}")

@router.post("/analysis")
async def run_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run IoT water consumption analysis"""
    try:
        processor = IoTWaterConsumptionProcessor()
        
        # Create analysis record
        analysis_id = processor.create_analysis_record(
            db=db,
            user_id=current_user.id,
            parameters=request.dict()
        )
        
        # Run analysis asynchronously
        processor.run_analysis_async(
            analysis_id=analysis_id,
            device_ids=request.device_ids,
            start_date=request.start_date,
            end_date=request.end_date,
            analysis_type=request.analysis_type,
            parameters=request.parameters or {}
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="pending",
            created_at=datetime.utcnow().isoformat()
        )
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analysis results by ID"""
    try:
        processor = IoTWaterConsumptionProcessor()
        results = processor.get_analysis_results(db, analysis_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "status": "success",
            "data": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis results: {str(e)}")

@router.get("/devices")
async def get_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of IoT devices"""
    try:
        processor = IoTWaterConsumptionProcessor()
        devices = processor.get_devices(db)
        
        return {
            "status": "success",
            "data": devices,
            "count": len(devices),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve devices: {str(e)}")

@router.get("/summary")
async def get_summary(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    period: str = Query("24h", description="Time period (24h, 7d, 30d)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get IoT data summary"""
    try:
        processor = IoTWaterConsumptionProcessor()
        
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == "24h":
            start_date = end_date - timedelta(days=1)
        elif period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=1)
        
        filters = {"start_date": start_date, "end_date": end_date}
        if device_id:
            filters["device_id"] = device_id
        
        summary = processor.get_summary(db, filters)
        
        return {
            "status": "success",
            "data": summary,
            "period": period,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summary: {str(e)}")

@router.get("/anomalies")
async def get_anomalies(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, description="Number of anomalies to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detected anomalies"""
    try:
        processor = IoTWaterConsumptionProcessor()
        
        filters = {}
        if device_id:
            filters["device_id"] = device_id
        if severity:
            filters["severity"] = severity
        
        anomalies = processor.get_anomalies(db, filters, limit)
        
        return {
            "status": "success",
            "data": anomalies,
            "count": len(anomalies),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve anomalies: {str(e)}")

@router.get("/efficiency")
async def get_efficiency_metrics(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    period: str = Query("30d", description="Time period (7d, 30d, 90d)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get efficiency metrics"""
    try:
        processor = IoTWaterConsumptionProcessor()
        
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        filters = {"start_date": start_date, "end_date": end_date}
        if device_id:
            filters["device_id"] = device_id
        
        efficiency = processor.get_efficiency_metrics(db, filters)
        
        return {
            "status": "success",
            "data": efficiency,
            "period": period,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve efficiency metrics: {str(e)}")

@router.get("/forecast")
async def get_forecast(
    device_id: str = Query(..., description="Device ID"),
    days: int = Query(7, description="Number of days to forecast"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get consumption forecast"""
    try:
        processor = IoTWaterConsumptionProcessor()
        forecast = processor.get_forecast(db, device_id, days)
        
        return {
            "status": "success",
            "data": forecast,
            "device_id": device_id,
            "forecast_days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}") 