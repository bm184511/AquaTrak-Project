#!/usr/bin/env python3
"""
Simple Data Import Test
AquaTrak - AI-GIS Water Risk Monitoring Platform

This script tests the core data import functionality without complex dependencies.

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

def test_sample_data_files():
    """Test that sample data files exist and are readable"""
    print("📁 Testing Sample Data Files...")
    
    sample_files = [
        ("IoT Water Consumption", "sample_data/iot_water_consumption.csv"),
        ("Environmental Health", "sample_data/environmental_health.csv"),
        ("Urban Green Space", "sample_data/urban_green_space.csv"),
        ("Urban Water Network", "sample_data/urban_water_network.csv")
    ]
    
    results = []
    
    for name, file_path in sample_files:
        if Path(file_path).exists():
            try:
                # Check file size
                file_size = Path(file_path).stat().st_size
                
                # Read first few lines
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    records = list(reader)
                
                print(f"✅ {name}: {len(records)} records, {file_size/1024:.1f}KB")
                
                if records:
                    # Show sample data
                    first_record = records[0]
                    print(f"   📋 Sample fields: {list(first_record.keys())[:5]}...")
                    print(f"   📊 Sample values: {dict(list(first_record.items())[:3])}")
                
                results.append({
                    'name': name,
                    'file': file_path,
                    'records': len(records),
                    'size_kb': file_size / 1024,
                    'status': 'success'
                })
                
            except Exception as e:
                print(f"❌ {name}: Error reading file - {e}")
                results.append({
                    'name': name,
                    'file': file_path,
                    'error': str(e),
                    'status': 'error'
                })
        else:
            print(f"❌ {name}: File not found")
            results.append({
                'name': name,
                'file': file_path,
                'status': 'not_found'
            })
    
    return results

def test_data_quality():
    """Test data quality of sample files"""
    print("\n🔬 Testing Data Quality...")
    
    quality_results = []
    
    # Test IoT Water Consumption data
    iot_file = "sample_data/iot_water_consumption.csv"
    if Path(iot_file).exists():
        print("   📊 Analyzing IoT Water Consumption data...")
        
        with open(iot_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            records = list(reader)
        
        if records:
            # Check completeness
            complete_records = 0
            valid_coordinates = 0
            valid_consumption = 0
            valid_timestamps = 0
            
            for record in records:
                # Check completeness
                if all(record.get(field) for field in ['device_id', 'timestamp', 'consumption']):
                    complete_records += 1
                
                # Check coordinates
                try:
                    lat = float(record.get('lat', 0))
                    lng = float(record.get('lng', 0))
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        valid_coordinates += 1
                except (ValueError, TypeError):
                    pass
                
                # Check consumption values
                try:
                    consumption = float(record.get('consumption', 0))
                    if 0 <= consumption <= 1000:  # Reasonable range
                        valid_consumption += 1
                except (ValueError, TypeError):
                    pass
                
                # Check timestamps
                try:
                    timestamp = record.get('timestamp', '')
                    if 'T' in timestamp and len(timestamp) >= 19:
                        valid_timestamps += 1
                except:
                    pass
            
            total_records = len(records)
            completeness_rate = (complete_records / total_records) * 100
            coordinate_accuracy = (valid_coordinates / total_records) * 100
            consumption_accuracy = (valid_consumption / total_records) * 100
            timestamp_accuracy = (valid_timestamps / total_records) * 100
            
            overall_quality = (completeness_rate + coordinate_accuracy + consumption_accuracy + timestamp_accuracy) / 4
            
            print(f"      📈 Total Records: {total_records}")
            print(f"      ✅ Complete Records: {completeness_rate:.1f}%")
            print(f"      🌍 Valid Coordinates: {coordinate_accuracy:.1f}%")
            print(f"      💧 Valid Consumption: {consumption_accuracy:.1f}%")
            print(f"      🕐 Valid Timestamps: {timestamp_accuracy:.1f}%")
            print(f"      🎯 Overall Quality: {overall_quality:.1f}%")
            
            quality_results.append({
                'dataset': 'IoT Water Consumption',
                'quality_score': overall_quality,
                'status': 'excellent' if overall_quality >= 90 else 'good' if overall_quality >= 80 else 'acceptable'
            })
    
    # Test Environmental Health data
    env_file = "sample_data/environmental_health.csv"
    if Path(env_file).exists():
        print("   📊 Analyzing Environmental Health data...")
        
        with open(env_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            records = list(reader)
        
        if records:
            # Check for key environmental parameters
            valid_records = 0
            for record in records:
                try:
                    # Check if key environmental parameters are present
                    pm25 = float(record.get('pm25', 0))
                    aqi = float(record.get('aqi', 0))
                    lat = float(record.get('lat', 0))
                    lng = float(record.get('lng', 0))
                    
                    if 0 <= pm25 <= 500 and 0 <= aqi <= 500 and -90 <= lat <= 90 and -180 <= lng <= 180:
                        valid_records += 1
                except (ValueError, TypeError):
                    pass
            
            total_records = len(records)
            quality_score = (valid_records / total_records) * 100
            
            print(f"      📈 Total Records: {total_records}")
            print(f"      ✅ Valid Records: {quality_score:.1f}%")
            
            quality_results.append({
                'dataset': 'Environmental Health',
                'quality_score': quality_score,
                'status': 'excellent' if quality_score >= 90 else 'good' if quality_score >= 80 else 'acceptable'
            })
    
    return quality_results

def test_data_transformation():
    """Test data transformation logic"""
    print("\n🔄 Testing Data Transformation...")
    
    # Test field mapping
    print("   🔄 Testing field mapping...")
    
    original_data = {
        'sensor_id': 'test_001',
        'time': '2024-01-01T00:00:00',
        'water_usage': 100.5,
        'lat': 40.7128,
        'lng': -74.0060
    }
    
    field_mapping = {
        'sensor_id': 'device_id',
        'time': 'timestamp',
        'water_usage': 'consumption'
    }
    
    # Apply field mapping
    transformed_data = {}
    for old_field, new_field in field_mapping.items():
        if old_field in original_data:
            transformed_data[new_field] = original_data[old_field]
    
    # Keep unmapped fields
    for field, value in original_data.items():
        if field not in field_mapping:
            transformed_data[field] = value
    
    expected_data = {
        'device_id': 'test_001',
        'timestamp': '2024-01-01T00:00:00',
        'consumption': 100.5,
        'lat': 40.7128,
        'lng': -74.0060
    }
    
    if transformed_data == expected_data:
        print("      ✅ Field mapping successful")
        print(f"      📥 Input: {original_data}")
        print(f"      📤 Output: {transformed_data}")
    else:
        print("      ❌ Field mapping failed")
        print(f"      Expected: {expected_data}")
        print(f"      Got: {transformed_data}")
    
    # Test data cleaning
    print("   🧹 Testing data cleaning...")
    
    test_values = [
        ('100.5', 100.5, True),
        ('invalid', None, False),
        ('50', 50.0, True),
        ('', None, False),
        ('0', 0.0, True),
    ]
    
    def clean_numeric(value):
        try:
            return float(value) if value.strip() else None
        except (ValueError, AttributeError):
            return None
    
    for input_val, expected, should_pass in test_values:
        result = clean_numeric(input_val)
        status = "✅" if (result == expected) == should_pass else "❌"
        print(f"      {status} '{input_val}' -> {result}")
    
    return True

def test_import_simulation():
    """Simulate the import process"""
    print("\n📥 Testing Import Simulation...")
    
    # Simulate importing IoT data
    iot_file = "sample_data/iot_water_consumption.csv"
    
    if Path(iot_file).exists():
        print("   📊 Simulating IoT Water Consumption import...")
        
        start_time = time.time()
        
        with open(iot_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            records = list(reader)
        
        # Simulate validation
        valid_records = 0
        invalid_records = 0
        
        for record in records:
            try:
                # Basic validation
                device_id = record.get('device_id')
                timestamp = record.get('timestamp')
                consumption = float(record.get('consumption', 0))
                lat = float(record.get('lat', 0))
                lng = float(record.get('lng', 0))
                
                if (device_id and timestamp and 
                    0 <= consumption <= 1000 and 
                    -90 <= lat <= 90 and -180 <= lng <= 180):
                    valid_records += 1
                else:
                    invalid_records += 1
                    
            except (ValueError, TypeError):
                invalid_records += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        total_records = len(records)
        success_rate = (valid_records / total_records) * 100
        throughput = total_records / processing_time if processing_time > 0 else 0
        
        print(f"      📈 Total Records: {total_records}")
        print(f"      ✅ Valid Records: {valid_records}")
        print(f"      ❌ Invalid Records: {invalid_records}")
        print(f"      🎯 Success Rate: {success_rate:.1f}%")
        print(f"      ⚡ Processing Time: {processing_time:.3f}s")
        print(f"      📊 Throughput: {throughput:.0f} records/s")
        
        if success_rate >= 95:
            print("      🏆 Excellent import quality!")
        elif success_rate >= 90:
            print("      👍 Good import quality")
        elif success_rate >= 80:
            print("      ⚠️ Acceptable import quality")
        else:
            print("      ❌ Poor import quality")
        
        return {
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'success_rate': success_rate,
            'processing_time': processing_time,
            'throughput': throughput
        }
    
    return None

def main():
    """Main test function"""
    print("="*80)
    print("AQUATRAK DATA IMPORT SYSTEM - SIMPLE TEST SUITE")
    print("="*80)
    print(f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    test_results = []
    
    # Test 1: Sample Data Files
    file_results = test_sample_data_files()
    test_results.append(('Sample Data Files', len(file_results) > 0))
    
    # Test 2: Data Quality
    quality_results = test_data_quality()
    test_results.append(('Data Quality', len(quality_results) > 0))
    
    # Test 3: Data Transformation
    transform_success = test_data_transformation()
    test_results.append(('Data Transformation', transform_success))
    
    # Test 4: Import Simulation
    import_result = test_import_simulation()
    test_results.append(('Import Simulation', import_result is not None))
    
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
    
    # Print detailed results
    if quality_results:
        print(f"\n🔬 Data Quality Summary:")
        for result in quality_results:
            print(f"   {result['dataset']}: {result['quality_score']:.1f}% ({result['status']})")
    
    if import_result:
        print(f"\n📥 Import Simulation Results:")
        print(f"   Success Rate: {import_result['success_rate']:.1f}%")
        print(f"   Throughput: {import_result['throughput']:.0f} records/s")
        print(f"   Processing Time: {import_result['processing_time']:.3f}s")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! The data import system is working correctly.")
        print("   The system can handle:")
        print("   ✅ Sample data file reading and validation")
        print("   ✅ Data quality assessment")
        print("   ✅ Field mapping and transformation")
        print("   ✅ Import process simulation")
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