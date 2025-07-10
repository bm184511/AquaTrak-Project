"""
CSV Data Importer
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import csv
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import pandas as pd
from .base_importer import BaseDataImporter
from common_utils.exceptions import DataImportError

logger = logging.getLogger(__name__)

class CSVDataImporter(BaseDataImporter):
    """CSV data importer for various data formats"""
    
    def __init__(self, module_name: str, data_source: str, 
                 field_mapping: Optional[Dict[str, str]] = None,
                 date_format: str = "%Y-%m-%d %H:%M:%S",
                 encoding: str = "utf-8",
                 delimiter: str = ","):
        super().__init__(module_name, data_source)
        self.field_mapping = field_mapping or {}
        self.date_format = date_format
        self.encoding = encoding
        self.delimiter = delimiter
    
    def validate_data(self, data: Union[str, Path, pd.DataFrame]) -> bool:
        """Validate CSV data format"""
        try:
            if isinstance(data, (str, Path)):
                # Check if file exists and is readable
                file_path = Path(data)
                if not file_path.exists():
                    raise DataImportError(f"CSV file not found: {file_path}")
                
                # Try to read first few lines to validate format
                with open(file_path, 'r', encoding=self.encoding) as f:
                    reader = csv.reader(f, delimiter=self.delimiter)
                    header = next(reader, None)
                    if not header:
                        raise DataImportError("CSV file is empty or has no header")
                    
                    # Check if we have at least one data row
                    first_row = next(reader, None)
                    if not first_row:
                        raise DataImportError("CSV file has no data rows")
            
            elif isinstance(data, pd.DataFrame):
                if data.empty:
                    raise DataImportError("DataFrame is empty")
                if len(data.columns) == 0:
                    raise DataImportError("DataFrame has no columns")
            
            else:
                raise DataImportError(f"Unsupported data type: {type(data)}")
            
            return True
            
        except Exception as e:
            logger.error(f"CSV validation failed: {e}")
            return False
    
    def transform_data(self, data: Union[str, Path, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Transform CSV data into standardized format"""
        try:
            # Load CSV data
            if isinstance(data, (str, Path)):
                df = pd.read_csv(data, encoding=self.encoding, delimiter=self.delimiter)
            else:
                df = data.copy()
            
            # Apply field mapping if provided
            if self.field_mapping:
                df = df.rename(columns=self.field_mapping)
            
            # Convert to list of dictionaries
            records = df.to_dict('records')
            
            # Clean and validate each record
            cleaned_records = []
            for i, record in enumerate(records):
                try:
                    cleaned_record = self._clean_record(record)
                    if cleaned_record:
                        cleaned_records.append(cleaned_record)
                    else:
                        self.add_error(f"Record {i+1} was cleaned to empty", record)
                except Exception as e:
                    self.add_error(f"Error cleaning record {i+1}: {e}", record)
            
            return cleaned_records
            
        except Exception as e:
            raise DataImportError(f"Failed to transform CSV data: {e}")
    
    def _clean_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and validate a single record"""
        cleaned = {}
        
        for key, value in record.items():
            if pd.isna(value) or value == '':
                continue
            
            # Clean string fields
            if isinstance(value, str):
                cleaned_value = self.clean_string_field(value)
                if cleaned_value:
                    cleaned[key] = cleaned_value
            
            # Clean numeric fields
            elif isinstance(value, (int, float)):
                cleaned_value = self.clean_numeric_field(value)
                if cleaned_value is not None:
                    cleaned[key] = cleaned_value
            
            # Handle datetime fields
            elif isinstance(value, datetime):
                cleaned[key] = value.isoformat()
            
            # Handle pandas datetime
            elif pd.api.types.is_datetime64_any_dtype(value):
                cleaned[key] = pd.to_datetime(value).isoformat()
            
            else:
                cleaned[key] = str(value).strip()
        
        return cleaned if cleaned else None
    
    def import_data(self, data: Union[str, Path, pd.DataFrame], **kwargs) -> Dict[str, Any]:
        """Import CSV data into the database"""
        self.import_stats['start_time'] = datetime.utcnow()
        
        try:
            # Validate data
            if not self.validate_data(data):
                raise DataImportError("CSV data validation failed")
            
            # Transform data
            records = self.transform_data(data)
            self.import_stats['total_records'] = len(records)
            
            if not records:
                raise DataImportError("No valid records found after transformation")
            
            # Import records based on module type
            self._import_records_by_module(records, **kwargs)
            
            self.import_stats['end_time'] = datetime.utcnow()
            self.log_import_stats()
            
            return self.get_import_summary()
            
        except Exception as e:
            self.import_stats['end_time'] = datetime.utcnow()
            logger.error(f"CSV import failed: {e}")
            raise DataImportError(f"CSV import failed: {e}")
    
    def _import_records_by_module(self, records: List[Dict[str, Any]], **kwargs):
        """Import records based on the module type"""
        if self.module_name == "iot_water_consumption":
            self._import_iot_data(records, **kwargs)
        elif self.module_name == "environmental_health":
            self._import_environmental_health_data(records, **kwargs)
        elif self.module_name == "urban_green_space":
            self._import_green_space_data(records, **kwargs)
        elif self.module_name == "urban_water_network":
            self._import_water_network_data(records, **kwargs)
        else:
            # Generic import for other modules
            self._import_generic_data(records, **kwargs)
    
    def _import_iot_data(self, records: List[Dict[str, Any]], **kwargs):
        """Import IoT water consumption data"""
        from models.modules import IoTWaterData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['device_id', 'timestamp', 'consumption']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Validate coordinates if present
                if 'lat' in record and 'lng' in record:
                    if not self.validate_coordinates(record):
                        continue
                
                # Create IoT data record
                iot_data = IoTWaterData(
                    device_id=record['device_id'],
                    timestamp=record['timestamp'],
                    consumption=float(record['consumption']),
                    flow_rate=float(record.get('flow_rate', 0)),
                    pressure=float(record.get('pressure', 0)),
                    temperature=float(record.get('temperature', 0)),
                    quality_metrics={
                        'ph': float(record.get('ph', 7.0)),
                        'turbidity': float(record.get('turbidity', 0)),
                        'conductivity': float(record.get('conductivity', 0)),
                        'dissolved_oxygen': float(record.get('dissolved_oxygen', 0)),
                        'temperature': float(record.get('temperature', 0))
                    },
                    location={
                        'lat': float(record.get('lat', 0)),
                        'lng': float(record.get('lng', 0))
                    },
                    created_at=datetime.utcnow()
                )
                
                self.db.add(iot_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing IoT record: {e}", record)
        
        self.db.commit()
    
    def _import_environmental_health_data(self, records: List[Dict[str, Any]], **kwargs):
        """Import environmental health data"""
        from models.modules import EnvironmentalHealthData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['timestamp']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Validate coordinates
                if not self.validate_coordinates(record):
                    continue
                
                # Create environmental health record
                env_data = EnvironmentalHealthData(
                    location={
                        'lat': float(record.get('lat', 0)),
                        'lng': float(record.get('lng', 0)),
                        'address': record.get('address', '')
                    },
                    timestamp=record['timestamp'],
                    air_quality={
                        'pm25': float(record.get('pm25', 0)),
                        'pm10': float(record.get('pm10', 0)),
                        'no2': float(record.get('no2', 0)),
                        'o3': float(record.get('o3', 0)),
                        'co': float(record.get('co', 0)),
                        'so2': float(record.get('so2', 0)),
                        'aqi': float(record.get('aqi', 0))
                    },
                    water_quality={
                        'ph': float(record.get('ph', 7.0)),
                        'turbidity': float(record.get('turbidity', 0)),
                        'conductivity': float(record.get('conductivity', 0)),
                        'dissolved_oxygen': float(record.get('dissolved_oxygen', 0)),
                        'temperature': float(record.get('temperature', 0))
                    },
                    soil_quality={
                        'ph': float(record.get('soil_ph', 7.0)),
                        'organic_matter': float(record.get('organic_matter', 0)),
                        'nitrogen': float(record.get('nitrogen', 0)),
                        'phosphorus': float(record.get('phosphorus', 0)),
                        'potassium': float(record.get('potassium', 0)),
                        'heavy_metals': {
                            'lead': float(record.get('lead', 0)),
                            'cadmium': float(record.get('cadmium', 0)),
                            'mercury': float(record.get('mercury', 0)),
                            'arsenic': float(record.get('arsenic', 0)),
                            'chromium': float(record.get('chromium', 0))
                        }
                    },
                    noise_levels={
                        'day_level': float(record.get('day_noise', 0)),
                        'night_level': float(record.get('night_noise', 0)),
                        'peak_level': float(record.get('peak_noise', 0)),
                        'equivalent_level': float(record.get('equivalent_noise', 0))
                    },
                    environmental_indicators={
                        'biodiversity_index': float(record.get('biodiversity_index', 0)),
                        'green_coverage': float(record.get('green_coverage', 0)),
                        'air_pollution_index': float(record.get('air_pollution_index', 0)),
                        'water_pollution_index': float(record.get('water_pollution_index', 0)),
                        'soil_contamination_index': float(record.get('soil_contamination_index', 0)),
                        'overall_health_score': float(record.get('overall_health_score', 0))
                    },
                    created_at=datetime.utcnow()
                )
                
                self.db.add(env_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing environmental health record: {e}", record)
        
        self.db.commit()
    
    def _import_green_space_data(self, records: List[Dict[str, Any]], **kwargs):
        """Import urban green space data"""
        from models.modules import GreenSpaceData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['green_space_type', 'lat', 'lng', 'area']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Create green space record
                green_data = GreenSpaceData(
                    location={
                        'lat': float(record['lat']),
                        'lng': float(record['lng']),
                        'area': float(record['area'])
                    },
                    green_space_type=record['green_space_type'],
                    vegetation_data={
                        'tree_density': float(record.get('tree_density', 0)),
                        'canopy_cover': float(record.get('canopy_cover', 0)),
                        'species_diversity': float(record.get('species_diversity', 0)),
                        'vegetation_health': float(record.get('vegetation_health', 0)),
                        'seasonal_changes': []
                    },
                    ecosystem_services={
                        'carbon_sequestration': float(record.get('carbon_sequestration', 0)),
                        'air_purification': float(record.get('air_purification', 0)),
                        'water_filtration': float(record.get('water_filtration', 0)),
                        'temperature_regulation': float(record.get('temperature_regulation', 0)),
                        'biodiversity_support': float(record.get('biodiversity_support', 0)),
                        'recreational_value': float(record.get('recreational_value', 0))
                    },
                    accessibility={
                        'walking_distance': float(record.get('walking_distance', 0)),
                        'public_transport': bool(record.get('public_transport', False)),
                        'parking_available': bool(record.get('parking_available', False)),
                        'wheelchair_accessible': bool(record.get('wheelchair_accessible', False)),
                        'opening_hours': record.get('opening_hours', ''),
                        'visitor_capacity': int(record.get('visitor_capacity', 0))
                    },
                    maintenance_status={
                        'overall_condition': record.get('overall_condition', 'good'),
                        'last_maintenance': record.get('last_maintenance', ''),
                        'next_maintenance': record.get('next_maintenance', ''),
                        'maintenance_needs': record.get('maintenance_needs', []),
                        'budget_allocated': float(record.get('budget_allocated', 0))
                    },
                    created_at=datetime.utcnow()
                )
                
                self.db.add(green_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing green space record: {e}", record)
        
        self.db.commit()
    
    def _import_water_network_data(self, records: List[Dict[str, Any]], **kwargs):
        """Import urban water network data"""
        from models.modules import WaterNetworkData
        
        for record in records:
            try:
                # Validate required fields
                required_fields = ['network_id', 'timestamp', 'pressure', 'flow_rate']
                if not self.validate_required_fields(record, required_fields):
                    continue
                
                # Validate coordinates
                if not self.validate_coordinates(record):
                    continue
                
                # Create water network record
                network_data = WaterNetworkData(
                    network_id=record['network_id'],
                    location={
                        'lat': float(record.get('lat', 0)),
                        'lng': float(record.get('lng', 0))
                    },
                    timestamp=record['timestamp'],
                    pressure=float(record['pressure']),
                    flow_rate=float(record['flow_rate']),
                    water_quality={
                        'ph': float(record.get('ph', 7.0)),
                        'turbidity': float(record.get('turbidity', 0)),
                        'conductivity': float(record.get('conductivity', 0)),
                        'dissolved_oxygen': float(record.get('dissolved_oxygen', 0)),
                        'temperature': float(record.get('temperature', 0))
                    },
                    infrastructure_status={
                        'pipe_condition': record.get('pipe_condition', 'good'),
                        'age_years': int(record.get('age_years', 0)),
                        'material': record.get('material', ''),
                        'diameter': float(record.get('diameter', 0)),
                        'last_inspection': record.get('last_inspection', ''),
                        'maintenance_history': []
                    },
                    performance_metrics={
                        'efficiency_score': float(record.get('efficiency_score', 0)),
                        'reliability_index': float(record.get('reliability_index', 0)),
                        'water_loss_percentage': float(record.get('water_loss_percentage', 0)),
                        'customer_satisfaction': float(record.get('customer_satisfaction', 0)),
                        'response_time_minutes': float(record.get('response_time_minutes', 0))
                    },
                    created_at=datetime.utcnow()
                )
                
                self.db.add(network_data)
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing water network record: {e}", record)
        
        self.db.commit()
    
    def _import_generic_data(self, records: List[Dict[str, Any]], **kwargs):
        """Generic import for other modules"""
        # This would be implemented based on specific module requirements
        logger.info(f"Generic import for {self.module_name}: {len(records)} records")
        
        for record in records:
            try:
                # Basic validation
                if not record:
                    continue
                
                # Store as JSON in a generic table or log
                logger.info(f"Generic record: {record}")
                self.import_stats['imported_records'] += 1
                
            except Exception as e:
                self.add_error(f"Error importing generic record: {e}", record) 