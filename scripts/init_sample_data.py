#!/usr/bin/env python3
"""
Initialize Sample Data Script
AquaTrak - AI-GIS Water Risk Monitoring Platform

This script initializes the database with sample data for testing and development.
"""

import sys
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.database import get_db, init_db
from models.system import User, Organization, Module, AnalysisResult, Alert, Dashboard
from models.modules import IoTWaterData, EnvironmentalHealthData, GreenSpaceData, WaterNetworkData

# Initialize password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_sample_organization(db: Session) -> Organization:
    """Create a sample organization"""
    org = Organization(
        id=uuid.uuid4(),
        name="AquaTrak Demo Organization",
        description="Demo organization for testing and development",
        country="IR",
        industry="Water Management",
        size="medium",
        subscription_plan="enterprise",
        settings={
            "default_language": "en",
            "default_country": "IR",
            "timezone": "Asia/Tehran",
            "data_retention_days": 365,
            "max_users": 50,
            "enabled_modules": [
                "iot_water_consumption",
                "environmental_health",
                "urban_green_space",
                "urban_water_network"
            ]
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def create_sample_users(db: Session, org_id: str) -> list[User]:
    """Create sample users"""
    users = []
    
    # Admin user
    admin_user = User(
        id=uuid.uuid4(),
        email="admin@aquatrak.com",
        username="admin",
        full_name="System Administrator",
        password_hash=pwd_context.hash("admin123"),
        role="admin",
        organization_id=org_id,
        country="IR",
        language="en",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    users.append(admin_user)
    
    # Manager user
    manager_user = User(
        id=uuid.uuid4(),
        email="manager@aquatrak.com",
        username="manager",
        full_name="Project Manager",
        password_hash=pwd_context.hash("manager123"),
        role="manager",
        organization_id=org_id,
        country="IR",
        language="en",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    users.append(manager_user)
    
    # Analyst user
    analyst_user = User(
        id=uuid.uuid4(),
        email="analyst@aquatrak.com",
        username="analyst",
        full_name="Data Analyst",
        password_hash=pwd_context.hash("analyst123"),
        role="analyst",
        organization_id=org_id,
        country="IR",
        language="en",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    users.append(analyst_user)
    
    # Viewer user
    viewer_user = User(
        id=uuid.uuid4(),
        email="viewer@aquatrak.com",
        username="viewer",
        full_name="Data Viewer",
        password_hash=pwd_context.hash("viewer123"),
        role="viewer",
        organization_id=org_id,
        country="IR",
        language="en",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    users.append(viewer_user)
    
    for user in users:
        db.add(user)
    db.commit()
    
    return users

def create_sample_modules(db: Session) -> list[Module]:
    """Create sample modules"""
    modules = []
    
    module_data = [
        {
            "name": "IoT Water Consumption",
            "description": "Real-time monitoring and analysis of water consumption using IoT sensors",
            "category": "iot_monitoring",
            "status": "active",
            "version": "1.0.0"
        },
        {
            "name": "Environmental Health",
            "description": "Comprehensive environmental health monitoring and risk assessment",
            "category": "environmental_health",
            "status": "active",
            "version": "1.0.0"
        },
        {
            "name": "Urban Green Space",
            "description": "Analysis of urban green spaces and ecosystem services",
            "category": "green_space",
            "status": "active",
            "version": "1.0.0"
        },
        {
            "name": "Urban Water Network",
            "description": "Monitoring and optimization of urban water distribution networks",
            "category": "urban_planning",
            "status": "active",
            "version": "1.0.0"
        },
        {
            "name": "Drought Prediction",
            "description": "AI-powered drought prediction and early warning system",
            "category": "drought_prediction",
            "status": "active",
            "version": "1.0.0"
        },
        {
            "name": "Flood Modeling",
            "description": "Urban flood modeling and risk assessment",
            "category": "flood_modeling",
            "status": "active",
            "version": "1.0.0"
        },
        {
            "name": "Groundwater Pollution",
            "description": "Groundwater quality monitoring and pollution detection",
            "category": "groundwater",
            "status": "active",
            "version": "1.0.0"
        },
        {
            "name": "Water Quality",
            "description": "Drinking water quality monitoring and analysis",
            "category": "water_quality",
            "status": "active",
            "version": "1.0.0"
        }
    ]
    
    for data in module_data:
        module = Module(
            id=uuid.uuid4(),
            name=data["name"],
            description=data["description"],
            category=data["category"],
            status=data["status"],
            version=data["version"],
            config={
                "enabled": True,
                "parameters": {},
                "data_sources": ["sensor_data", "satellite_data"],
                "update_frequency": 3600
            },
            last_updated=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        modules.append(module)
        db.add(module)
    
    db.commit()
    return modules

def create_sample_analysis_results(db: Session, modules: list[Module], users: list[User]) -> list[AnalysisResult]:
    """Create sample analysis results"""
    results = []
    
    for i, module in enumerate(modules[:4]):  # Create results for first 4 modules
        for j in range(3):  # 3 results per module
            result = AnalysisResult(
                id=uuid.uuid4(),
                module_id=module.id,
                module_name=module.name,
                analysis_type="comprehensive",
                status="completed" if j < 2 else "running",
                parameters={
                    "time_range": "30d",
                    "location": "Tehran, Iran",
                    "data_sources": ["sensor_data", "satellite_data"]
                },
                results={
                    "efficiency_score": 85.5 + j * 2,
                    "anomalies_detected": 3 + j,
                    "recommendations": [
                        "Optimize water distribution",
                        "Implement leak detection",
                        "Upgrade monitoring systems"
                    ]
                },
                metadata={
                    "data_sources": ["sensor_data", "satellite_data"],
                    "processing_time": 120 + j * 30,
                    "data_points": 10000 + j * 5000,
                    "geographic_scope": {
                        "country": "IR",
                        "region": "Tehran",
                        "city": "Tehran"
                    },
                    "confidence_score": 0.92 - j * 0.05,
                    "model_version": "1.0.0"
                },
                user_id=users[j % len(users)].id,
                created_at=datetime.utcnow() - timedelta(days=j),
                updated_at=datetime.utcnow() - timedelta(hours=j),
                completed_at=datetime.utcnow() - timedelta(hours=j) if j < 2 else None
            )
            results.append(result)
            db.add(result)
    
    db.commit()
    return results

def create_sample_alerts(db: Session, modules: list[Module], users: list[User]) -> list[Alert]:
    """Create sample alerts"""
    alerts = []
    
    alert_data = [
        {
            "type": "anomaly_detected",
            "severity": "critical",
            "title": "High Water Consumption Detected",
            "message": "Water consumption exceeded normal levels by 150% in Zone A"
        },
        {
            "type": "threshold_exceeded",
            "severity": "warning",
            "title": "Water Quality Alert",
            "message": "Turbidity levels exceeded safety threshold"
        },
        {
            "type": "maintenance_required",
            "severity": "info",
            "title": "Sensor Maintenance Due",
            "message": "IoT sensor maintenance scheduled for next week"
        },
        {
            "type": "system_error",
            "severity": "error",
            "title": "Data Processing Error",
            "message": "Failed to process environmental health data"
        }
    ]
    
    for i, data in enumerate(alert_data):
        alert = Alert(
            id=uuid.uuid4(),
            type=data["type"],
            severity=data["severity"],
            title=data["title"],
            message=data["message"],
            module_id=modules[i % len(modules)].id if i < len(modules) else None,
            location={
                "lat": 35.6892 + (i * 0.01),
                "lng": 51.3890 + (i * 0.01)
            },
            metadata={
                "zone": f"Zone {chr(65 + i)}",
                "affected_devices": i + 1
            },
            user_id=users[i % len(users)].id,
            status="active" if i < 2 else "acknowledged",
            created_at=datetime.utcnow() - timedelta(hours=i * 2),
            acknowledged_at=datetime.utcnow() - timedelta(hours=i) if i >= 2 else None
        )
        alerts.append(alert)
        db.add(alert)
    
    db.commit()
    return alerts

def create_sample_dashboards(db: Session, users: list[User]) -> list[Dashboard]:
    """Create sample dashboards"""
    dashboards = []
    
    dashboard_data = [
        {
            "name": "Main Dashboard",
            "description": "Overview of all water monitoring systems",
            "is_public": True
        },
        {
            "name": "IoT Monitoring",
            "description": "Real-time IoT sensor data and analytics",
            "is_public": False
        },
        {
            "name": "Environmental Health",
            "description": "Environmental health indicators and trends",
            "is_public": False
        }
    ]
    
    for i, data in enumerate(dashboard_data):
        dashboard = Dashboard(
            id=uuid.uuid4(),
            name=data["name"],
            description=data["description"],
            user_id=users[i % len(users)].id,
            is_public=data["is_public"],
            widgets=[
                {
                    "id": f"widget_{i}_{j}",
                    "type": "chart" if j % 2 == 0 else "metric",
                    "title": f"Widget {j + 1}",
                    "config": {
                        "chart_type": "line" if j % 2 == 0 else None,
                        "metrics": ["consumption", "efficiency"]
                    },
                    "data_source": f"module_{i}",
                    "refresh_interval": 300
                }
                for j in range(3)
            ],
            layout=[
                {
                    "widget_id": f"widget_{i}_{j}",
                    "x": j * 4,
                    "y": 0,
                    "width": 4,
                    "height": 3
                }
                for j in range(3)
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        dashboards.append(dashboard)
        db.add(dashboard)
    
    db.commit()
    return dashboards

def create_sample_module_data(db: Session) -> None:
    """Create sample data for specific modules"""
    
    # IoT Water Data
    for i in range(50):
        iot_data = IoTWaterData(
            id=uuid.uuid4(),
            device_id=f"device_{i % 5 + 1}",
            timestamp=datetime.utcnow() - timedelta(hours=i),
            consumption=100 + (i % 20) * 10,
            flow_rate=2.5 + (i % 10) * 0.5,
            pressure=3.2 + (i % 8) * 0.3,
            temperature=20 + (i % 15),
            quality_metrics={
                "ph": 7.0 + (i % 10) * 0.1,
                "turbidity": 1.0 + (i % 5) * 0.5,
                "conductivity": 500 + (i % 100) * 10,
                "dissolved_oxygen": 8.0 + (i % 4) * 0.5,
                "temperature": 20 + (i % 15)
            },
            location={
                "lat": 35.6892 + (i % 10) * 0.01,
                "lng": 51.3890 + (i % 10) * 0.01
            },
            created_at=datetime.utcnow() - timedelta(hours=i)
        )
        db.add(iot_data)
    
    # Environmental Health Data
    for i in range(30):
        env_data = EnvironmentalHealthData(
            id=uuid.uuid4(),
            location={
                "lat": 35.6892 + (i % 10) * 0.01,
                "lng": 51.3890 + (i % 10) * 0.01,
                "address": f"Location {i + 1}, Tehran, Iran"
            },
            timestamp=datetime.utcnow() - timedelta(days=i),
            air_quality={
                "pm25": 15 + (i % 20),
                "pm10": 30 + (i % 30),
                "no2": 20 + (i % 15),
                "o3": 40 + (i % 25),
                "co": 1.0 + (i % 5) * 0.2,
                "so2": 5 + (i % 10),
                "aqi": 50 + (i % 100)
            },
            water_quality={
                "ph": 7.0 + (i % 10) * 0.1,
                "turbidity": 1.0 + (i % 5) * 0.5,
                "conductivity": 500 + (i % 100) * 10,
                "dissolved_oxygen": 8.0 + (i % 4) * 0.5,
                "temperature": 20 + (i % 15)
            },
            soil_quality={
                "ph": 6.5 + (i % 10) * 0.2,
                "organic_matter": 2.0 + (i % 5) * 0.5,
                "nitrogen": 0.1 + (i % 10) * 0.02,
                "phosphorus": 0.05 + (i % 10) * 0.01,
                "potassium": 0.2 + (i % 10) * 0.05,
                "heavy_metals": {
                    "lead": 0.01 + (i % 10) * 0.005,
                    "cadmium": 0.001 + (i % 10) * 0.0005,
                    "mercury": 0.0001 + (i % 10) * 0.00005,
                    "arsenic": 0.005 + (i % 10) * 0.002,
                    "chromium": 0.02 + (i % 10) * 0.01
                }
            },
            noise_levels={
                "day_level": 60 + (i % 20),
                "night_level": 45 + (i % 15),
                "peak_level": 80 + (i % 30),
                "equivalent_level": 65 + (i % 20)
            },
            environmental_indicators={
                "biodiversity_index": 0.7 + (i % 10) * 0.03,
                "green_coverage": 25 + (i % 20),
                "air_pollution_index": 50 + (i % 50),
                "water_pollution_index": 30 + (i % 40),
                "soil_contamination_index": 20 + (i % 30),
                "overall_health_score": 75 + (i % 20)
            },
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        db.add(env_data)
    
    db.commit()

def main():
    """Main function to initialize sample data"""
    print("🚀 Initializing AquaTrak database with sample data...")
    
    try:
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Get database session
        db = next(get_db())
        
        # Create sample data
        print("📊 Creating sample organization...")
        org = create_sample_organization(db)
        print(f"✅ Created organization: {org.name}")
        
        print("👥 Creating sample users...")
        users = create_sample_users(db, str(org.id))
        print(f"✅ Created {len(users)} users")
        
        print("🔧 Creating sample modules...")
        modules = create_sample_modules(db)
        print(f"✅ Created {len(modules)} modules")
        
        print("📈 Creating sample analysis results...")
        results = create_sample_analysis_results(db, modules, users)
        print(f"✅ Created {len(results)} analysis results")
        
        print("🚨 Creating sample alerts...")
        alerts = create_sample_alerts(db, modules, users)
        print(f"✅ Created {len(alerts)} alerts")
        
        print("📊 Creating sample dashboards...")
        dashboards = create_sample_dashboards(db, users)
        print(f"✅ Created {len(dashboards)} dashboards")
        
        print("📊 Creating sample module data...")
        create_sample_module_data(db)
        print("✅ Created sample module data")
        
        print("\n🎉 Sample data initialization completed successfully!")
        print("\n📋 Sample User Credentials:")
        print("  Admin: admin@aquatrak.com / admin123")
        print("  Manager: manager@aquatrak.com / manager123")
        print("  Analyst: analyst@aquatrak.com / analyst123")
        print("  Viewer: viewer@aquatrak.com / viewer123")
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main() 