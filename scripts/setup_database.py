#!/usr/bin/env python3
"""
Database setup script for AquaTrak
Creates all tables and initial data
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.database import engine, init_db, get_db_context
from config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Set up the complete database"""
    try:
        logger.info("Starting database setup...")
        
        # Check database connection
        logger.info("Checking database connection...")
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        
        # Initialize database tables
        logger.info("Creating database tables...")
        init_db()
        logger.info("Database tables created successfully")
        
        # Insert initial data
        logger.info("Inserting initial data...")
        insert_initial_data()
        logger.info("Initial data inserted successfully")
        
        logger.info("Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def insert_initial_data():
    """Insert initial data into the database"""
    with get_db_context() as db:
        # Insert default admin user if not exists
        from models.system import User, Organization, UserOrganization, DataSource
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@aquatrak.com',
                hashed_password='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G',  # admin123
                full_name='Administrator',
                roles=['admin'],
                country_code='IR',
                language='en'
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user created")
        
        # Insert default organization if not exists
        org = db.query(Organization).filter(Organization.name == 'AquaTrak Organization').first()
        if not org:
            org = Organization(
                name='AquaTrak Organization',
                type='government',
                country_code='IR',
                contact_email='contact@aquatrak.com',
                subscription_plan='premium'
            )
            db.add(org)
            db.commit()
            logger.info("Default organization created")
        
        # Link admin to organization if not exists
        user_org = db.query(UserOrganization).filter(
            UserOrganization.user_id == admin_user.id,
            UserOrganization.organization_id == org.id
        ).first()
        
        if not user_org:
            user_org = UserOrganization(
                user_id=admin_user.id,
                organization_id=org.id,
                role='admin'
            )
            db.add(user_org)
            db.commit()
            logger.info("Admin linked to organization")
        
        # Insert default data sources
        data_sources = [
            {'name': 'NOAA', 'type': 'weather', 'url': 'https://api.weather.gov'},
            {'name': 'Copernicus', 'type': 'satellite', 'url': 'https://scihub.copernicus.eu'},
            {'name': 'ECMWF', 'type': 'forecast', 'url': 'https://api.ecmwf.int'},
            {'name': 'USGS', 'type': 'hydrology', 'url': 'https://waterdata.usgs.gov'},
            {'name': 'NASA', 'type': 'satellite', 'url': 'https://earthdata.nasa.gov'}
        ]
        
        for source_data in data_sources:
            existing = db.query(DataSource).filter(DataSource.name == source_data['name']).first()
            if not existing:
                source = DataSource(**source_data, status='active')
                db.add(source)
        
        db.commit()
        logger.info("Default data sources created")

def main():
    """Main function"""
    settings = get_settings()
    
    print("=" * 60)
    print("AquaTrak Database Setup")
    print("=" * 60)
    print(f"Database URL: {settings.database_url or 'Using individual settings'}")
    print(f"Database Host: {settings.db_host}")
    print(f"Database Name: {settings.db_name}")
    print(f"Database User: {settings.db_user}")
    print("=" * 60)
    
    # Confirm setup
    response = input("Do you want to proceed with database setup? (y/N): ")
    if response.lower() != 'y':
        print("Database setup cancelled.")
        return
    
    # Run setup
    success = setup_database()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("\nDefault credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("Email: admin@aquatrak.com")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 