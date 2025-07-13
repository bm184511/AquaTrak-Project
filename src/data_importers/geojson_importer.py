"""
GeoJSON Data Importer
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base_importer import BaseDataImporter
from common_utils.exceptions import DataImportError

logger = logging.getLogger(__name__)

class GeoJSONDataImporter(BaseDataImporter):
    """Imports data from GeoJSON files"""
    
    def __init__(self, module_name: str, data_source: str):
        super().__init__(module_name, data_source)
        self.supported_extensions = ['.geojson', '.json']
    
    def validate_file(self, file_path: str) -> bool:
        """Validate GeoJSON file format"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            if path.suffix.lower() not in self.supported_extensions:
                logger.error(f"Unsupported file extension: {path.suffix}")
                return False
            
            # Try to parse GeoJSON to validate format
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate GeoJSON structure
            if not isinstance(data, dict):
                logger.error(f"Invalid GeoJSON structure: root must be an object")
                return False
            
            if 'type' not in data:
                logger.error(f"Missing 'type' field in GeoJSON")
                return False
            
            if data['type'] == 'FeatureCollection':
                if 'features' not in data:
                    logger.error(f"FeatureCollection missing 'features' array")
                    return False
            elif data['type'] == 'Feature':
                if 'geometry' not in data:
                    logger.error(f"Feature missing 'geometry' object")
                    return False
            else:
                logger.warning(f"Unsupported GeoJSON type: {data['type']}")
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating GeoJSON file {file_path}: {e}")
            return False
    
    def import_data(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Import data from GeoJSON file"""
        try:
            if not self.validate_file(file_path):
                raise DataImportError(f"Invalid GeoJSON file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract features based on GeoJSON type
            if data['type'] == 'FeatureCollection':
                features = data['features']
            elif data['type'] == 'Feature':
                features = [data]
            else:
                features = []
            
            # Transform features
            transformed_records = self._transform_features(features, **kwargs)
            
            # Import to database
            imported_count = self._import_to_database(transformed_records)
            
            return {
                'module_name': self.module_name,
                'data_source': self.data_source,
                'total_records': len(features),
                'imported_records': imported_count,
                'failed_records': len(features) - imported_count,
                'success_rate': (imported_count / len(features)) * 100 if features else 0,
                'duration': '00:00:01',  # Mock duration
                'error_count': len(features) - imported_count
            }
            
        except Exception as e:
            logger.error(f"GeoJSON import failed for {file_path}: {e}")
            raise DataImportError(f"GeoJSON import failed: {e}")
    
    def _transform_features(self, features: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Transform GeoJSON features to database format"""
        transformed = []
        
        for feature in features:
            try:
                if feature['type'] != 'Feature':
                    logger.warning(f"Skipping non-Feature object: {feature['type']}")
                    continue
                
                # Extract geometry and properties
                geometry = feature.get('geometry', {})
                properties = feature.get('properties', {})
                
                # Create transformed record
                transformed_record = {
                    'geometry': geometry,
                    'properties': properties,
                    'import_timestamp': self.start_time.isoformat(),
                    'data_source': self.data_source
                }
                
                # Apply field mapping if provided
                if hasattr(self, 'field_mapping') and self.field_mapping:
                    for source_field, target_field in self.field_mapping.items():
                        if source_field in properties:
                            transformed_record[target_field] = properties[source_field]
                
                transformed.append(transformed_record)
                
            except Exception as e:
                logger.warning(f"Failed to transform feature: {e}")
                continue
        
        return transformed
    
    def _import_to_database(self, records: List[Dict[str, Any]]) -> int:
        """Import records to database"""
        # This would integrate with the actual database models
        # For now, just return the count of records that would be imported
        logger.info(f"Would import {len(records)} GeoJSON features to {self.module_name}")
        return len(records) 