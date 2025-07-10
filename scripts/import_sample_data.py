#!/usr/bin/env python3
"""
Sample Data Import Script
AquaTrak - AI-GIS Water Risk Monitoring Platform

This script imports sample data for all modules to populate the database
with realistic test data for development and testing.

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import random
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_importers.manager import DataImportManager
from data_importers.csv_importer import CSVDataImporter
from data_importers.api_importer import APIDataImporter
from data_importers.satellite_importer import SatelliteDataImporter
from common_utils.exceptions import DataImportError
from config.database import init_database
from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_iot_water_data(num_records: int = 1000) -> list:
    """Generate sample IoT water consumption data"""
    data = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_records):
        timestamp = base_time + timedelta(hours=i)
        
        # Generate realistic water consumption patterns
        hour = timestamp.hour
        if 6 <= hour <= 9:  # Morning peak
            consumption = random.uniform(50, 150)
        elif 18 <= hour <= 22:  # Evening peak
            consumption = random.uniform(60, 180)
        else:  # Off-peak
            consumption = random.uniform(10, 40)
        
        # Add some anomalies
        if random.random() < 0.05:  # 5% chance of anomaly
            consumption *= random.uniform(2, 5)
        
        record = {
            'device_id': f"iot_device_{random.randint(1, 50):03d}",
            'timestamp': timestamp.isoformat(),
            'consumption': round(consumption, 2),
            'flow_rate': round(random.uniform(0.5, 5.0), 2),
            'pressure': round(random.uniform(2.0, 8.0), 2),
            'temperature': round(random.uniform(15, 25), 1),
            'ph': round(random.uniform(6.5, 8.5), 2),
            'turbidity': round(random.uniform(0, 5), 2),
            'conductivity': round(random.uniform(200, 800), 0),
            'dissolved_oxygen': round(random.uniform(6, 12), 1),
            'lat': round(random.uniform(25.0, 50.0), 6),
            'lng': round(random.uniform(-120.0, -70.0), 6)
        }
        data.append(record)
    
    return data

def generate_environmental_health_data(num_records: int = 500) -> list:
    """Generate sample environmental health data"""
    data = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_records):
        timestamp = base_time + timedelta(hours=i*2)
        
        # Generate realistic environmental data
        record = {
            'timestamp': timestamp.isoformat(),
            'lat': round(random.uniform(25.0, 50.0), 6),
            'lng': round(random.uniform(-120.0, -70.0), 6),
            'address': f"Sample Location {random.randint(1, 100)}",
            'pm25': round(random.uniform(5, 35), 1),
            'pm10': round(random.uniform(10, 60), 1),
            'no2': round(random.uniform(10, 50), 1),
            'o3': round(random.uniform(20, 80), 1),
            'co': round(random.uniform(0.5, 3.0), 2),
            'so2': round(random.uniform(2, 15), 1),
            'aqi': round(random.uniform(20, 100), 0),
            'ph': round(random.uniform(6.5, 8.5), 2),
            'turbidity': round(random.uniform(0, 5), 2),
            'conductivity': round(random.uniform(200, 800), 0),
            'dissolved_oxygen': round(random.uniform(6, 12), 1),
            'temperature': round(random.uniform(15, 25), 1),
            'soil_ph': round(random.uniform(6.0, 7.5), 2),
            'organic_matter': round(random.uniform(1, 5), 2),
            'nitrogen': round(random.uniform(10, 50), 1),
            'phosphorus': round(random.uniform(5, 25), 1),
            'potassium': round(random.uniform(50, 200), 1),
            'lead': round(random.uniform(0, 10), 2),
            'cadmium': round(random.uniform(0, 2), 2),
            'mercury': round(random.uniform(0, 1), 2),
            'arsenic': round(random.uniform(0, 5), 2),
            'chromium': round(random.uniform(0, 15), 2),
            'day_noise': round(random.uniform(45, 65), 1),
            'night_noise': round(random.uniform(35, 55), 1),
            'peak_noise': round(random.uniform(60, 80), 1),
            'equivalent_noise': round(random.uniform(50, 70), 1),
            'biodiversity_index': round(random.uniform(0.3, 0.8), 2),
            'green_coverage': round(random.uniform(10, 40), 1),
            'air_pollution_index': round(random.uniform(20, 80), 1),
            'water_pollution_index': round(random.uniform(10, 60), 1),
            'soil_contamination_index': round(random.uniform(5, 40), 1),
            'overall_health_score': round(random.uniform(50, 90), 1)
        }
        data.append(record)
    
    return data

def generate_green_space_data(num_records: int = 200) -> list:
    """Generate sample urban green space data"""
    data = []
    
    green_space_types = ['park', 'garden', 'forest', 'wetland', 'community_garden', 'rooftop_garden']
    
    for i in range(num_records):
        green_type = random.choice(green_space_types)
        
        record = {
            'green_space_type': green_type,
            'lat': round(random.uniform(25.0, 50.0), 6),
            'lng': round(random.uniform(-120.0, -70.0), 6),
            'area': round(random.uniform(1, 100), 2),
            'tree_density': round(random.uniform(10, 200), 1),
            'canopy_cover': round(random.uniform(20, 80), 1),
            'species_diversity': round(random.uniform(5, 50), 1),
            'vegetation_health': round(random.uniform(60, 95), 1),
            'carbon_sequestration': round(random.uniform(100, 1000), 1),
            'air_purification': round(random.uniform(50, 200), 1),
            'water_filtration': round(random.uniform(20, 100), 1),
            'temperature_regulation': round(random.uniform(1, 5), 2),
            'biodiversity_support': round(random.uniform(0.3, 0.9), 2),
            'recreational_value': round(random.uniform(0.5, 1.0), 2),
            'walking_distance': round(random.uniform(100, 2000), 0),
            'public_transport': random.choice([True, False]),
            'parking_available': random.choice([True, False]),
            'wheelchair_accessible': random.choice([True, False]),
            'opening_hours': '06:00-22:00',
            'visitor_capacity': random.randint(50, 1000),
            'overall_condition': random.choice(['excellent', 'good', 'fair', 'poor']),
            'last_maintenance': (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat(),
            'next_maintenance': (datetime.utcnow() + timedelta(days=random.randint(30, 180))).isoformat(),
            'budget_allocated': round(random.uniform(1000, 50000), 2)
        }
        data.append(record)
    
    return data

def generate_water_network_data(num_records: int = 800) -> list:
    """Generate sample urban water network data"""
    data = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_records):
        timestamp = base_time + timedelta(hours=i)
        
        record = {
            'network_id': f"network_{random.randint(1, 20):03d}",
            'timestamp': timestamp.isoformat(),
            'pressure': round(random.uniform(3.0, 7.0), 2),
            'flow_rate': round(random.uniform(10, 100), 2),
            'lat': round(random.uniform(25.0, 50.0), 6),
            'lng': round(random.uniform(-120.0, -70.0), 6),
            'ph': round(random.uniform(6.5, 8.5), 2),
            'turbidity': round(random.uniform(0, 5), 2),
            'conductivity': round(random.uniform(200, 800), 0),
            'dissolved_oxygen': round(random.uniform(6, 12), 1),
            'temperature': round(random.uniform(15, 25), 1),
            'pipe_condition': random.choice(['excellent', 'good', 'fair', 'poor']),
            'age_years': random.randint(5, 50),
            'material': random.choice(['PVC', 'HDPE', 'cast_iron', 'steel', 'concrete']),
            'diameter': round(random.uniform(100, 600), 0),
            'last_inspection': (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat(),
            'efficiency_score': round(random.uniform(70, 95), 1),
            'reliability_index': round(random.uniform(0.8, 0.99), 3),
            'water_loss_percentage': round(random.uniform(5, 25), 1),
            'customer_satisfaction': round(random.uniform(70, 95), 1),
            'response_time_minutes': round(random.uniform(15, 120), 0)
        }
        data.append(record)
    
    return data

def save_data_to_csv(data: list, filename: str):
    """Save data to CSV file"""
    if not data:
        return
    
    import csv
    
    filepath = Path("sample_data") / filename
    filepath.parent.mkdir(exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    
    logger.info(f"Saved {len(data)} records to {filepath}")

def import_sample_data():
    """Import sample data for all modules"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Initialize import manager
        manager = DataImportManager()
        
        # Generate and save sample data
        logger.info("Generating sample data...")
        
        # IoT Water Consumption
        iot_data = generate_iot_water_data(1000)
        save_data_to_csv(iot_data, "iot_water_consumption.csv")
        
        # Environmental Health
        env_data = generate_environmental_health_data(500)
        save_data_to_csv(env_data, "environmental_health.csv")
        
        # Urban Green Space
        green_data = generate_green_space_data(200)
        save_data_to_csv(green_data, "urban_green_space.csv")
        
        # Urban Water Network
        network_data = generate_water_network_data(800)
        save_data_to_csv(network_data, "urban_water_network.csv")
        
        # Import data using the manager
        logger.info("Importing sample data...")
        
        import_tasks = [
            {
                'type': 'csv',
                'module_name': 'iot_water_consumption',
                'data_source': 'sample_data/iot_water_consumption.csv',
                'options': {}
            },
            {
                'type': 'csv',
                'module_name': 'environmental_health',
                'data_source': 'sample_data/environmental_health.csv',
                'options': {}
            },
            {
                'type': 'csv',
                'module_name': 'urban_green_space',
                'data_source': 'sample_data/urban_green_space.csv',
                'options': {}
            },
            {
                'type': 'csv',
                'module_name': 'urban_water_network',
                'data_source': 'sample_data/urban_water_network.csv',
                'options': {}
            }
        ]
        
        # Execute batch import
        results = manager.batch_import(import_tasks)
        
        # Log results
        logger.info("Sample data import completed!")
        logger.info(f"Total tasks: {results['total_tasks']}")
        logger.info(f"Completed: {results['completed_tasks']}")
        logger.info(f"Failed: {results['failed_tasks']}")
        
        # Print detailed results
        for result in results['results']:
            if result['status'] == 'success':
                summary = result['result']
                logger.info(f"✓ {summary['module_name']}: {summary['imported_records']} records imported")
            else:
                logger.error(f"✗ {result['task']['module_name']}: {result['error']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Sample data import failed: {e}")
        raise

def main():
    """Main function"""
    try:
        logger.info("Starting sample data import...")
        results = import_sample_data()
        logger.info("Sample data import completed successfully!")
        
        # Print summary
        print("\n" + "="*50)
        print("SAMPLE DATA IMPORT SUMMARY")
        print("="*50)
        print(f"Total tasks: {results['total_tasks']}")
        print(f"Successful: {results['completed_tasks']}")
        print(f"Failed: {results['failed_tasks']}")
        print(f"Duration: {results['end_time'] - results['start_time']}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Sample data import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 