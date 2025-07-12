"""
Data Import Manager
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_importer import BaseDataImporter
from .csv_importer import CSVDataImporter
from .api_importer import APIDataImporter
from .satellite_importer import SatelliteDataImporter
from .json_importer import JSONDataImporter
from .geojson_importer import GeoJSONDataImporter
from .sensor_importer import SensorDataImporter
from .weather_importer import WeatherDataImporter
from .gis_importer import GISDataImporter
from common_utils.exceptions import DataImportError
from config.settings import get_settings

logger = logging.getLogger(__name__)

class DataImportManager:
    """Manages data imports from multiple sources and formats"""
    
    def __init__(self):
        self.settings = get_settings()
        self.importers: Dict[str, BaseDataImporter] = {}
        self.import_history: List[Dict[str, Any]] = []
        self.max_workers = 4  # Maximum concurrent imports
        
    def register_importer(self, name: str, importer: BaseDataImporter):
        """Register a data importer"""
        self.importers[name] = importer
        logger.info(f"Registered importer: {name}")
    
    def get_importer(self, name: str) -> Optional[BaseDataImporter]:
        """Get a registered importer by name"""
        return self.importers.get(name)
    
    def list_importers(self) -> List[str]:
        """List all registered importers"""
        return list(self.importers.keys())
    
    def import_csv_data(self, module_name: str, file_path: str, 
                        field_mapping: Optional[Dict[str, str]] = None,
                        **kwargs) -> Dict[str, Any]:
        """Import data from CSV file"""
        try:
            importer = CSVDataImporter(
                module_name=module_name,
                data_source=file_path,
                field_mapping=field_mapping
            )
            
            with importer:
                result = importer.import_data(file_path, **kwargs)
                self._record_import(module_name, "csv", result)
                return result
                
        except Exception as e:
            logger.error(f"CSV import failed: {e}")
            raise DataImportError(f"CSV import failed: {e}")
    
    def import_api_data(self, module_name: str, api_config: Dict[str, Any],
                        **kwargs) -> Dict[str, Any]:
        """Import data from API"""
        try:
            importer = APIDataImporter(
                module_name=module_name,
                data_source=api_config.get('url', 'unknown'),
                api_config=api_config
            )
            
            with importer:
                result = importer.import_data(**kwargs)
                self._record_import(module_name, "api", result)
                return result
                
        except Exception as e:
            logger.error(f"API import failed: {e}")
            raise DataImportError(f"API import failed: {e}")
    
    def import_satellite_data(self, module_name: str, file_path: str,
                              satellite_type: str = "sentinel", **kwargs) -> Dict[str, Any]:
        """Import satellite data"""
        try:
            importer = SatelliteDataImporter(
                module_name=module_name,
                data_source=file_path,
                satellite_type=satellite_type
            )
            
            with importer:
                result = importer.import_data(file_path, **kwargs)
                self._record_import(module_name, "satellite", result)
                return result
                
        except Exception as e:
            logger.error(f"Satellite import failed: {e}")
            raise DataImportError(f"Satellite import failed: {e}")
    
    def import_json_data(self, module_name: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """Import data from JSON file"""
        try:
            importer = JSONDataImporter(
                module_name=module_name,
                data_source=file_path
            )
            
            with importer:
                result = importer.import_data(file_path, **kwargs)
                self._record_import(module_name, "json", result)
                return result
                
        except Exception as e:
            logger.error(f"JSON import failed: {e}")
            raise DataImportError(f"JSON import failed: {e}")
    
    def import_geojson_data(self, module_name: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """Import data from GeoJSON file"""
        try:
            importer = GeoJSONDataImporter(
                module_name=module_name,
                data_source=file_path
            )
            
            with importer:
                result = importer.import_data(file_path, **kwargs)
                self._record_import(module_name, "geojson", result)
                return result
                
        except Exception as e:
            logger.error(f"GeoJSON import failed: {e}")
            raise DataImportError(f"GeoJSON import failed: {e}")
    
    def import_sensor_data(self, module_name: str, data_source: str, **kwargs) -> Dict[str, Any]:
        """Import sensor data"""
        try:
            importer = SensorDataImporter(
                module_name=module_name,
                data_source=data_source
            )
            
            with importer:
                result = importer.import_data(data_source, **kwargs)
                self._record_import(module_name, "sensor", result)
                return result
                
        except Exception as e:
            logger.error(f"Sensor import failed: {e}")
            raise DataImportError(f"Sensor import failed: {e}")
    
    def import_weather_data(self, module_name: str, data_source: str, **kwargs) -> Dict[str, Any]:
        """Import weather data"""
        try:
            importer = WeatherDataImporter(
                module_name=module_name,
                data_source=data_source
            )
            
            with importer:
                result = importer.import_data(data_source, **kwargs)
                self._record_import(module_name, "weather", result)
                return result
                
        except Exception as e:
            logger.error(f"Weather import failed: {e}")
            raise DataImportError(f"Weather import failed: {e}")
    
    def import_gis_data(self, module_name: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """Import GIS data"""
        try:
            importer = GISDataImporter(
                module_name=module_name,
                data_source=file_path
            )
            
            with importer:
                result = importer.import_data(file_path, **kwargs)
                self._record_import(module_name, "gis", result)
                return result
                
        except Exception as e:
            logger.error(f"GIS import failed: {e}")
            raise DataImportError(f"GIS import failed: {e}")
    
    def batch_import(self, import_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple imports in parallel"""
        results = {
            'total_tasks': len(import_tasks),
            'completed_tasks': 0,
            'failed_tasks': 0,
            'results': [],
            'start_time': datetime.utcnow(),
            'end_time': None
        }
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_task = {}
                for task in import_tasks:
                    future = executor.submit(self._execute_import_task, task)
                    future_to_task[future] = task
                
                # Collect results
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        results['results'].append({
                            'task': task,
                            'status': 'success',
                            'result': result
                        })
                        results['completed_tasks'] += 1
                    except Exception as e:
                        results['results'].append({
                            'task': task,
                            'status': 'failed',
                            'error': str(e)
                        })
                        results['failed_tasks'] += 1
                        logger.error(f"Task failed: {task} - {e}")
            
            results['end_time'] = datetime.utcnow()
            duration = results['end_time'] - results['start_time']
            logger.info(f"Batch import completed: {results['completed_tasks']} successful, "
                        f"{results['failed_tasks']} failed in {duration}")
            
            return results
            
        except Exception as e:
            results['end_time'] = datetime.utcnow()
            logger.error(f"Batch import failed: {e}")
            raise DataImportError(f"Batch import failed: {e}")
    
    def _execute_import_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single import task"""
        import_type = task.get('type')
        module_name = task.get('module_name')
        data_source = task.get('data_source')
        
        if import_type == 'csv':
            return self.import_csv_data(module_name, data_source, **task.get('options', {}))
        elif import_type == 'api':
            return self.import_api_data(module_name, task.get('api_config', {}), **task.get('options', {}))
        elif import_type == 'satellite':
            return self.import_satellite_data(module_name, data_source, **task.get('options', {}))
        elif import_type == 'json':
            return self.import_json_data(module_name, data_source, **task.get('options', {}))
        elif import_type == 'geojson':
            return self.import_geojson_data(module_name, data_source, **task.get('options', {}))
        elif import_type == 'sensor':
            return self.import_sensor_data(module_name, data_source, **task.get('options', {}))
        elif import_type == 'weather':
            return self.import_weather_data(module_name, data_source, **task.get('options', {}))
        elif import_type == 'gis':
            return self.import_gis_data(module_name, data_source, **task.get('options', {}))
        else:
            raise DataImportError(f"Unsupported import type: {import_type}")
    
    def _record_import(self, module_name: str, import_type: str, result: Dict[str, Any]):
        """Record import history"""
        import_record = {
            'module_name': module_name,
            'import_type': import_type,
            'timestamp': datetime.utcnow(),
            'result': result
        }
        self.import_history.append(import_record)
        
        # Keep only last 1000 records
        if len(self.import_history) > 1000:
            self.import_history = self.import_history[-1000:]
    
    def get_import_history(self, module_name: Optional[str] = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get import history"""
        history = self.import_history
        
        if module_name:
            history = [record for record in history if record['module_name'] == module_name]
        
        return history[-limit:]
    
    def get_import_stats(self) -> Dict[str, Any]:
        """Get overall import statistics"""
        if not self.import_history:
            return {
                'total_imports': 0,
                'successful_imports': 0,
                'failed_imports': 0,
                'total_records': 0,
                'modules': {}
            }
        
        stats = {
            'total_imports': len(self.import_history),
            'successful_imports': 0,
            'failed_imports': 0,
            'total_records': 0,
            'modules': {}
        }
        
        for record in self.import_history:
            result = record['result']
            module_name = record['module_name']
            
            if result.get('imported_records', 0) > 0:
                stats['successful_imports'] += 1
                stats['total_records'] += result.get('imported_records', 0)
            else:
                stats['failed_imports'] += 1
            
            if module_name not in stats['modules']:
                stats['modules'][module_name] = {
                    'imports': 0,
                    'records': 0,
                    'last_import': None
                }
            
            stats['modules'][module_name]['imports'] += 1
            stats['modules'][module_name]['records'] += result.get('imported_records', 0)
            stats['modules'][module_name]['last_import'] = record['timestamp']
        
        return stats
    
    def schedule_recurring_import(self, task: Dict[str, Any], 
                                  interval_hours: int = 24) -> str:
        """Schedule a recurring import task"""
        # This would integrate with a task scheduler like Celery
        # For now, just log the schedule
        logger.info(f"Scheduled recurring import: {task} every {interval_hours} hours")
        return f"scheduled_{datetime.utcnow().timestamp()}"
    
    def cancel_scheduled_import(self, schedule_id: str):
        """Cancel a scheduled import"""
        logger.info(f"Cancelled scheduled import: {schedule_id}")
    
    def validate_import_config(self, config: Dict[str, Any]) -> bool:
        """Validate import configuration"""
        required_fields = ['type', 'module_name', 'data_source']
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field in import config: {field}")
                return False
        
        # Validate import type
        valid_types = ['csv', 'api', 'satellite', 'json', 'geojson', 'sensor', 'weather', 'gis']
        if config['type'] not in valid_types:
            logger.error(f"Invalid import type: {config['type']}")
            return False
        
        # Validate module name
        valid_modules = [
            'iot_water_consumption', 'environmental_health', 'urban_green_space',
            'urban_water_network', 'agricultural_reservoir', 'data_center_water',
            'drinking_water_quality', 'drought_prediction', 'dust_storm_analysis',
            'groundwater_pollution', 'insar_subsidence', 'transboundary_water',
            'urban_flood_modeling'
        ]
        if config['module_name'] not in valid_modules:
            logger.error(f"Invalid module name: {config['module_name']}")
            return False
        
        return True
    
    def create_sample_data(self, module_name: str, num_records: int = 100) -> Dict[str, Any]:
        """Create sample data for testing"""
        try:
            # This would generate realistic sample data based on the module
            logger.info(f"Creating {num_records} sample records for {module_name}")
            
            # For now, return a mock result
            return {
                'module_name': module_name,
                'data_source': 'sample_data',
                'total_records': num_records,
                'imported_records': num_records,
                'failed_records': 0,
                'success_rate': 100.0,
                'duration': '00:00:01',
                'error_count': 0
            }
            
        except Exception as e:
            logger.error(f"Sample data creation failed: {e}")
            raise DataImportError(f"Sample data creation failed: {e}")