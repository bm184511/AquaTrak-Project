"""
Data Import API Endpoints Tests
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import unittest
import tempfile
import json
import csv
from pathlib import Path
import sys
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import app
from config.database import init_database

class TestDataImportAPI(unittest.TestCase):
    """Test suite for data import API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("Setting up API test environment...")
        
        # Initialize test database
        try:
            init_database()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            raise
        
        # Create test client
        cls.client = TestClient(app)
        
        # Set up sample data paths
        cls.sample_data_dir = Path("sample_data")
        cls.iot_csv = cls.sample_data_dir / "iot_water_consumption.csv"
        
        print("✓ API test environment ready")
    
    def test_01_get_supported_formats(self):
        """Test GET /api/data-import/supported-formats"""
        print("\nTesting supported formats endpoint...")
        
        try:
            response = self.client.get("/api/data-import/supported-formats")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("formats", data)
            self.assertIsInstance(data["formats"], list)
            
            # Check for expected formats
            format_types = [fmt["type"] for fmt in data["formats"]]
            expected_types = ["csv", "json", "geojson", "api", "satellite"]
            
            for expected_type in expected_types:
                self.assertIn(expected_type, format_types)
            
            print("✓ Supported formats endpoint successful")
            
        except Exception as e:
            print(f"✗ Supported formats endpoint failed: {e}")
            raise
    
    def test_02_get_supported_modules(self):
        """Test GET /api/data-import/modules"""
        print("\nTesting supported modules endpoint...")
        
        try:
            response = self.client.get("/api/data-import/modules")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("modules", data)
            self.assertIsInstance(data["modules"], list)
            
            # Check for expected modules
            module_names = [module["name"] for module in data["modules"]]
            expected_modules = [
                "iot_water_consumption", "environmental_health", 
                "urban_green_space", "urban_water_network"
            ]
            
            for expected_module in expected_modules:
                self.assertIn(expected_module, module_names)
            
            print("✓ Supported modules endpoint successful")
            
        except Exception as e:
            print(f"✗ Supported modules endpoint failed: {e}")
            raise
    
    def test_03_get_import_stats(self):
        """Test GET /api/data-import/stats"""
        print("\nTesting import stats endpoint...")
        
        try:
            response = self.client.get("/api/data-import/stats")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify stats structure
            self.assertIn("total_imports", data)
            self.assertIn("successful_imports", data)
            self.assertIn("failed_imports", data)
            self.assertIn("total_records", data)
            self.assertIn("modules", data)
            
            self.assertIsInstance(data["total_imports"], int)
            self.assertIsInstance(data["successful_imports"], int)
            self.assertIsInstance(data["failed_imports"], int)
            self.assertIsInstance(data["total_records"], int)
            self.assertIsInstance(data["modules"], dict)
            
            print("✓ Import stats endpoint successful")
            
        except Exception as e:
            print(f"✗ Import stats endpoint failed: {e}")
            raise
    
    def test_04_get_import_history(self):
        """Test GET /api/data-import/history"""
        print("\nTesting import history endpoint...")
        
        try:
            response = self.client.get("/api/data-import/history")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("history", data)
            self.assertIsInstance(data["history"], list)
            
            print("✓ Import history endpoint successful")
            
        except Exception as e:
            print(f"✗ Import history endpoint failed: {e}")
            raise
    
    def test_05_single_import_csv(self):
        """Test POST /api/data-import/single with CSV data"""
        print("\nTesting single CSV import endpoint...")
        
        try:
            # Create test CSV file
            test_data = [
                {'device_id': 'test_001', 'timestamp': '2024-01-01T00:00:00', 'consumption': 100.5},
                {'device_id': 'test_002', 'timestamp': '2024-01-01T01:00:00', 'consumption': 150.2}
            ]
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=['device_id', 'timestamp', 'consumption'])
                writer.writeheader()
                for row in test_data:
                    writer.writerow(row)
                temp_path = temp_file.name
            
            try:
                # Test single import
                import_request = {
                    "type": "csv",
                    "module_name": "iot_water_consumption",
                    "data_source": temp_path,
                    "options": {}
                }
                
                response = self.client.post(
                    "/api/data-import/single",
                    json=import_request
                )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                self.assertIn("imported_records", data)
                self.assertIn("total_records", data)
                self.assertIn("success_rate", data)
                
                self.assertGreater(data["imported_records"], 0)
                
                print(f"✓ Single CSV import successful: {data['imported_records']} records")
                
            finally:
                # Clean up
                import os
                os.unlink(temp_path)
            
        except Exception as e:
            print(f"✗ Single CSV import failed: {e}")
            raise
    
    def test_06_batch_import(self):
        """Test POST /api/data-import/batch"""
        print("\nTesting batch import endpoint...")
        
        try:
            batch_request = {
                "tasks": [
                    {
                        "type": "csv",
                        "module_name": "iot_water_consumption",
                        "data_source": str(self.iot_csv),
                        "options": {}
                    }
                ],
                "parallel": True
            }
            
            response = self.client.post(
                "/api/data-import/batch",
                json=batch_request
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("total_tasks", data)
            self.assertIn("completed_tasks", data)
            self.assertIn("failed_tasks", data)
            self.assertIn("results", data)
            
            self.assertEqual(data["total_tasks"], 1)
            self.assertGreaterEqual(data["completed_tasks"], 0)
            
            print(f"✓ Batch import successful: {data['completed_tasks']}/{data['total_tasks']} tasks")
            
        except Exception as e:
            print(f"✗ Batch import failed: {e}")
            raise
    
    def test_07_upload_csv_file(self):
        """Test POST /api/data-import/upload-csv"""
        print("\nTesting CSV file upload endpoint...")
        
        try:
            # Create test CSV file
            test_data = [
                {'device_id': 'upload_test_001', 'timestamp': '2024-01-01T00:00:00', 'consumption': 100.5},
                {'device_id': 'upload_test_002', 'timestamp': '2024-01-01T01:00:00', 'consumption': 150.2}
            ]
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=['device_id', 'timestamp', 'consumption'])
                writer.writeheader()
                for row in test_data:
                    writer.writerow(row)
                temp_path = temp_file.name
            
            try:
                # Test file upload
                with open(temp_path, 'rb') as file:
                    response = self.client.post(
                        "/api/data-import/upload-csv",
                        files={"file": ("test.csv", file, "text/csv")},
                        data={"module_name": "iot_water_consumption"}
                    )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                self.assertIn("imported_records", data)
                self.assertIn("total_records", data)
                self.assertIn("success_rate", data)
                
                self.assertGreater(data["imported_records"], 0)
                
                print(f"✓ CSV file upload successful: {data['imported_records']} records")
                
            finally:
                # Clean up
                import os
                os.unlink(temp_path)
            
        except Exception as e:
            print(f"✗ CSV file upload failed: {e}")
            raise
    
    def test_08_upload_json_file(self):
        """Test POST /api/data-import/upload-json"""
        print("\nTesting JSON file upload endpoint...")
        
        try:
            # Create test JSON file
            test_data = [
                {'device_id': 'json_test_001', 'timestamp': '2024-01-01T00:00:00', 'consumption': 100.5},
                {'device_id': 'json_test_002', 'timestamp': '2024-01-01T01:00:00', 'consumption': 150.2}
            ]
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                json.dump(test_data, temp_file)
                temp_path = temp_file.name
            
            try:
                # Test file upload
                with open(temp_path, 'rb') as file:
                    response = self.client.post(
                        "/api/data-import/upload-json",
                        files={"file": ("test.json", file, "application/json")},
                        data={"module_name": "iot_water_consumption"}
                    )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                self.assertIn("imported_records", data)
                self.assertIn("total_records", data)
                self.assertIn("success_rate", data)
                
                print(f"✓ JSON file upload successful: {data['imported_records']} records")
                
            finally:
                # Clean up
                import os
                os.unlink(temp_path)
            
        except Exception as e:
            print(f"✗ JSON file upload failed: {e}")
            raise
    
    def test_09_sample_data_creation(self):
        """Test POST /api/data-import/sample-data"""
        print("\nTesting sample data creation endpoint...")
        
        try:
            response = self.client.post(
                "/api/data-import/sample-data",
                params={"module_name": "iot_water_consumption", "num_records": 10}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("imported_records", data)
            self.assertIn("total_records", data)
            self.assertIn("success_rate", data)
            
            print(f"✓ Sample data creation successful: {data['imported_records']} records")
            
        except Exception as e:
            print(f"✗ Sample data creation failed: {e}")
            raise
    
    def test_10_error_handling(self):
        """Test error handling in API endpoints"""
        print("\nTesting API error handling...")
        
        try:
            # Test invalid import type
            invalid_request = {
                "type": "invalid_type",
                "module_name": "iot_water_consumption",
                "data_source": "test.csv"
            }
            
            response = self.client.post(
                "/api/data-import/single",
                json=invalid_request
            )
            
            self.assertEqual(response.status_code, 400)
            
            # Test invalid module name
            invalid_module_request = {
                "type": "csv",
                "module_name": "invalid_module",
                "data_source": "test.csv"
            }
            
            response = self.client.post(
                "/api/data-import/single",
                json=invalid_module_request
            )
            
            self.assertEqual(response.status_code, 400)
            
            print("✓ API error handling successful")
            
        except Exception as e:
            print(f"✗ API error handling failed: {e}")
            raise
    
    def test_11_field_mapping_api(self):
        """Test field mapping in API"""
        print("\nTesting field mapping in API...")
        
        try:
            # Create test CSV with different field names
            test_data = [
                {'sensor_id': 'api_test_001', 'time': '2024-01-01T00:00:00', 'water_usage': 100.5},
                {'sensor_id': 'api_test_002', 'time': '2024-01-01T01:00:00', 'water_usage': 150.2}
            ]
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=['sensor_id', 'time', 'water_usage'])
                writer.writeheader()
                for row in test_data:
                    writer.writerow(row)
                temp_path = temp_file.name
            
            try:
                # Test with field mapping
                import_request = {
                    "type": "csv",
                    "module_name": "iot_water_consumption",
                    "data_source": temp_path,
                    "field_mapping": {
                        "sensor_id": "device_id",
                        "time": "timestamp",
                        "water_usage": "consumption"
                    },
                    "options": {}
                }
                
                response = self.client.post(
                    "/api/data-import/single",
                    json=import_request
                )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                self.assertGreater(data["imported_records"], 0)
                
                print("✓ Field mapping API successful")
                
            finally:
                # Clean up
                import os
                os.unlink(temp_path)
            
        except Exception as e:
            print(f"✗ Field mapping API failed: {e}")
            raise

def run_api_tests():
    """Run all API tests"""
    print("="*60)
    print("AQUATRAK DATA IMPORT API TESTS")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataImportAPI)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("API TEST SUMMARY")
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
        print("\n🎉 ALL API TESTS PASSED!")
    else:
        print("\n❌ SOME API TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1) 