#!/usr/bin/env python3
"""
Test Runner for AquaTrak Data Import System
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import sys
import time
import unittest
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_all_tests():
    """Run all test suites"""
    print("="*80)
    print("AQUATRAK DATA IMPORT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results summary
    test_results = {
        'unit_tests': {'run': 0, 'passed': 0, 'failed': 0, 'errors': 0},
        'api_tests': {'run': 0, 'passed': 0, 'failed': 0, 'errors': 0},
        'performance_tests': {'run': 0, 'passed': 0, 'failed': 0, 'errors': 0}
    }
    
    total_start_time = time.time()
    
    # 1. Run Unit Tests
    print("🧪 RUNNING UNIT TESTS")
    print("-" * 40)
    
    try:
        from tests.test_data_import import TestDataImportSystem
        unit_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataImportSystem)
        unit_runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        unit_result = unit_runner.run(unit_suite)
        
        test_results['unit_tests']['run'] = unit_result.testsRun
        test_results['unit_tests']['failed'] = len(unit_result.failures)
        test_results['unit_tests']['errors'] = len(unit_result.errors)
        test_results['unit_tests']['passed'] = unit_result.testsRun - len(unit_result.failures) - len(unit_result.errors)
        
        print(f"✓ Unit tests completed: {test_results['unit_tests']['passed']}/{test_results['unit_tests']['run']} passed")
        
    except Exception as e:
        print(f"✗ Unit tests failed to run: {e}")
        test_results['unit_tests']['errors'] = 1
    
    print()
    
    # 2. Run API Tests
    print("🌐 RUNNING API TESTS")
    print("-" * 40)
    
    try:
        from tests.test_api_endpoints import TestDataImportAPI
        api_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataImportAPI)
        api_runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        api_result = api_runner.run(api_suite)
        
        test_results['api_tests']['run'] = api_result.testsRun
        test_results['api_tests']['failed'] = len(api_result.failures)
        test_results['api_tests']['errors'] = len(api_result.errors)
        test_results['api_tests']['passed'] = api_result.testsRun - len(api_result.failures) - len(api_result.errors)
        
        print(f"✓ API tests completed: {test_results['api_tests']['passed']}/{test_results['api_tests']['run']} passed")
        
    except Exception as e:
        print(f"✗ API tests failed to run: {e}")
        test_results['api_tests']['errors'] = 1
    
    print()
    
    # 3. Run Performance Tests
    print("⚡ RUNNING PERFORMANCE TESTS")
    print("-" * 40)
    
    try:
        from tests.test_performance import TestDataImportPerformance
        perf_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataImportPerformance)
        perf_runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        perf_result = perf_runner.run(perf_suite)
        
        test_results['performance_tests']['run'] = perf_result.testsRun
        test_results['performance_tests']['failed'] = len(perf_result.failures)
        test_results['performance_tests']['errors'] = len(perf_result.errors)
        test_results['performance_tests']['passed'] = perf_result.testsRun - len(perf_result.failures) - len(perf_result.errors)
        
        print(f"✓ Performance tests completed: {test_results['performance_tests']['passed']}/{test_results['performance_tests']['run']} passed")
        
    except Exception as e:
        print(f"✗ Performance tests failed to run: {e}")
        test_results['performance_tests']['errors'] = 1
    
    print()
    
    # Calculate totals
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    total_tests = sum(result['run'] for result in test_results.values())
    total_passed = sum(result['passed'] for result in test_results.values())
    total_failed = sum(result['failed'] for result in test_results.values())
    total_errors = sum(result['errors'] for result in test_results.values())
    
    # Print comprehensive summary
    print("="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    print(f"Total execution time: {total_duration:.2f} seconds")
    print()
    
    print("📊 TEST RESULTS BY CATEGORY:")
    print("-" * 40)
    
    for category, results in test_results.items():
        category_name = category.replace('_', ' ').title()
        if results['run'] > 0:
            success_rate = (results['passed'] / results['run']) * 100
            status = "✅ PASSED" if results['failed'] == 0 and results['errors'] == 0 else "❌ FAILED"
            print(f"{category_name:20} | {results['passed']:3d}/{results['run']:3d} passed | {success_rate:5.1f}% | {status}")
        else:
            print(f"{category_name:20} | {'N/A':>7} | {'N/A':>6} | ❌ ERROR")
    
    print()
    print("📈 OVERALL STATISTICS:")
    print("-" * 40)
    print(f"Total Tests Run:     {total_tests}")
    print(f"Tests Passed:        {total_passed}")
    print(f"Tests Failed:        {total_failed}")
    print(f"Test Errors:         {total_errors}")
    
    if total_tests > 0:
        overall_success_rate = (total_passed / total_tests) * 100
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
    else:
        overall_success_rate = 0
        print("Overall Success Rate: N/A")
    
    print()
    
    # Determine overall status
    if total_failed == 0 and total_errors == 0 and total_tests > 0:
        print("🎉 ALL TESTS PASSED! The data import system is working correctly.")
        overall_status = "SUCCESS"
    elif total_passed > 0:
        print("⚠️  SOME TESTS FAILED. Please review the failures and fix issues.")
        overall_status = "PARTIAL_SUCCESS"
    else:
        print("❌ ALL TESTS FAILED. The data import system has critical issues.")
        overall_status = "FAILURE"
    
    print()
    print("="*80)
    print(f"TEST EXECUTION COMPLETED AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return overall_status == "SUCCESS"

def run_specific_test_category(category):
    """Run a specific test category"""
    categories = {
        'unit': 'tests.test_data_import.TestDataImportSystem',
        'api': 'tests.test_api_endpoints.TestDataImportAPI',
        'performance': 'tests.test_performance.TestDataImportPerformance'
    }
    
    if category not in categories:
        print(f"Unknown test category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return False
    
    print(f"Running {category} tests...")
    
    try:
        # Import and run the specific test
        module_name, class_name = categories[category].rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        test_class = getattr(module, class_name)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Failed to run {category} tests: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        success = run_specific_test_category(category)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 