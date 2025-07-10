"""
Data Import Performance Tests
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import unittest
import tempfile
import time
import csv
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_importers.manager import DataImportManager
from data_importers.csv_importer import CSVDataImporter
from config.database import init_database

class TestDataImportPerformance(unittest.TestCase):
    """Test suite for data import performance"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("Setting up performance test environment...")
        
        # Initialize test database
        try:
            init_database()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            raise
        
        cls.manager = DataImportManager()
        cls.performance_thresholds = {
            'small_dataset': 1000,    # records
            'medium_dataset': 10000,  # records
            'large_dataset': 100000,  # records
            'small_time': 5,          # seconds
            'medium_time': 30,        # seconds
            'large_time': 300         # seconds
        }
        
        print("✓ Performance test environment ready")
    
    def generate_large_dataset(self, num_records: int, module_name: str) -> str:
        """Generate a large dataset for testing"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        
        if module_name == "iot_water_consumption":
            # Generate IoT water consumption data
            fieldnames = ['device_id', 'timestamp', 'consumption', 'flow_rate', 'pressure', 'temperature', 'lat', 'lng']
            
            with temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()
                
                base_time = datetime.utcnow() - timedelta(days=30)
                
                for i in range(num_records):
                    timestamp = base_time + timedelta(hours=i)
                    
                    record = {
                        'device_id': f"device_{i % 100:03d}",
                        'timestamp': timestamp.isoformat(),
                        'consumption': round(random.uniform(10, 200), 2),
                        'flow_rate': round(random.uniform(0.5, 5.0), 2),
                        'pressure': round(random.uniform(2.0, 8.0), 2),
                        'temperature': round(random.uniform(15, 25), 1),
                        'lat': round(random.uniform(25.0, 50.0), 6),
                        'lng': round(random.uniform(-120.0, -70.0), 6)
                    }
                    writer.writerow(record)
        
        return temp_file.name
    
    def test_01_small_dataset_performance(self):
        """Test performance with small dataset (1,000 records)"""
        print("\nTesting small dataset performance (1,000 records)...")
        
        try:
            # Generate small dataset
            dataset_path = self.generate_large_dataset(1000, "iot_water_consumption")
            
            try:
                # Measure import time
                start_time = time.time()
                
                result = self.manager.import_csv_data(
                    module_name="iot_water_consumption",
                    file_path=dataset_path
                )
                
                end_time = time.time()
                import_time = end_time - start_time
                
                # Verify performance
                self.assertLess(import_time, self.performance_thresholds['small_time'])
                self.assertEqual(result['total_records'], 1000)
                self.assertGreater(result['success_rate'], 95)
                
                print(f"✓ Small dataset import successful: {import_time:.2f}s, "
                      f"{result['success_rate']}% success rate")
                
            finally:
                # Clean up
                import os
                os.unlink(dataset_path)
            
        except Exception as e:
            print(f"✗ Small dataset performance test failed: {e}")
            raise
    
    def test_02_medium_dataset_performance(self):
        """Test performance with medium dataset (10,000 records)"""
        print("\nTesting medium dataset performance (10,000 records)...")
        
        try:
            # Generate medium dataset
            dataset_path = self.generate_large_dataset(10000, "iot_water_consumption")
            
            try:
                # Measure import time
                start_time = time.time()
                
                result = self.manager.import_csv_data(
                    module_name="iot_water_consumption",
                    file_path=dataset_path
                )
                
                end_time = time.time()
                import_time = end_time - start_time
                
                # Verify performance
                self.assertLess(import_time, self.performance_thresholds['medium_time'])
                self.assertEqual(result['total_records'], 10000)
                self.assertGreater(result['success_rate'], 95)
                
                print(f"✓ Medium dataset import successful: {import_time:.2f}s, "
                      f"{result['success_rate']}% success rate")
                
            finally:
                # Clean up
                import os
                os.unlink(dataset_path)
            
        except Exception as e:
            print(f"✗ Medium dataset performance test failed: {e}")
            raise
    
    def test_03_large_dataset_performance(self):
        """Test performance with large dataset (100,000 records)"""
        print("\nTesting large dataset performance (100,000 records)...")
        
        try:
            # Generate large dataset
            dataset_path = self.generate_large_dataset(100000, "iot_water_consumption")
            
            try:
                # Measure import time
                start_time = time.time()
                
                result = self.manager.import_csv_data(
                    module_name="iot_water_consumption",
                    file_path=dataset_path
                )
                
                end_time = time.time()
                import_time = end_time - start_time
                
                # Verify performance
                self.assertLess(import_time, self.performance_thresholds['large_time'])
                self.assertEqual(result['total_records'], 100000)
                self.assertGreater(result['success_rate'], 95)
                
                print(f"✓ Large dataset import successful: {import_time:.2f}s, "
                      f"{result['success_rate']}% success rate")
                
            finally:
                # Clean up
                import os
                os.unlink(dataset_path)
            
        except Exception as e:
            print(f"✗ Large dataset performance test failed: {e}")
            raise
    
    def test_04_batch_import_performance(self):
        """Test batch import performance"""
        print("\nTesting batch import performance...")
        
        try:
            # Generate multiple datasets
            datasets = []
            for i in range(3):
                dataset_path = self.generate_large_dataset(1000, "iot_water_consumption")
                datasets.append(dataset_path)
            
            try:
                # Create batch import tasks
                import_tasks = [
                    {
                        'type': 'csv',
                        'module_name': 'iot_water_consumption',
                        'data_source': dataset_path
                    }
                    for dataset_path in datasets
                ]
                
                # Measure batch import time
                start_time = time.time()
                
                result = self.manager.batch_import(import_tasks)
                
                end_time = time.time()
                import_time = end_time - start_time
                
                # Verify performance
                self.assertLess(import_time, self.performance_thresholds['medium_time'])
                self.assertEqual(result['total_tasks'], 3)
                self.assertEqual(result['completed_tasks'], 3)
                self.assertEqual(result['failed_tasks'], 0)
                
                print(f"✓ Batch import successful: {import_time:.2f}s, "
                      f"{result['completed_tasks']}/{result['total_tasks']} tasks completed")
                
            finally:
                # Clean up
                import os
                for dataset_path in datasets:
                    os.unlink(dataset_path)
            
        except Exception as e:
            print(f"✗ Batch import performance test failed: {e}")
            raise
    
    def test_05_memory_usage(self):
        """Test memory usage during large imports"""
        print("\nTesting memory usage...")
        
        try:
            import psutil
            import os
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Generate and import large dataset
            dataset_path = self.generate_large_dataset(50000, "iot_water_consumption")
            
            try:
                result = self.manager.import_csv_data(
                    module_name="iot_water_consumption",
                    file_path=dataset_path
                )
                
                # Get final memory usage
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                # Verify memory usage is reasonable (less than 500MB increase)
                self.assertLess(memory_increase, 500)
                
                print(f"✓ Memory usage test successful: {memory_increase:.2f}MB increase")
                
            finally:
                # Clean up
                os.unlink(dataset_path)
            
        except ImportError:
            print("⚠ psutil not available, skipping memory test")
        except Exception as e:
            print(f"✗ Memory usage test failed: {e}")
            raise
    
    def test_06_concurrent_imports(self):
        """Test concurrent import performance"""
        print("\nTesting concurrent imports...")
        
        try:
            import threading
            import queue
            
            # Generate datasets
            datasets = []
            for i in range(5):
                dataset_path = self.generate_large_dataset(1000, "iot_water_consumption")
                datasets.append(dataset_path)
            
            try:
                results_queue = queue.Queue()
                
                def import_dataset(dataset_path, thread_id):
                    """Import dataset in separate thread"""
                    try:
                        start_time = time.time()
                        
                        result = self.manager.import_csv_data(
                            module_name="iot_water_consumption",
                            file_path=dataset_path
                        )
                        
                        end_time = time.time()
                        import_time = end_time - start_time
                        
                        results_queue.put({
                            'thread_id': thread_id,
                            'success': True,
                            'time': import_time,
                            'records': result['imported_records']
                        })
                        
                    except Exception as e:
                        results_queue.put({
                            'thread_id': thread_id,
                            'success': False,
                            'error': str(e)
                        })
                
                # Start concurrent imports
                threads = []
                start_time = time.time()
                
                for i, dataset_path in enumerate(datasets):
                    thread = threading.Thread(
                        target=import_dataset,
                        args=(dataset_path, i)
                    )
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # Collect results
                results = []
                while not results_queue.empty():
                    results.append(results_queue.get())
                
                # Verify results
                successful_imports = [r for r in results if r['success']]
                self.assertEqual(len(successful_imports), 5)
                
                # Check performance (should be faster than sequential)
                sequential_time = sum(r['time'] for r in successful_imports)
                self.assertLess(total_time, sequential_time * 1.5)  # Allow some overhead
                
                print(f"✓ Concurrent imports successful: {total_time:.2f}s total, "
                      f"{len(successful_imports)}/5 successful")
                
            finally:
                # Clean up
                import os
                for dataset_path in datasets:
                    os.unlink(dataset_path)
            
        except Exception as e:
            print(f"✗ Concurrent imports test failed: {e}")
            raise
    
    def test_07_error_recovery_performance(self):
        """Test performance with error recovery"""
        print("\nTesting error recovery performance...")
        
        try:
            # Create dataset with some invalid records
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
            
            with temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=['device_id', 'timestamp', 'consumption'])
                writer.writeheader()
                
                # Add valid records
                for i in range(1000):
                    record = {
                        'device_id': f"device_{i:03d}",
                        'timestamp': (datetime.utcnow() + timedelta(hours=i)).isoformat(),
                        'consumption': random.uniform(10, 200)
                    }
                    writer.writerow(record)
                
                # Add some invalid records
                for i in range(50):
                    record = {
                        'device_id': f"device_invalid_{i}",
                        'timestamp': 'invalid_timestamp',  # Invalid timestamp
                        'consumption': 'invalid_consumption'  # Invalid consumption
                    }
                    writer.writerow(record)
            
            dataset_path = temp_file.name
            
            try:
                # Measure import time with errors
                start_time = time.time()
                
                result = self.manager.import_csv_data(
                    module_name="iot_water_consumption",
                    file_path=dataset_path
                )
                
                end_time = time.time()
                import_time = end_time - start_time
                
                # Verify error handling performance
                self.assertLess(import_time, self.performance_thresholds['small_time'])
                self.assertEqual(result['total_records'], 1050)
                self.assertGreater(result['imported_records'], 1000)  # Most records should be imported
                self.assertGreater(result['failed_records'], 0)  # Some should fail
                
                print(f"✓ Error recovery test successful: {import_time:.2f}s, "
                      f"{result['imported_records']} imported, {result['failed_records']} failed")
                
            finally:
                # Clean up
                import os
                os.unlink(dataset_path)
            
        except Exception as e:
            print(f"✗ Error recovery performance test failed: {e}")
            raise

def run_performance_tests():
    """Run all performance tests"""
    print("="*60)
    print("AQUATRAK DATA IMPORT PERFORMANCE TESTS")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataImportPerformance)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*60)
    print("PERFORMANCE TEST SUMMARY")
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
        print("\n🎉 ALL PERFORMANCE TESTS PASSED!")
    else:
        print("\n❌ SOME PERFORMANCE TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1) 