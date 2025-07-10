# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
API routes for InSAR Land Subsidence Monitoring Module
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
import tempfile
import os

from .models import (
    SubsidenceData, SubsidenceResult, SubsidenceReport, 
    SubsidenceAlert, SatelliteType
)
from .processor import InSARSubsidenceProcessor
from ...security.auth import get_current_user
from ...common_utils.file_utils import save_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/insar", tags=["InSAR Subsidence Monitoring"])

# Initialize processor
processor = InSARSubsidenceProcessor()

@router.post("/analyze", response_model=SubsidenceResult)
async def analyze_subsidence(
    satellite_type: SatelliteType = Form(...),
    date1: str = Form(...),
    date2: str = Form(...),
    coherence_threshold: float = Form(0.3),
    deformation_threshold: float = Form(0.01),
    min_lat: float = Form(...),
    max_lat: float = Form(...),
    min_lon: float = Form(...),
    max_lon: float = Form(...),
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    dem_file: Optional[UploadFile] = File(None),
    mask_file: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_user)
):
    """
    Analyze land subsidence using InSAR satellite imagery
    
    This endpoint processes two satellite images to detect and measure land subsidence.
    """
    try:
        # Save uploaded files
        image1_path = await save_uploaded_file(image1, "insar")
        image2_path = await save_uploaded_file(image2, "insar")
        
        dem_path = None
        if dem_file:
            dem_path = await save_uploaded_file(dem_file, "insar")
        
        mask_path = None
        if mask_file:
            mask_path = await save_uploaded_file(mask_file, "insar")
        
        # Create input data
        from datetime import datetime
        data = SubsidenceData(
            satellite_type=satellite_type,
            image1_path=image1_path,
            image2_path=image2_path,
            date1=datetime.fromisoformat(date1),
            date2=datetime.fromisoformat(date2),
            bounds={
                'min_lat': min_lat,
                'max_lat': max_lat,
                'min_lon': min_lon,
                'max_lon': max_lon
            },
            coherence_threshold=coherence_threshold,
            deformation_threshold=deformation_threshold,
            dem_path=dem_path,
            mask_path=mask_path
        )
        
        # Process data
        result = processor.process(data)
        
        logger.info(f"InSAR analysis completed: {result.analysis_id}")
        return result
        
    except Exception as e:
        logger.error(f"InSAR analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{analysis_id}", response_model=SubsidenceResult)
async def get_analysis_result(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    """Get analysis result by ID"""
    # In practice, this would load from database
    raise HTTPException(status_code=404, detail="Analysis result not found")

@router.get("/results/{analysis_id}/report", response_model=SubsidenceReport)
async def generate_report(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    """Generate comprehensive report for analysis"""
    # In practice, this would load result from database and generate report
    raise HTTPException(status_code=404, detail="Analysis result not found")

@router.get("/results/{analysis_id}/alerts", response_model=List[SubsidenceAlert])
async def get_alerts(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    """Get alerts for analysis"""
    # In practice, this would load from database
    raise HTTPException(status_code=404, detail="Analysis result not found")

@router.get("/results/{analysis_id}/download/{file_type}")
async def download_result_file(
    analysis_id: str,
    file_type: str,
    current_user = Depends(get_current_user)
):
    """Download result files (GeoTIFF, GeoJSON, etc.)"""
    # In practice, this would serve files from storage
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/statistics")
async def get_statistics(current_user = Depends(get_current_user)):
    """Get overall statistics for InSAR analyses"""
    # In practice, this would aggregate from database
    return {
        "total_analyses": 0,
        "total_area_covered": 0.0,
        "critical_areas": 0,
        "high_risk_areas": 0
    }

@router.get("/satellites")
async def get_supported_satellites():
    """Get list of supported satellite types"""
    return [
        {"id": sat.value, "name": sat.value.replace("-", " ").title()}
        for sat in SatelliteType
    ] 