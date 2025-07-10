"""
Satellite Data Importer
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import logging
import rasterio
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
import json
from .base_importer import BaseDataImporter
from common_utils.exceptions import DataImportError

logger = logging.getLogger(__name__)

class SatelliteDataImporter(BaseDataImporter):
    """Satellite data importer for remote sensing data"""
    
    def __init__(self, module_name: str, data_source: str,
                 satellite_type: str = "sentinel",
                 processing_level: str = "L2A"):
        super().__init__(module_name, data_source)
        self.satellite_type = satellite_type
        self.processing_level = processing_level
    
    def validate_data(self, data: Union[str, Path, Dict]) -> bool:
        """Validate satellite data format"""
        try:
            if isinstance(data, (str, Path)):
                file_path = Path(data)
                if not file_path.exists():
                    raise DataImportError(f"Satellite data file not found: {file_path}")
                
                # Check file extension
                if file_path.suffix.lower() not in ['.tif', '.tiff', '.jp2', '.hdf', '.nc']:
                    raise DataImportError(f"Unsupported satellite data format: {file_path.suffix}")
                
                # Try to open with rasterio to validate
                with rasterio.open(file_path) as src:
                    if src.count == 0:
                        raise DataImportError("Satellite data file has no bands")
            
            elif isinstance(data, dict):
                # Validate metadata structure
                required_fields = ['timestamp', 'satellite_id', 'data_type']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise DataImportError(f"Missing required fields in satellite metadata: {missing_fields}")
            
            else:
                raise DataImportError(f"Unsupported satellite data type: {type(data)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Satellite data validation failed: {e}")
            return False
    
    def transform_data(self, data: Union[str, Path, Dict]) -> List[Dict[str, Any]]:
        """Transform satellite data into standardized format"""
        try:
            if isinstance(data, (str, Path)):
                return self._transform_raster_data(data)
            elif isinstance(data, dict):
                return self._transform_metadata(data)
            else:
                raise DataImportError(f"Unsupported data type for transformation: {type(data)}")
                
        except Exception as e:
            raise DataImportError(f"Failed to transform satellite data: {e}")
    
    def _transform_raster_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Transform raster satellite data"""
        records = []
        
        try:
            with rasterio.open(file_path) as src:
                # Read metadata
                metadata = {
                    'timestamp': src.tags().get('timestamp', datetime.utcnow().isoformat()),
                    'satellite_id': src.tags().get('satellite_id', 'unknown'),
                    'data_type': src.tags().get('data_type', 'optical'),
                    'processing_level': src.tags().get('processing_level', self.processing_level),
                    'cloud_cover': float(src.tags().get('cloud_cover', 0)),
                    'resolution': float(src.tags().get('resolution', 10)),
                    'crs': str(src.crs),
                    'bounds': src.bounds,
                    'width': src.width,
                    'height': src.height,
                    'count': src.count
                }
                
                # Read bands and calculate indices
                bands = src.read()
                
                # Calculate common indices
                if src.count >= 4:  # Multispectral data
                    indices = self._calculate_indices(bands, src.tags())
                else:
                    indices = {}
                
                # Create record
                record = {
                    **metadata,
                    'indices': indices,
                    'file_path': str(file_path),
                    'created_at': datetime.utcnow().isoformat()
                }
                
                records.append(record)
                
        except Exception as e:
            raise DataImportError(f"Error processing raster data: {e}")
        
        return records
    
    def _transform_metadata(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform satellite metadata"""
        # Validate and clean metadata
        required_fields = ['timestamp', 'satellite_id', 'data_type']
        if not self.validate_required_fields(metadata, required_fields):
            return []
        
        # Add default values for missing fields
        record = {
            'timestamp': metadata['timestamp'],
            'satellite_id': metadata['satellite_id'],
            'data_type': metadata['data_type'],
            'processing_level': metadata.get('processing_level', self.processing_level),
            'cloud_cover': float(metadata.get('cloud_cover', 0)),
            'resolution': float(metadata.get('resolution', 10)),
            'location': metadata.get('location', {}),
            'indices': metadata.get('indices', {}),
            'created_at': datetime.utcnow().isoformat()
        }
        
        return [record]
    
    def _calculate_indices(self, bands: np.ndarray, tags: Dict[str, str]) -> Dict[str, float]:
        """Calculate common satellite indices"""
        indices = {}
        
        try:
            # NDVI (Normalized Difference Vegetation Index)
            if bands.shape[0] >= 4:
                red = bands[2].astype(float)  # Red band (usually band 3)
                nir = bands[3].astype(float)  # NIR band (usually band 4)
                
                # Avoid division by zero
                denominator = nir + red
                denominator[denominator == 0] = 1
                
                ndvi = (nir - red) / denominator
                indices['ndvi'] = float(np.nanmean(ndvi))
            
            # NDWI (Normalized Difference Water Index)
            if bands.shape[0] >= 4:
                green = bands[1].astype(float)  # Green band (usually band 2)
                nir = bands[3].astype(float)  # NIR band (usually band 4)
                
                denominator = green + nir
                denominator[denominator == 0] = 1
                
                ndwi = (green - nir) / denominator
                indices['ndwi'] = float(np.nanmean(ndwi))
            
            # EVI (Enhanced Vegetation Index)
            if bands.shape[0] >= 4:
                blue = bands[0].astype(float)  # Blue band (usually band 1)
                red = bands[2].astype(float)  # Red band (usually band 3)
                nir = bands[3].astype(float)  # NIR band (usually band 4)
                
                denominator = nir + 6 * red - 7.5 * blue
                denominator[denominator == 0] = 1
                
                evi = 2.5 * (nir - red) / denominator
                indices['evi'] = float(np.nanmean(evi))
            
            # SAVI (Soil Adjusted Vegetation Index)
            if bands.shape[0] >= 4:
                red = bands[2].astype(float)
                nir = bands[3].astype(float)
                L = 0.5  # Soil brightness correction factor
                
                denominator = nir + red + L
                denominator[denominator == 0] = 1
                
                savi = (1 + L) * (nir - red) / denominator
                indices['savi'] = float(np.nanmean(savi))
            
            # MNDWI (Modified Normalized Difference Water Index)
            if bands.shape[0] >= 5:
                green = bands[1].astype(float)
                swir = bands[4].astype(float)  # SWIR band (usually band 5)
                
                denominator = green + swir
                denominator[denominator == 0] = 1
                
                mndwi = (green - swir) / denominator
                indices['mndwi'] = float(np.nanmean(mndwi))
                
        except Exception as e:
            logger.warning(f"Error calculating indices: {e}")
        
        return indices
    
    def import_data(self, data: Union[str, Path, Dict], **kwargs) -> Dict[str, Any]:
        """Import satellite data into the database"""
        self.import_stats['start_time'] = datetime.utcnow()
        
        try:
            # Validate data
            if not self.validate_data(data):
                raise DataImportError("Satellite data validation failed")
            
            # Transform data
            records = self.transform_data(data)
            self.import_stats['total_records'] = len(records)
            
            if not records:
                raise DataImportError("No valid records found after transformation")
            
            # Import records
            self._import_satellite_records(records, **kwargs)
            
            self.import_stats['end_time'] = datetime.utcnow()
            self.log_import_stats()
            
            return self.get_import_summary()
            
        except Exception as e:
            self.import_stats['end_time'] = datetime.utcnow()
            logger.error(f"Satellite import failed: {e}")
            raise DataImportError(f"Satellite import failed: {e}")
    
    def _import_satellite_records(self, records: List[Dict[str, Any]], **kwargs):
        """Import satellite records into the database"""
        from models.modules import SatelliteData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['timestamp', 'satellite_id', 'data_type']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Validate coordinates if present
                if 'location' in record and record['location']:
                    if not self.validate_coordinates(record['location']):
                        continue
                
                # Create satellite data record
                satellite_data = SatelliteData(
                    satellite_id=record['satellite_id'],
                    data_type=record['data_type'],
                    timestamp=record['timestamp'],
                    location=record.get('location', {}),
                    data_values={
                        'indices': record.get('indices', {}),
                        'cloud_cover': record.get('cloud_cover', 0),
                        'resolution': record.get('resolution', 10)
                    },
                    quality_metrics={
                        'cloud_cover': float(record.get('cloud_cover', 0)),
                        'resolution': float(record.get('resolution', 10)),
                        'accuracy': float(record.get('accuracy', 0))
                    },
                    metadata={
                        'mission': record.get('mission', ''),
                        'instrument': record.get('instrument', ''),
                        'processing_level': record.get('processing_level', self.processing_level),
                        'file_path': record.get('file_path', ''),
                        'crs': record.get('crs', ''),
                        'bounds': record.get('bounds', {}),
                        'width': record.get('width', 0),
                        'height': record.get('height', 0),
                        'count': record.get('count', 0)
                    },
                    created_at=datetime.utcnow()
                )
                
                self.db.add(satellite_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing satellite record: {e}", record)
        
        self.db.commit()
    
    def process_sentinel_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """Process Sentinel satellite data specifically"""
        try:
            # Set Sentinel-specific parameters
            self.satellite_type = "sentinel"
            self.processing_level = kwargs.get('processing_level', 'L2A')
            
            # Process the data
            return self.import_data(file_path, **kwargs)
            
        except Exception as e:
            raise DataImportError(f"Sentinel data processing failed: {e}")
    
    def process_landsat_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """Process Landsat satellite data specifically"""
        try:
            # Set Landsat-specific parameters
            self.satellite_type = "landsat"
            self.processing_level = kwargs.get('processing_level', 'L2')
            
            # Process the data
            return self.import_data(file_path, **kwargs)
            
        except Exception as e:
            raise DataImportError(f"Landsat data processing failed: {e}")
    
    def process_modis_data(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """Process MODIS satellite data specifically"""
        try:
            # Set MODIS-specific parameters
            self.satellite_type = "modis"
            self.processing_level = kwargs.get('processing_level', 'L3')
            
            # Process the data
            return self.import_data(file_path, **kwargs)
            
        except Exception as e:
            raise DataImportError(f"MODIS data processing failed: {e}") 