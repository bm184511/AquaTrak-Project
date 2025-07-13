"""
Base Data Importer
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from config.database import get_db
from common_utils.exceptions import DataImportError

logger = logging.getLogger(__name__)

class BaseDataImporter(ABC):
    """Base class for all data importers"""
    
    def __init__(self, module_name: str, data_source: str):
        self.module_name = module_name
        self.data_source = data_source
        self.db: Optional[Session] = None
        self.start_time = datetime.utcnow()  # Initialize start_time
        self.import_stats = {
            'total_records': 0,
            'imported_records': 0,
            'failed_records': 0,
            'errors': [],
            'start_time': None,
            'end_time': None
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.db = next(get_db())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.db:
            self.db.close()
    
    @abstractmethod
    def validate_data(self, data: Any) -> bool:
        """Validate the data format and structure"""
        pass
    
    @abstractmethod
    def transform_data(self, data: Any) -> List[Dict[str, Any]]:
        """Transform raw data into the required format"""
        pass
    
    @abstractmethod
    def import_data(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Import data into the database"""
        pass
    
    def log_import_stats(self):
        """Log import statistics"""
        duration = None
        if self.import_stats['start_time'] and self.import_stats['end_time']:
            duration = self.import_stats['end_time'] - self.import_stats['start_time']
        
        logger.info(f"Import completed for {self.module_name} from {self.data_source}")
        logger.info(f"Total records: {self.import_stats['total_records']}")
        logger.info(f"Imported records: {self.import_stats['imported_records']}")
        logger.info(f"Failed records: {self.import_stats['failed_records']}")
        logger.info(f"Duration: {duration}")
        
        if self.import_stats['errors']:
            logger.error(f"Import errors: {len(self.import_stats['errors'])}")
            for error in self.import_stats['errors'][:5]:  # Log first 5 errors
                logger.error(f"  - {error}")
    
    def add_error(self, error: str, record: Optional[Dict] = None):
        """Add an error to the import statistics"""
        error_info = {
            'error': error,
            'record': record,
            'timestamp': datetime.utcnow()
        }
        self.import_stats['errors'].append(error_info)
        self.import_stats['failed_records'] += 1
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that required fields are present in the data"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            self.add_error(f"Missing required fields: {missing_fields}", data)
            return False
        return True
    
    def validate_data_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> bool:
        """Validate data types for specified fields"""
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    self.add_error(f"Invalid type for field '{field}': expected {expected_type}, got {type(data[field])}", data)
                    return False
        return True
    
    def validate_date_range(self, data: Dict[str, Any], date_field: str, 
                          min_date: Optional[datetime] = None, 
                          max_date: Optional[datetime] = None) -> bool:
        """Validate date range for a field"""
        if date_field in data and data[date_field]:
            try:
                if isinstance(data[date_field], str):
                    date_value = datetime.fromisoformat(data[date_field].replace('Z', '+00:00'))
                else:
                    date_value = data[date_field]
                
                if min_date and date_value < min_date:
                    self.add_error(f"Date {date_field} is before minimum date {min_date}", data)
                    return False
                
                if max_date and date_value > max_date:
                    self.add_error(f"Date {date_field} is after maximum date {max_date}", data)
                    return False
                    
            except (ValueError, TypeError) as e:
                self.add_error(f"Invalid date format for {date_field}: {e}", data)
                return False
        
        return True
    
    def validate_coordinates(self, data: Dict[str, Any], lat_field: str = 'lat', 
                           lng_field: str = 'lng') -> bool:
        """Validate geographic coordinates"""
        if lat_field in data and lng_field in data:
            try:
                lat = float(data[lat_field])
                lng = float(data[lng_field])
                
                if not (-90 <= lat <= 90):
                    self.add_error(f"Invalid latitude: {lat} (must be between -90 and 90)", data)
                    return False
                
                if not (-180 <= lng <= 180):
                    self.add_error(f"Invalid longitude: {lng} (must be between -180 and 180)", data)
                    return False
                    
            except (ValueError, TypeError) as e:
                self.add_error(f"Invalid coordinate format: {e}", data)
                return False
        
        return True
    
    def clean_string_field(self, value: Any, max_length: Optional[int] = None) -> Optional[str]:
        """Clean and validate a string field"""
        if value is None:
            return None
        
        cleaned = str(value).strip()
        if not cleaned:
            return None
        
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        
        return cleaned
    
    def clean_numeric_field(self, value: Any, min_value: Optional[float] = None, 
                           max_value: Optional[float] = None) -> Optional[float]:
        """Clean and validate a numeric field"""
        if value is None:
            return None
        
        try:
            numeric_value = float(value)
            
            if min_value is not None and numeric_value < min_value:
                return None
            
            if max_value is not None and numeric_value > max_value:
                return None
            
            return numeric_value
            
        except (ValueError, TypeError):
            return None
    
    def get_import_summary(self) -> Dict[str, Any]:
        """Get a summary of the import operation"""
        duration = None
        if self.import_stats['start_time'] and self.import_stats['end_time']:
            duration = self.import_stats['end_time'] - self.import_stats['start_time']
        
        success_rate = 0
        if self.import_stats['total_records'] > 0:
            success_rate = (self.import_stats['imported_records'] / self.import_stats['total_records']) * 100
        
        return {
            'module_name': self.module_name,
            'data_source': self.data_source,
            'total_records': self.import_stats['total_records'],
            'imported_records': self.import_stats['imported_records'],
            'failed_records': self.import_stats['failed_records'],
            'success_rate': round(success_rate, 2),
            'duration': str(duration) if duration else None,
            'error_count': len(self.import_stats['errors']),
            'start_time': self.import_stats['start_time'].isoformat() if self.import_stats['start_time'] else None,
            'end_time': self.import_stats['end_time'].isoformat() if self.import_stats['end_time'] else None
        } 