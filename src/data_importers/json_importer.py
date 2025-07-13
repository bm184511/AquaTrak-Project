"""
JSON Data Importer
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

class JSONDataImporter(BaseDataImporter):
    """Imports data from JSON files"""
    
    def __init__(self, module_name: str, data_source: str):
        super().__init__(module_name, data_source)
        self.supported_extensions = ['.json']
    
    def validate_file(self, file_path: str) -> bool:
        """Validate JSON file format"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            if path.suffix.lower() not in self.supported_extensions:
                logger.error(f"Unsupported file extension: {path.suffix}")
                return False
            
            # Try to parse JSON to validate format
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating JSON file {file_path}: {e}")
            return False
    
    def import_data(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Import data from JSON file"""
        try:
            if not self.validate_file(file_path):
                raise DataImportError(f"Invalid JSON file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process the data based on structure
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Handle different JSON structures
                if 'data' in data:
                    records = data['data']
                elif 'records' in data:
                    records = data['records']
                elif 'features' in data:  # GeoJSON-like structure
                    records = data['features']
                else:
                    records = [data]  # Single record
            else:
                raise DataImportError(f"Unsupported JSON structure in {file_path}")
            
            # Transform records if needed
            transformed_records = self._transform_records(records, **kwargs)
            
            # Import to database
            imported_count = self._import_to_database(transformed_records)
            
            return {
                'module_name': self.module_name,
                'data_source': self.data_source,
                'total_records': len(records),
                'imported_records': imported_count,
                'failed_records': len(records) - imported_count,
                'success_rate': (imported_count / len(records)) * 100 if records else 0,
                'duration': '00:00:01',  # Mock duration
                'error_count': len(records) - imported_count
            }
            
        except Exception as e:
            logger.error(f"JSON import failed for {file_path}: {e}")
            raise DataImportError(f"JSON import failed: {e}")
    
    def _transform_records(self, records: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Transform JSON records to database format"""
        transformed = []
        
        for record in records:
            try:
                # Apply field mapping if provided
                if hasattr(self, 'field_mapping') and self.field_mapping:
                    transformed_record = {}
                    for source_field, target_field in self.field_mapping.items():
                        if source_field in record:
                            transformed_record[target_field] = record[source_field]
                else:
                    transformed_record = record.copy()
                
                # Add metadata
                transformed_record['import_timestamp'] = self.start_time.isoformat()
                transformed_record['data_source'] = self.data_source
                
                transformed.append(transformed_record)
                
            except Exception as e:
                logger.warning(f"Failed to transform record: {e}")
                continue
        
        return transformed
    
    def _import_to_database(self, records: List[Dict[str, Any]]) -> int:
        """Import records to database"""
        # This would integrate with the actual database models
        # For now, just return the count of records that would be imported
        logger.info(f"Would import {len(records)} records to {self.module_name}")
        return len(records) 