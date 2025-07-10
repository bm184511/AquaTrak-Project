"""
Data Import System Tests
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import unittest
import tempfile
import os
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_importers.manager import DataImportManager
from data_importers.csv_importer import CSVDataImporter
from data_importers.api_importer import APIDataImporter
from data_importers.satellite_importer import SatelliteDataImporter
from common_utils.exceptions import DataImportError
from config.database import init_database, get_db
from models.base import Base

class TestDataImportSystem(unittest.TestCase):
    """Test suite for the data import system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("Setting up test environment...")
        
        # Initialize test database
        try:
            init_database()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            raise
        
        # Set up sample data paths
        cls.sample_data_dir = Path("sample_data")
        cls.iot_csv = cls.sample_data_dir / "iot_water_consumption.csv"
        cls.env_csv = cls.sample_data_dir / "environmental_health.csv"
        cls.green_csv = cls.sample_data_dir / "urban_green_space.csv"
        cls.network_csv = cls.sample_data_dir / "urban_water_network.csv"
        
        # Verify sample data exists
        for file_path in [cls.iot_csv, cls.env_csv, cls.green_csv, cls.network_csv]:
            if not file_path.exists():
                raise FileNotFoundError(f"Sample data file not found: {file_path}")
        
        print("✓ Sample data files verified")
    
    def setUp(self):
        """Set up for each test"""
        self.manager = DataImportManager()
    
    def test_01_csv_importer_initialization(self):
        """Test CSV importer initialization"""
        print("\nTesting CSV importer initialization...")
        
        try:
            importer = CSVDataImporter(
                module_name="iot_water_consumption",
                data_source="test.csv",
                field_mapping={"device_id": "sensor_id"}
            )
            
            self.assertEqual(importer.module_name, "iot_water_consumption")
            self.assertEqual(importer.data_source, "test.csv")
            self.assertEqual(importer.field_mapping, {"device_id": "sensor_id"})
            
            print("✓ CSV importer initialization successful")
            
        except Exception as e:
            print(f"✗ CSV importer initialization failed: {e}")
            raise
    
    def test_02_csv_data_validation(self):
        """Test CSV data validation"""
        print("\nTesting CSV data validation...")
        
        try:
            importer = CSVDataImporter("iot_water_consumption", str(self.iot_csv))
            
            # Test validation
            is_valid = importer.validate_data(self.iot_csv)
            self.assertTrue(is_valid)
            
            print("✓ CSV data validation successful")
            
        except Exception as e:
            print(f"✗ CSV data validation failed: {e}")
            raise
    
    def test_03_csv_data_transformation(self):
        """Test CSV data transformation"""
        print("\nTesting CSV data transformation...")
        
        try:
            importer = CSVDataImporter("iot_water_consumption", str(self.iot_csv))
            
            # Transform data
            records = importer.transform_data(self.iot_csv)
            
            # Verify transformation
            self.assertIsInstance(records, list)
            self.assertGreater(len(records), 0)
            
            # Check first record structure
            first_record = records[0]
            required_fields = ['device_id', 'timestamp', 'consumption']
            for field in required_fields:
                self.assertIn(field, first_record)
            
            print(f"✓ CSV data transformation successful: {len(records)} records")
            
        except Exception as e:
            print(f"✗ CSV data transformation failed: {e}")
            raise
    
    def test_04_iot_water_import(self):
        """Test IoT water consumption data import"""
        print("\nTesting IoT water consumption import...")
        
        try:
            result = self.manager.import_csv_data(
                module_name="iot_water_consumption",
                file_path=str(self.iot_csv)
            )
            
            # Verify import results
            self.assertIsInstance(result, dict)
            self.assertIn('imported_records', result)
            self.assertIn('total_records', result)
            self.assertIn('success_rate', result)
            
            self.assertGreater(result['imported_records'], 0)
            self.assertGreater(result['success_rate'], 0)
            
            print(f"✓ IoT water import successful: {result['imported_records']} records, "
                  f"{result['success_rate']}% success rate")
            
        except Exception as e:
            print(f"✗ IoT water import failed: {e}")
            raise
    
    def test_05_environmental_health_import(self):
        """Test environmental health data import"""
        print("\nTesting environmental health import...")
        
        try:
            result = self.manager.import_csv_data(
                module_name="environmental_health",
                file_path=str(self.env_csv)
            )
            
            # Verify import results
            self.assertIsInstance(result, dict)
            self.assertIn('imported_records', result)
            self.assertIn('total_records', result)
            self.assertIn('success_rate', result)
            
            self.assertGreater(result['imported_records'], 0)
            self.assertGreater(result['success_rate'], 0)
            
            print(f"✓ Environmental health import successful: {result['imported_records']} records, "
                  f"{result['success_rate']}% success rate")
            
        except Exception as e:
            print(f"✗ Environmental health import failed: {e}")
            raise
    
    def test_06_urban_green_space_import(self):
        """Test urban green space data import"""
        print("\nTesting urban green space import...")
        
        try:
            result = self.manager.import_csv_data(
                module_name="urban_green_space",
                file_path=str(self.green_csv)
            )
            
            # Verify import results
            self.assertIsInstance(result, dict)
            self.assertIn('imported_records', result)
            self.assertIn('total_records', result)
            self.assertIn('success_rate', result)
            
            self.assertGreater(result['imported_records'], 0)
            self.assertGreater(result['success_rate'], 0)
            
            print(f"✓ Urban green space import successful: {result['imported_records']} records, "
                  f"{result['success_rate']}% success rate")
            
        except Exception as e:
            print(f"✗ Urban green space import failed: {e}")
            raise
    
    def test_07_urban_water_network_import(self):
        """Test urban water network data import"""
        print("\nTesting urban water network import...")
        
        try:
            result = self.manager.import_csv_data(
                module_name="urban_water_network",
                file_path=str(self.network_csv)
            )
            
            # Verify import results
            self.assertIsInstance(result, dict)
            self.assertIn('imported_records', result)
            self.assertIn('total_records', result)
            self.assertIn('success_rate', result)
            
            self.assertGreater(result['imported_records'], 0)
            self.assertGreater(result['success_rate'], 0)
            
            print(f"✓ Urban water network import successful: {result['imported_records']} records, "
                  f"{result['success_rate']}% success rate")
            
        except Exception as e:
            print(f"✗ Urban water network import failed: {e}")
            raise
    
    def test_08_batch_import(self):
        """Test batch import functionality"""
        print("\nTesting batch import...")
        
        try:
            import_tasks = [
                {
                    'type': 'csv',
                    'module_name': 'iot_water_consumption',
                    'data_source': str(self.iot_csv)
                },
                {
                    'type': 'csv',
                    'module_name': 'environmental_health',
                    'data_source': str(self.env_csv)
                }
            ]
            
            results = self.manager.batch_import(import_tasks)
            
            # Verify batch results
            self.assertIsInstance(results, dict)
            self.assertIn('total_tasks', results)
            self.assertIn('completed_tasks', results)
            self.assertIn('failed_tasks', results)
            self.assertIn('results', results)
            
            self.assertEqual(results['total_tasks'], 2)
            self.assertGreaterEqual(results['completed_tasks'], 0)
            
            print(f"✓ Batch import successful: {results['completed_tasks']}/{results['total_tasks']} tasks completed")
            
        except Exception as e:
            print(f"✗ Batch import failed: {e}")
            raise
    
    def test_09_field_mapping(self):
        """Test field mapping functionality"""
        print("\nTesting field mapping...")
        
        try:
            # Create test CSV with different field names
            test_data = [
                {'sensor_id': 'test_001', 'time': '2024-01-01T00:00:00', 'water_usage': 100.5},
                {'sensor_id': 'test_002', 'time': '2024-01-01T01:00:00', 'water_usage': 150.2}
            ]
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=['sensor_id', 'time', 'water_usage'])
                writer.writeheader()
                for row in test_data:
                    writer.writerow(row)
                temp_path = temp_file.name
            
            try:
                # Import with field mapping
                field_mapping = {
                    'sensor_id': 'device_id',
                    'time': 'timestamp',
                    'water_usage': 'consumption'
                }
                
                result = self.manager.import_csv_data(
                    module_name="iot_water_consumption",
                    file_path=temp_path,
                    field_mapping=field_mapping
                )
                
                self.assertGreater(result['imported_records'], 0)
                print("✓ Field mapping successful")
                
            finally:
                # Clean up
                os.unlink(temp_path)
            
        except Exception as e:
            print(f"✗ Field mapping failed: {e}")
            raise
    
    def test_10_data_validation(self):
        """Test data validation features"""
        print("\nTesting data validation...")
        
        try:
            importer = CSVDataImporter("iot_water_consumption", "test.csv")
            
            # Test required fields validation
            valid_record = {
                'device_id': 'test_001',
                'timestamp': '2024-01-01T00:00:00',
                'consumption': 100.5
            }
            
            is_valid = importer.validate_required_fields(
                valid_record, 
                ['device_id', 'timestamp', 'consumption']
            )
            self.assertTrue(is_valid)
            
            # Test invalid record
            invalid_record = {
                'device_id': 'test_001',
                'consumption': 100.5
                # Missing timestamp
            }
            
            is_valid = importer.validate_required_fields(
                invalid_record, 
                ['device_id', 'timestamp', 'consumption']
            )
            self.assertFalse(is_valid)
            
            # Test coordinate validation
            valid_coords = {'lat': 40.7128, 'lng': -74.0060}
            is_valid = importer.validate_coordinates(valid_coords)
            self.assertTrue(is_valid)
            
            invalid_coords = {'lat': 100.0, 'lng': -200.0}  # Invalid coordinates
            is_valid = importer.validate_coordinates(invalid_coords)
            self.assertFalse(is_valid)
            
            print("✓ Data validation successful")
            
        except Exception as e:
            print(f"✗ Data validation failed: {e}")
            raise
    
    def test_11_error_handling(self):
        """Test error handling"""
        print("\nTesting error handling...")
        
        try:
            # Test with non-existent file
            with self.assertRaises(DataImportError):
                self.manager.import_csv_data(
                    module_name="iot_water_consumption",
                    file_path="non_existent_file.csv"
                )
            
            # Test with invalid module name
            with self.assertRaises(Exception):
                self.manager.import_csv_data(
                    module_name="invalid_module",
                    file_path=str(self.iot_csv)
                )
            
            print("✓ Error handling successful")
            
        except Exception as e:
            print(f"✗ Error handling failed: {e}")
            raise
    
    def test_12_import_statistics(self):
        """Test import statistics tracking"""
        print("\nTesting import statistics...")
        
        try:
            # Get import stats
            stats = self.manager.get_import_stats()
            
            # Verify stats structure
            self.assertIsInstance(stats, dict)
            self.assertIn('total_imports', stats)
            self.assertIn('successful_imports', stats)
            self.assertIn('failed_imports', stats)
            self.assertIn('total_records', stats)
            self.assertIn('modules', stats)
            
            # Get import history
            history = self.manager.get_import_history(limit=10)
            self.assertIsInstance(history, list)
            
            print(f"✓ Import statistics successful: {stats['total_imports']} total imports, "
                  f"{stats['total_records']} total records")
            
        except Exception as e:
            print(f"✗ Import statistics failed: {e}")
            raise
    
    def test_13_api_importer_initialization(self):
        """Test API importer initialization"""
        print("\nTesting API importer initialization...")
        
        try:
            api_config = {
                'url': 'https://api.example.com/data',
                'method': 'GET',
                'api_key': 'test_key'
            }
            
            importer = APIDataImporter(
                module_name="weather_data",
                data_source="weather_api",
                api_config=api_config
            )
            
            self.assertEqual(importer.module_name, "weather_data")
            self.assertEqual(importer.data_source, "weather_api")
            self.assertEqual(importer.api_config, api_config)
            
            print("✓ API importer initialization successful")
            
        except Exception as e:
            print(f"✗ API importer initialization failed: {e}")
            raise
    
    def test_14_satellite_importer_initialization(self):
        """Test satellite importer initialization"""
        print("\nTesting satellite importer initialization...")
        
        try:
            importer = SatelliteDataImporter(
                module_name="satellite_data",
                data_source="sentinel_data",
                satellite_type="sentinel",
                processing_level="L2A"
            )
            
            self.assertEqual(importer.module_name, "satellite_data")
            self.assertEqual(importer.satellite_type, "sentinel")
            self.assertEqual(importer.processing_level, "L2A")
            
            print("✓ Satellite importer initialization successful")
            
        except Exception as e:
            print(f"✗ Satellite importer initialization failed: {e}")
            raise
    
    def test_15_sample_data_creation(self):
        """Test sample data creation"""
        print("\nTesting sample data creation...")
        
        try:
            result = self.manager.create_sample_data(
                module_name="iot_water_consumption",
                num_records=50
            )
            
            self.assertIsInstance(result, dict)
            self.assertIn('imported_records', result)
            self.assertIn('total_records', result)
            
            print(f"✓ Sample data creation successful: {result['imported_records']} records")
            
        except Exception as e:
            print(f"✗ Sample data creation failed: {e}")
            raise

def run_tests():
    """Run all tests"""
    print("="*60)
    print("AQUATRAK DATA IMPORT SYSTEM TESTS")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataImportSystem)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 