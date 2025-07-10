"""
API Data Importer
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import requests
import logging
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
from .base_importer import BaseDataImporter
from common_utils.exceptions import DataImportError
from config.settings import get_settings

logger = logging.getLogger(__name__)

class APIDataImporter(BaseDataImporter):
    """API data importer for external data sources"""
    
    def __init__(self, module_name: str, data_source: str, 
                 api_config: Dict[str, Any],
                 rate_limit: Optional[int] = None):
        super().__init__(module_name, data_source)
        self.api_config = api_config
        self.rate_limit = rate_limit  # requests per minute
        self.last_request_time = 0
        self.session = requests.Session()
        self.settings = get_settings()
        
        # Configure session
        self.session.headers.update({
            'User-Agent': 'AquaTrak-DataImporter/1.0',
            'Accept': 'application/json'
        })
        
        # Add API key if provided
        if 'api_key' in api_config:
            if 'header_name' in api_config:
                self.session.headers[api_config['header_name']] = api_config['api_key']
            else:
                self.session.headers['Authorization'] = f"Bearer {api_config['api_key']}"
    
    def validate_data(self, data: Any) -> bool:
        """Validate API response data"""
        try:
            if isinstance(data, dict):
                # Check for common API response patterns
                if 'error' in data or 'errors' in data:
                    return False
                if 'status' in data and data['status'] == 'error':
                    return False
                return True
            
            elif isinstance(data, list):
                return len(data) > 0
            
            else:
                return False
                
        except Exception as e:
            logger.error(f"API data validation failed: {e}")
            return False
    
    def transform_data(self, data: Any) -> List[Dict[str, Any]]:
        """Transform API response data into standardized format"""
        try:
            if isinstance(data, dict):
                # Handle paginated responses
                if 'data' in data:
                    records = data['data']
                elif 'results' in data:
                    records = data['results']
                elif 'items' in data:
                    records = data['items']
                else:
                    records = [data]
            
            elif isinstance(data, list):
                records = data
            
            else:
                raise DataImportError(f"Unsupported API response format: {type(data)}")
            
            # Transform records
            transformed_records = []
            for record in records:
                try:
                    transformed = self._transform_record(record)
                    if transformed:
                        transformed_records.append(transformed)
                except Exception as e:
                    self.add_error(f"Error transforming record: {e}", record)
            
            return transformed_records
            
        except Exception as e:
            raise DataImportError(f"Failed to transform API data: {e}")
    
    def _transform_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform a single API record"""
        # Apply field mapping if configured
        if 'field_mapping' in self.api_config:
            transformed = {}
            for api_field, target_field in self.api_config['field_mapping'].items():
                if api_field in record:
                    transformed[target_field] = record[api_field]
            return transformed
        
        return record
    
    def import_data(self, **kwargs) -> Dict[str, Any]:
        """Import data from API"""
        self.import_stats['start_time'] = datetime.utcnow()
        
        try:
            # Fetch data from API
            data = self._fetch_api_data(**kwargs)
            
            if not data:
                raise DataImportError("No data received from API")
            
            # Validate data
            if not self.validate_data(data):
                raise DataImportError("API data validation failed")
            
            # Transform data
            records = self.transform_data(data)
            self.import_stats['total_records'] = len(records)
            
            if not records:
                raise DataImportError("No valid records found after transformation")
            
            # Import records
            self._import_records_by_module(records, **kwargs)
            
            self.import_stats['end_time'] = datetime.utcnow()
            self.log_import_stats()
            
            return self.get_import_summary()
            
        except Exception as e:
            self.import_stats['end_time'] = datetime.utcnow()
            logger.error(f"API import failed: {e}")
            raise DataImportError(f"API import failed: {e}")
    
    def _fetch_api_data(self, **kwargs) -> Any:
        """Fetch data from the API"""
        url = self.api_config['url']
        method = self.api_config.get('method', 'GET')
        params = self.api_config.get('params', {})
        headers = self.api_config.get('headers', {})
        
        # Add dynamic parameters
        if 'date_from' in kwargs:
            params['date_from'] = kwargs['date_from']
        if 'date_to' in kwargs:
            params['date_to'] = kwargs['date_to']
        if 'location' in kwargs:
            params['location'] = kwargs['location']
        
        # Apply rate limiting
        if self.rate_limit:
            self._apply_rate_limit()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=params, headers=headers)
            else:
                raise DataImportError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Parse response
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return response.text
                
        except requests.exceptions.RequestException as e:
            raise DataImportError(f"API request failed: {e}")
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        if self.rate_limit:
            min_interval = 60.0 / self.rate_limit  # seconds between requests
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            self.last_request_time = time.time()
    
    def _import_records_by_module(self, records: List[Dict[str, Any]], **kwargs):
        """Import records based on the module type"""
        if self.module_name == "weather_data":
            self._import_weather_data(records, **kwargs)
        elif self.module_name == "satellite_data":
            self._import_satellite_data(records, **kwargs)
        elif self.module_name == "sensor_data":
            self._import_sensor_data(records, **kwargs)
        else:
            # Generic import for other modules
            self._import_generic_data(records, **kwargs)
    
    def _import_weather_data(self, records: List[Dict[str, Any]], **kwargs):
        """Import weather data from external APIs"""
        from models.modules import WeatherData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['timestamp', 'temperature', 'humidity']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Validate coordinates
                if not self.validate_coordinates(record):
                    continue
                
                # Create weather data record
                weather_data = WeatherData(
                    location={
                        'lat': float(record.get('lat', 0)),
                        'lng': float(record.get('lng', 0))
                    },
                    timestamp=record['timestamp'],
                    temperature=float(record['temperature']),
                    humidity=float(record['humidity']),
                    pressure=float(record.get('pressure', 0)),
                    wind_speed=float(record.get('wind_speed', 0)),
                    wind_direction=float(record.get('wind_direction', 0)),
                    precipitation=float(record.get('precipitation', 0)),
                    visibility=float(record.get('visibility', 0)),
                    weather_condition=record.get('weather_condition', ''),
                    created_at=datetime.utcnow()
                )
                
                self.db.add(weather_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing weather record: {e}", record)
        
        self.db.commit()
    
    def _import_satellite_data(self, records: List[Dict[str, Any]], **kwargs):
        """Import satellite data from external APIs"""
        from models.modules import SatelliteData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['timestamp', 'satellite_id', 'data_type']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Create satellite data record
                satellite_data = SatelliteData(
                    satellite_id=record['satellite_id'],
                    data_type=record['data_type'],
                    timestamp=record['timestamp'],
                    location={
                        'lat': float(record.get('lat', 0)),
                        'lng': float(record.get('lng', 0))
                    },
                    data_values=record.get('data_values', {}),
                    quality_metrics={
                        'cloud_cover': float(record.get('cloud_cover', 0)),
                        'resolution': float(record.get('resolution', 0)),
                        'accuracy': float(record.get('accuracy', 0))
                    },
                    metadata={
                        'mission': record.get('mission', ''),
                        'instrument': record.get('instrument', ''),
                        'processing_level': record.get('processing_level', '')
                    },
                    created_at=datetime.utcnow()
                )
                
                self.db.add(satellite_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing satellite record: {e}", record)
        
        self.db.commit()
    
    def _import_sensor_data(self, records: List[Dict[str, Any]], **kwargs):
        """Import sensor data from external APIs"""
        from models.modules import SensorData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['sensor_id', 'timestamp', 'sensor_type']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Create sensor data record
                sensor_data = SensorData(
                    sensor_id=record['sensor_id'],
                    sensor_type=record['sensor_type'],
                    timestamp=record['timestamp'],
                    location={
                        'lat': float(record.get('lat', 0)),
                        'lng': float(record.get('lng', 0))
                    },
                    measurements=record.get('measurements', {}),
                    status=record.get('status', 'active'),
                    battery_level=float(record.get('battery_level', 100)),
                    signal_strength=float(record.get('signal_strength', 0)),
                    created_at=datetime.utcnow()
                )
                
                self.db.add(sensor_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing sensor record: {e}", record)
        
        self.db.commit()
    
    def _import_generic_data(self, records: List[Dict[str, Any]], **kwargs):
        """Generic import for other API data"""
        logger.info(f"Generic API import for {self.module_name}: {len(records)} records")
        
        for record in records:
            try:
                # Store in a generic data table or log
                logger.info(f"API record: {record}")
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing API record: {e}", record)
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close() 