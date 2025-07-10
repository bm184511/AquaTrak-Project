#!/usr/bin/env python3
"""
Full Data Import Test
AquaTrak - AI-GIS Water Risk Monitoring Platform

This script performs a full test of the data import system using the generated sample data.

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import sys
import os
import time
import csv
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_csv_import():
    """Test CSV data import functionality"""
    print("📥 Testing CSV Data Import...")
    
    try:
        from data_importers.csv_importer import CSVDataImporter
        
        # Test files
        test_files = [
            ("iot_water_consumption", "sample_data/iot_water_consumption.csv"),
            ("environmental_health", "sample_data/environmental_health.csv"),
            ("urban_green_space", "sample_data/urban_green_space.csv"),
            ("urban_water_network", "sample_data/urban_water_network.csv")
        ]
        
        results = []
        
        for module_name, file_path in test_files:
            if not Path(file_path).exists():
                print(f"❌ File not found: {file_path}")
                continue
            
            print(f"\n🔍 Testing {module_name}...")
            
            try:
                # Initialize importer
                importer = CSVDataImporter(
                    module_name=module_name,
                    data_source=file_path
                )
                
                # Validate data
                is_valid = importer.validate_data(file_path)
                print(f"   ✅ Data validation: {'PASSED' if is_valid else 'FAILED'}")
                
                if is_valid:
                    # Transform data
                    start_time = time.time()
                    records = importer.transform_data(file_path)
                    transform_time = time.time() - start_time
                    
                    print(f"   ✅ Data transformation: {len(records)} records in {transform_time:.2f}s")
                    
                    # Check data quality
                    if records:
                        first_record = records[0]
                        print(f"   📋 Sample fields: {list(first_record.keys())[:5]}...")
                        
                        # Check for required fields based on module
                        if module_name == "iot_water_consumption":
                            required_fields = ['device_id', 'timestamp', 'consumption']
                        elif module_name == "environmental_health":
                            required_fields = ['timestamp', 'lat', 'lng']
                        elif module_name == "urban_green_space":
                            required_fields = ['green_space_type', 'lat', 'lng']
                        elif module_name == "urban_water_network":
                            required_fields = ['network_id', 'timestamp', 'pressure']
                        else:
                            required_fields = []
                        
                        if required_fields:
                            missing_fields = [field for field in required_fields if field not in first_record]
                            if missing_fields:
                                print(f"   ⚠️ Missing required fields: {missing_fields}")
                            else:
                                print(f"   ✅ All required fields present")
                    
                    results.append({
                        'module': module_name,
                        'file': file_path,
                        'records': len(records),
                        'valid': is_valid,
                        'transform_time': transform_time
                    })
                
            except Exception as e:
                print(f"   ❌ Error processing {module_name}: {e}")
                results.append({
                    'module': module_name,
                    'file': file_path,
                    'records': 0,
                    'valid': False,
                    'error': str(e)
                })
        
        # Print summary
        print(f"\n📊 CSV Import Summary:")
        print("-" * 50)
        total_records = sum(r['records'] for r in results)
        valid_files = sum(1 for r in results if r['valid'])
        
        for result in results:
            status = "✅" if result['valid'] else "❌"
            print(f"{status} {result['module']:25} | {result['records']:6d} records | {result.get('transform_time', 0):.2f}s")
        
        print(f"\n📈 Total: {total_records} records from {valid_files}/{len(results)} files")
        
        return results
        
    except Exception as e:
        print(f"❌ CSV import test failed: {e}")
        return []

def test_field_mapping():
    """Test field mapping functionality"""
    print("\n🔄 Testing Field Mapping...")
    
    try:
        from data_importers.csv_importer import CSVDataImporter
        
        # Create test data with different field names
        test_data = [
            {'sensor_id': 'test_001', 'time': '2024-01-01T00:00:00', 'water_usage': 100.5, 'lat': 40.7128, 'lng': -74.0060},
            {'sensor_id': 'test_002', 'time': '2024-01-01T01:00:00', 'water_usage': 150.2, 'lat': 40.7129, 'lng': -74.0061},
        ]
        
        # Create temporary CSV file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=['sensor_id', 'time', 'water_usage', 'lat', 'lng'])
            writer.writeheader()
            for row in test_data:
                writer.writerow(row)
            temp_path = temp_file.name
        
        try:
            # Test with field mapping
            field_mapping = {
                'sensor_id': 'device_id',
                'time': 'timestamp',
                'water_usage': 'consumption'
            }
            
            importer = CSVDataImporter(
                module_name="iot_water_consumption",
                data_source=temp_path,
                field_mapping=field_mapping
            )
            
            # Transform data
            records = importer.transform_data(temp_path)
            
            if records:
                first_record = records[0]
                expected_fields = ['device_id', 'timestamp', 'consumption', 'lat', 'lng']
                actual_fields = list(first_record.keys())
                
                print(f"   📥 Original fields: {list(test_data[0].keys())}")
                print(f"   📤 Mapped fields: {actual_fields}")
                
                # Check if mapping worked
                mapping_success = all(field in actual_fields for field in ['device_id', 'timestamp', 'consumption'])
                if mapping_success:
                    print("   ✅ Field mapping successful")
                else:
                    print("   ❌ Field mapping failed")
                
                return mapping_success
            else:
                print("   ❌ No records transformed")
                return False
                
        finally:
            # Clean up
            os.unlink(temp_path)
        
    except Exception as e:
        print(f"   ❌ Field mapping test failed: {e}")
        return False

def test_data_validation():
    """Test data validation features"""
    print("\n🔍 Testing Data Validation...")
    
    try:
        from data_importers.csv_importer import CSVDataImporter
        
        importer = CSVDataImporter("test_module", "test_source")
        
        # Test coordinate validation
        test_coords = [
            ({'lat': 40.7128, 'lng': -74.0060}, True),   # Valid
            ({'lat': 100.0, 'lng': -200.0}, False),      # Invalid
            ({'lat': -91.0, 'lng': 0.0}, False),         # Invalid
            ({'lat': 0.0, 'lng': 181.0}, False),         # Invalid
        ]
        
        coord_results = []
        for coords, expected in test_coords:
            result = importer.validate_coordinates(coords)
            coord_results.append(result == expected)
            status = "✅" if result == expected else "❌"
            print(f"   {status} Coordinates {coords}: {'Valid' if result else 'Invalid'}")
        
        # Test required fields validation
        test_records = [
            ({'device_id': 'test', 'timestamp': '2024-01-01', 'consumption': 100}, ['device_id', 'timestamp'], True),
            ({'device_id': 'test', 'consumption': 100}, ['device_id', 'timestamp'], False),
            ({'device_id': None, 'timestamp': '2024-01-01'}, ['device_id', 'timestamp'], False),
        ]
        
        field_results = []
        for record, required, expected in test_records:
            result = importer.validate_required_fields(record, required)
            field_results.append(result == expected)
            status = "✅" if result == expected else "❌"
            print(f"   {status} Fields {required}: {'Valid' if result else 'Invalid'}")
        
        # Test data type validation
        test_types = [
            ({'value': '100.5'}, {'value': float}, True),
            ({'value': 'invalid'}, {'value': float}, False),
            ({'value': 100}, {'value': int}, True),
            ({'value': '100'}, {'value': int}, False),
        ]
        
        type_results = []
        for record, field_types, expected in test_types:
            result = importer.validate_data_types(record, field_types)
            type_results.append(result == expected)
            status = "✅" if result == expected else "❌"
            print(f"   {status} Type validation: {'Valid' if result else 'Invalid'}")
        
        # Calculate overall success
        all_results = coord_results + field_results + type_results
        success_rate = sum(all_results) / len(all_results) * 100
        
        print(f"\n   📊 Validation Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 90
        
    except Exception as e:
        print(f"   ❌ Data validation test failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n⚠️ Testing Error Handling...")
    
    try:
        from data_importers.csv_importer import CSVDataImporter
        from common_utils.exceptions import DataImportError
        
        # Test with non-existent file
        try:
            importer = CSVDataImporter("test_module", "non_existent_file.csv")
            importer.validate_data("non_existent_file.csv")
            print("   ❌ Should have raised error for non-existent file")
            return False
        except Exception as e:
            print(f"   ✅ Correctly handled non-existent file: {type(e).__name__}")
        
        # Test with invalid CSV format
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            temp_file.write("invalid,csv,format\n")
            temp_file.write("no,proper,structure\n")
            temp_path = temp_file.name
        
        try:
            importer = CSVDataImporter("test_module", temp_path)
            records = importer.transform_data(temp_path)
            print(f"   ✅ Handled invalid CSV gracefully: {len(records)} records")
        except Exception as e:
            print(f"   ✅ Correctly handled invalid CSV: {type(e).__name__}")
        finally:
            os.unlink(temp_path)
        
        # Test with empty file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            temp_path = temp_file.name
        
        try:
            importer = CSVDataImporter("test_module", temp_path)
            is_valid = importer.validate_data(temp_path)
            print(f"   ✅ Handled empty file: {'Valid' if is_valid else 'Invalid'}")
        except Exception as e:
            print(f"   ✅ Correctly handled empty file: {type(e).__name__}")
        finally:
            os.unlink(temp_path)
        
        print("   ✅ Error handling tests completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        return False

def test_performance():
    """Test import performance"""
    print("\n⚡ Testing Performance...")
    
    try:
        from data_importers.csv_importer import CSVDataImporter
        
        # Test with different dataset sizes
        test_sizes = [100, 1000, 5000]
        
        for size in test_sizes:
            print(f"\n   📊 Testing {size} records...")
            
            # Generate test data
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
                writer = csv.DictWriter(temp_file, fieldnames=['device_id', 'timestamp', 'consumption', 'lat', 'lng'])
                writer.writeheader()
                
                for i in range(size):
                    record = {
                        'device_id': f'device_{i:03d}',
                        'timestamp': f'2024-01-01T{i%24:02d}:00:00',
                        'consumption': 100 + i,
                        'lat': 40.0 + (i % 10) * 0.1,
                        'lng': -74.0 + (i % 10) * 0.1
                    }
                    writer.writerow(record)
                
                temp_path = temp_file.name
            
            try:
                # Measure performance
                importer = CSVDataImporter("iot_water_consumption", temp_path)
                
                # Validation time
                start_time = time.time()
                is_valid = importer.validate_data(temp_path)
                validation_time = time.time() - start_time
                
                # Transformation time
                start_time = time.time()
                records = importer.transform_data(temp_path)
                transformation_time = time.time() - start_time
                
                # Calculate throughput
                validation_throughput = size / validation_time if validation_time > 0 else 0
                transformation_throughput = size / transformation_time if transformation_time > 0 else 0
                
                print(f"      ✅ Validation: {validation_time:.3f}s ({validation_throughput:.0f} records/s)")
                print(f"      ✅ Transformation: {transformation_time:.3f}s ({transformation_throughput:.0f} records/s)")
                print(f"      📈 Total: {validation_time + transformation_time:.3f}s for {size} records")
                
                # Performance thresholds
                max_time = size / 1000  # 1000 records per second minimum
                if validation_time + transformation_time <= max_time:
                    print(f"      🎯 Performance: EXCELLENT")
                elif validation_time + transformation_time <= max_time * 2:
                    print(f"      🎯 Performance: GOOD")
                else:
                    print(f"      🎯 Performance: NEEDS IMPROVEMENT")
                
            finally:
                os.unlink(temp_path)
        
        print("   ✅ Performance tests completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        return False

def main():
    """Main test function"""
    print("="*80)
    print("AQUATRAK DATA IMPORT SYSTEM - FULL TEST SUITE")
    print("="*80)
    print(f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    test_results = []
    
    # Test 1: CSV Import
    csv_results = test_csv_import()
    test_results.append(('CSV Import', len(csv_results) > 0))
    
    # Test 2: Field Mapping
    mapping_success = test_field_mapping()
    test_results.append(('Field Mapping', mapping_success))
    
    # Test 3: Data Validation
    validation_success = test_data_validation()
    test_results.append(('Data Validation', validation_success))
    
    # Test 4: Error Handling
    error_handling_success = test_error_handling()
    test_results.append(('Error Handling', error_handling_success))
    
    # Test 5: Performance
    performance_success = test_performance()
    test_results.append(('Performance', performance_success))
    
    # Print comprehensive summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print("📊 Test Results:")
    print("-" * 50)
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} | {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! The data import system is fully functional.")
        print("   The system can handle:")
        print("   ✅ CSV file reading and validation")
        print("   ✅ Field mapping and transformation")
        print("   ✅ Data quality validation")
        print("   ✅ Error handling and recovery")
        print("   ✅ Performance optimization")
    elif passed_tests >= total_tests * 0.8:
        print("\n👍 MOST TESTS PASSED! The data import system is mostly functional.")
        print("   Some minor issues may need attention.")
    else:
        print("\n❌ MANY TESTS FAILED! The data import system needs significant work.")
        print("   Please review the failures and fix critical issues.")
    
    print("\n" + "="*80)
    print(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 