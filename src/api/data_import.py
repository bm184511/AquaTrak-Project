"""
Data Import API
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import json
from pathlib import Path
import tempfile
import shutil

from data_importers.manager import DataImportManager
from data_importers.base_importer import BaseDataImporter
from common_utils.exceptions import DataImportError
from security.auth import get_current_user
from models.system import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data-import", tags=["Data Import"])

# Initialize import manager
import_manager = DataImportManager()

class ImportTaskRequest(BaseModel):
    """Request model for import tasks"""
    type: str = Field(..., description="Import type (csv, api, satellite, json, geojson, sensor, weather, gis)")
    module_name: str = Field(..., description="Target module name")
    data_source: str = Field(..., description="Data source (file path, API URL, etc.)")
    options: Dict[str, Any] = Field(default_factory=dict, description="Import options")
    field_mapping: Optional[Dict[str, str]] = Field(None, description="Field mapping for CSV imports")
    api_config: Optional[Dict[str, Any]] = Field(None, description="API configuration for API imports")

class BatchImportRequest(BaseModel):
    """Request model for batch imports"""
    tasks: List[ImportTaskRequest] = Field(..., description="List of import tasks")
    parallel: bool = Field(True, description="Execute imports in parallel")

class ImportResult(BaseModel):
    """Import result model"""
    module_name: str
    data_source: str
    total_records: int
    imported_records: int
    failed_records: int
    success_rate: float
    duration: Optional[str]
    error_count: int
    start_time: Optional[str]
    end_time: Optional[str]

class BatchImportResult(BaseModel):
    """Batch import result model"""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    results: List[Dict[str, Any]]
    start_time: str
    end_time: Optional[str]

@router.post("/single", response_model=ImportResult)
async def import_single_data(
    task: ImportTaskRequest,
    current_user: User = Depends(get_current_user)
):
    """Import data from a single source"""
    try:
        logger.info(f"Single import requested by user {current_user.id}: {task.module_name}")
        
        # Validate import configuration
        if not import_manager.validate_import_config(task.dict()):
            raise HTTPException(status_code=400, detail="Invalid import configuration")
        
        # Execute import based on type
        if task.type == 'csv':
            result = import_manager.import_csv_data(
                task.module_name,
                task.data_source,
                field_mapping=task.field_mapping,
                **task.options
            )
        elif task.type == 'api':
            if not task.api_config:
                raise HTTPException(status_code=400, detail="API configuration required for API imports")
            result = import_manager.import_api_data(
                task.module_name,
                task.api_config,
                **task.options
            )
        elif task.type == 'satellite':
            result = import_manager.import_satellite_data(
                task.module_name,
                task.data_source,
                **task.options
            )
        elif task.type == 'json':
            result = import_manager.import_json_data(
                task.module_name,
                task.data_source,
                **task.options
            )
        elif task.type == 'geojson':
            result = import_manager.import_geojson_data(
                task.module_name,
                task.data_source,
                **task.options
            )
        elif task.type == 'sensor':
            result = import_manager.import_sensor_data(
                task.module_name,
                task.data_source,
                **task.options
            )
        elif task.type == 'weather':
            result = import_manager.import_weather_data(
                task.module_name,
                task.data_source,
                **task.options
            )
        elif task.type == 'gis':
            result = import_manager.import_gis_data(
                task.module_name,
                task.data_source,
                **task.options
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported import type: {task.type}")
        
        return ImportResult(**result)
        
    except DataImportError as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch", response_model=BatchImportResult)
async def import_batch_data(
    request: BatchImportRequest,
    current_user: User = Depends(get_current_user)
):
    """Import data from multiple sources in batch"""
    try:
        logger.info(f"Batch import requested by user {current_user.id}: {len(request.tasks)} tasks")
        
        # Validate all import configurations
        for task in request.tasks:
            if not import_manager.validate_import_config(task.dict()):
                raise HTTPException(status_code=400, detail=f"Invalid import configuration for {task.module_name}")
        
        # Convert to task format expected by manager
        import_tasks = []
        for task in request.tasks:
            task_dict = task.dict()
            if task.type == 'api' and task.api_config:
                task_dict['api_config'] = task.api_config
            import_tasks.append(task_dict)
        
        # Execute batch import
        results = import_manager.batch_import(import_tasks)
        
        return BatchImportResult(**results)
        
    except DataImportError as e:
        logger.error(f"Batch import failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during batch import: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload-csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    module_name: str = Form(...),
    field_mapping: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Upload and import CSV file"""
    try:
        logger.info(f"CSV upload requested by user {current_user.id}: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Parse field mapping if provided
        mapping = None
        if field_mapping:
            try:
                mapping = json.loads(field_mapping)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid field mapping JSON")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Import the CSV file
            result = import_manager.import_csv_data(
                module_name,
                temp_path,
                field_mapping=mapping
            )
            
            return ImportResult(**result)
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
        
    except DataImportError as e:
        logger.error(f"CSV import failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during CSV upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload-json")
async def upload_json_file(
    file: UploadFile = File(...),
    module_name: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and import JSON file"""
    try:
        logger.info(f"JSON upload requested by user {current_user.id}: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Import the JSON file
            result = import_manager.import_json_data(module_name, temp_path)
            
            return ImportResult(**result)
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
        
    except DataImportError as e:
        logger.error(f"JSON import failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during JSON upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload-geojson")
async def upload_geojson_file(
    file: UploadFile = File(...),
    module_name: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and import GeoJSON file"""
    try:
        logger.info(f"GeoJSON upload requested by user {current_user.id}: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.geojson'):
            raise HTTPException(status_code=400, detail="Only GeoJSON files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Import the GeoJSON file
            result = import_manager.import_geojson_data(module_name, temp_path)
            
            return ImportResult(**result)
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
        
    except DataImportError as e:
        logger.error(f"GeoJSON import failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during GeoJSON upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history")
async def get_import_history(
    module_name: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get import history"""
    try:
        history = import_manager.get_import_history(module_name, limit)
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Error retrieving import history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats")
async def get_import_stats(
    current_user: User = Depends(get_current_user)
):
    """Get import statistics"""
    try:
        stats = import_manager.get_import_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving import stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sample-data")
async def create_sample_data(
    module_name: str,
    num_records: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Create sample data for testing"""
    try:
        logger.info(f"Sample data creation requested by user {current_user.id}: {module_name}")
        
        result = import_manager.create_sample_data(module_name, num_records)
        
        return ImportResult(**result)
        
    except DataImportError as e:
        logger.error(f"Sample data creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during sample data creation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported import formats"""
    return {
        "formats": [
            {
                "type": "csv",
                "description": "Comma-separated values file",
                "extensions": [".csv"],
                "modules": ["iot_water_consumption", "environmental_health", "urban_green_space", "urban_water_network"]
            },
            {
                "type": "json",
                "description": "JavaScript Object Notation file",
                "extensions": [".json"],
                "modules": ["all"]
            },
            {
                "type": "geojson",
                "description": "Geographic JSON file",
                "extensions": [".geojson"],
                "modules": ["environmental_health", "urban_green_space", "urban_water_network"]
            },
            {
                "type": "api",
                "description": "External API endpoint",
                "extensions": [],
                "modules": ["weather_data", "satellite_data", "sensor_data"]
            },
            {
                "type": "satellite",
                "description": "Satellite imagery data",
                "extensions": [".tif", ".tiff", ".jp2", ".hdf", ".nc"],
                "modules": ["satellite_data"]
            }
        ]
    }

@router.get("/modules")
async def get_supported_modules():
    """Get list of supported modules"""
    return {
        "modules": [
            {
                "name": "iot_water_consumption",
                "description": "IoT Water Consumption Monitoring",
                "supported_formats": ["csv", "json", "api"]
            },
            {
                "name": "environmental_health",
                "description": "Environmental Health Assessment",
                "supported_formats": ["csv", "json", "geojson", "api"]
            },
            {
                "name": "urban_green_space",
                "description": "Urban Green Space Analysis",
                "supported_formats": ["csv", "json", "geojson", "satellite"]
            },
            {
                "name": "urban_water_network",
                "description": "Urban Water Network Monitoring",
                "supported_formats": ["csv", "json", "geojson", "api"]
            },
            {
                "name": "agricultural_reservoir",
                "description": "Agricultural Reservoir Management",
                "supported_formats": ["csv", "json", "satellite"]
            },
            {
                "name": "data_center_water",
                "description": "Data Center Water Usage",
                "supported_formats": ["csv", "json", "api"]
            },
            {
                "name": "drinking_water_quality",
                "description": "Drinking Water Quality Monitoring",
                "supported_formats": ["csv", "json", "api"]
            },
            {
                "name": "drought_prediction",
                "description": "Drought Prediction Models",
                "supported_formats": ["csv", "json", "satellite", "api"]
            },
            {
                "name": "dust_storm_analysis",
                "description": "Dust Storm Analysis",
                "supported_formats": ["csv", "json", "satellite"]
            },
            {
                "name": "groundwater_pollution",
                "description": "Groundwater Pollution Monitoring",
                "supported_formats": ["csv", "json", "geojson"]
            },
            {
                "name": "insar_subsidence",
                "description": "InSAR Subsidence Analysis",
                "supported_formats": ["csv", "json", "satellite"]
            },
            {
                "name": "transboundary_water",
                "description": "Transboundary Water Management",
                "supported_formats": ["csv", "json", "geojson", "api"]
            },
            {
                "name": "urban_flood_modeling",
                "description": "Urban Flood Modeling",
                "supported_formats": ["csv", "json", "geojson", "satellite"]
            }
        ]
    } 