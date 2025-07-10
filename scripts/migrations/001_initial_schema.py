"""
Initial database migration for AquaTrak
Migration: 001_initial_schema
Description: Create all tables and initial data
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade database to this revision"""
    
    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    
    # ============================================================================
    # CORE SYSTEM TABLES
    # ============================================================================
    
    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('roles', postgresql.ARRAY(sa.String), default=['user']),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('country_code', sa.String(2)),
        sa.Column('language', sa.String(5), default='en'),
        sa.Column('organization', sa.String(255)),
        sa.Column('phone', sa.String(20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Organizations table
    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50)),
        sa.Column('country_code', sa.String(2)),
        sa.Column('address', sa.Text),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('contact_phone', sa.String(20)),
        sa.Column('subscription_plan', sa.String(50), default='basic'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # User organizations table
    op.create_table('user_organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(50), default='member'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'organization_id')
    )
    
    # ============================================================================
    # MODULE TABLES
    # ============================================================================
    
    # InSAR Subsidence tables
    op.create_table('insar_subsidence_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('satellite_source', sa.String(50)),
        sa.Column('acquisition_date', sa.Date, nullable=False),
        sa.Column('interferogram_path', sa.String(500)),
        sa.Column('coherence_threshold', sa.Float, default=0.3),
        sa.Column('deformation_rate', sa.Float),
        sa.Column('uncertainty', sa.Float),
        sa.Column('geometry', sa.Text),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('insar_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('subsidence_rate', sa.Float),
        sa.Column('risk_level', sa.String(20)),
        sa.Column('affected_area_km2', sa.Float),
        sa.Column('population_at_risk', sa.Integer),
        sa.Column('infrastructure_risk', postgresql.JSONB),
        sa.Column('recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Urban Flood Modeling tables
    op.create_table('flood_modeling_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('rainfall_intensity', sa.Float),
        sa.Column('duration_hours', sa.Float),
        sa.Column('return_period', sa.Integer),
        sa.Column('elevation_data_path', sa.String(500)),
        sa.Column('land_use_data', postgresql.JSONB),
        sa.Column('soil_type_data', postgresql.JSONB),
        sa.Column('drainage_network', postgresql.JSONB),
        sa.Column('geometry', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('flood_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('flood_depth_max', sa.Float),
        sa.Column('flood_extent_km2', sa.Float),
        sa.Column('affected_population', sa.Integer),
        sa.Column('infrastructure_damage_estimate', sa.Float),
        sa.Column('evacuation_required', sa.Boolean),
        sa.Column('risk_zones', postgresql.JSONB),
        sa.Column('mitigation_measures', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Groundwater Pollution tables
    op.create_table('groundwater_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('well_id', sa.String(100), nullable=False),
        sa.Column('sampling_date', sa.Date, nullable=False),
        sa.Column('depth_m', sa.Float),
        sa.Column('ph', sa.Float),
        sa.Column('conductivity', sa.Float),
        sa.Column('temperature', sa.Float),
        sa.Column('dissolved_oxygen', sa.Float),
        sa.Column('turbidity', sa.Float),
        sa.Column('contaminants', postgresql.JSONB),
        sa.Column('location', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('groundwater_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('aquifer_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('pollution_index', sa.Float),
        sa.Column('risk_level', sa.String(20)),
        sa.Column('affected_area_km2', sa.Float),
        sa.Column('contaminant_sources', postgresql.JSONB),
        sa.Column('remediation_priority', postgresql.ARRAY(sa.String)),
        sa.Column('monitoring_recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # IoT Water Consumption tables
    op.create_table('iot_sensor_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('sensor_id', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('flow_rate', sa.Float),
        sa.Column('pressure', sa.Float),
        sa.Column('temperature', sa.Float),
        sa.Column('conductivity', sa.Float),
        sa.Column('ph', sa.Float),
        sa.Column('location', sa.Text),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('iot_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('facility_id', sa.String(100), nullable=False),
        sa.Column('analysis_period_start', sa.DateTime(timezone=True)),
        sa.Column('analysis_period_end', sa.DateTime(timezone=True)),
        sa.Column('total_consumption', sa.Float),
        sa.Column('average_flow_rate', sa.Float),
        sa.Column('efficiency_score', sa.Float),
        sa.Column('anomalies_detected', sa.Integer),
        sa.Column('cost_savings_potential', sa.Float),
        sa.Column('optimization_recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Drought Prediction tables
    op.create_table('drought_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('precipitation_mm', sa.Float),
        sa.Column('temperature_celsius', sa.Float),
        sa.Column('humidity_percent', sa.Float),
        sa.Column('wind_speed_ms', sa.Float),
        sa.Column('soil_moisture', sa.Float),
        sa.Column('vegetation_index', sa.Float),
        sa.Column('evapotranspiration', sa.Float),
        sa.Column('geometry', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('drought_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('spi_index', sa.Float),
        sa.Column('drought_severity', sa.String(20)),
        sa.Column('drought_duration_days', sa.Integer),
        sa.Column('affected_area_km2', sa.Float),
        sa.Column('agricultural_impact', sa.Float),
        sa.Column('water_shortage_risk', sa.Float),
        sa.Column('mitigation_strategies', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Urban Water Network tables
    op.create_table('water_network_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('node_id', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('flow_rate', sa.Float),
        sa.Column('pressure', sa.Float),
        sa.Column('water_level', sa.Float),
        sa.Column('quality_parameters', postgresql.JSONB),
        sa.Column('location', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('water_network_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('network_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('leak_detection_count', sa.Integer),
        sa.Column('pressure_optimization_score', sa.Float),
        sa.Column('flow_efficiency', sa.Float),
        sa.Column('water_quality_score', sa.Float),
        sa.Column('network_performance_score', sa.Float),
        sa.Column('maintenance_priorities', postgresql.ARRAY(sa.String)),
        sa.Column('cost_savings_potential', sa.Float),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Drinking Water Quality tables
    op.create_table('drinking_water_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('sample_id', sa.String(100), nullable=False),
        sa.Column('sampling_date', sa.Date, nullable=False),
        sa.Column('source_type', sa.String(50)),
        sa.Column('location', sa.Text),
        sa.Column('physical_parameters', postgresql.JSONB),
        sa.Column('chemical_parameters', postgresql.JSONB),
        sa.Column('microbiological_parameters', postgresql.JSONB),
        sa.Column('heavy_metals', postgresql.JSONB),
        sa.Column('organic_compounds', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('drinking_water_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('water_system_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('overall_quality_score', sa.Float),
        sa.Column('compliance_status', sa.String(20)),
        sa.Column('health_risk_assessment', postgresql.JSONB),
        sa.Column('contaminant_priority_list', postgresql.ARRAY(sa.String)),
        sa.Column('treatment_recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('monitoring_frequency', sa.String(50)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Transboundary Water tables
    op.create_table('transboundary_basin_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('basin_id', sa.String(100), nullable=False),
        sa.Column('basin_name', sa.String(255), nullable=False),
        sa.Column('countries', postgresql.ARRAY(sa.String)),
        sa.Column('area_km2', sa.Float),
        sa.Column('population', sa.Integer),
        sa.Column('water_resources', postgresql.JSONB),
        sa.Column('agreements', postgresql.JSONB),
        sa.Column('geometry', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('transboundary_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('basin_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('water_balance', postgresql.JSONB),
        sa.Column('conflict_risk_score', sa.Float),
        sa.Column('cooperation_index', sa.Float),
        sa.Column('sustainability_score', sa.Float),
        sa.Column('allocation_analysis', postgresql.JSONB),
        sa.Column('risk_assessment', postgresql.JSONB),
        sa.Column('recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Dust Storm tables
    op.create_table('dust_storm_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('wind_speed_ms', sa.Float),
        sa.Column('wind_direction_degrees', sa.Float),
        sa.Column('visibility_km', sa.Float),
        sa.Column('pm10_concentration', sa.Float),
        sa.Column('pm25_concentration', sa.Float),
        sa.Column('temperature_celsius', sa.Float),
        sa.Column('humidity_percent', sa.Float),
        sa.Column('atmospheric_pressure', sa.Float),
        sa.Column('location', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('dust_storm_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('storm_probability', sa.Float),
        sa.Column('intensity_level', sa.String(20)),
        sa.Column('affected_area_km2', sa.Float),
        sa.Column('population_impact', sa.Integer),
        sa.Column('air_quality_index', sa.Integer),
        sa.Column('health_risk_level', sa.String(20)),
        sa.Column('early_warning_level', sa.String(20)),
        sa.Column('response_recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Data Center Water tables
    op.create_table('datacenter_water_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('datacenter_id', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cooling_water_consumption', sa.Float),
        sa.Column('humidity_control_water', sa.Float),
        sa.Column('fire_suppression_water', sa.Float),
        sa.Column('total_water_consumption', sa.Float),
        sa.Column('energy_consumption_kwh', sa.Float),
        sa.Column('server_load_percent', sa.Float),
        sa.Column('cooling_efficiency', sa.Float),
        sa.Column('location', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('datacenter_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('datacenter_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('water_use_efficiency', sa.Float),
        sa.Column('pue_ratio', sa.Float),
        sa.Column('wue_ratio', sa.Float),
        sa.Column('cooling_optimization_score', sa.Float),
        sa.Column('sustainability_score', sa.Float),
        sa.Column('cost_savings_potential', sa.Float),
        sa.Column('optimization_recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Agricultural Reservoir tables
    op.create_table('agricultural_reservoir_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('reservoir_id', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('water_level_m', sa.Float),
        sa.Column('storage_capacity_m3', sa.Float),
        sa.Column('inflow_rate_m3s', sa.Float),
        sa.Column('outflow_rate_m3s', sa.Float),
        sa.Column('evaporation_rate_mm', sa.Float),
        sa.Column('water_temperature_celsius', sa.Float),
        sa.Column('water_quality_parameters', postgresql.JSONB),
        sa.Column('weather_conditions', postgresql.JSONB),
        sa.Column('location', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('agricultural_reservoir_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reservoir_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('water_availability_score', sa.Float),
        sa.Column('irrigation_efficiency', sa.Float),
        sa.Column('crop_water_requirement', sa.Float),
        sa.Column('reservoir_optimization_score', sa.Float),
        sa.Column('risk_assessment', postgresql.JSONB),
        sa.Column('forecasting_accuracy', sa.Float),
        sa.Column('management_recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Urban Green Space tables
    op.create_table('urban_green_space_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('green_space_id', sa.String(100), nullable=False),
        sa.Column('area_hectares', sa.Float),
        sa.Column('vegetation_density', sa.Float),
        sa.Column('tree_coverage_percent', sa.Float),
        sa.Column('water_features', postgresql.JSONB),
        sa.Column('species_richness', sa.Integer),
        sa.Column('habitat_diversity', sa.Float),
        sa.Column('accessibility_score', sa.Float),
        sa.Column('recreation_facilities', postgresql.JSONB),
        sa.Column('location', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('urban_green_space_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('green_space_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('ecosystem_services_score', sa.Float),
        sa.Column('biodiversity_level', sa.String(20)),
        sa.Column('climate_resilience_score', sa.Float),
        sa.Column('optimization_potential', sa.Float),
        sa.Column('health_benefits_score', sa.Float),
        sa.Column('economic_value_usd', sa.Float),
        sa.Column('recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Environmental Health tables
    op.create_table('environmental_health_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('sampling_date', sa.Date, nullable=False),
        sa.Column('population_density', sa.Integer),
        sa.Column('exposure_duration_years', sa.Float),
        sa.Column('water_contaminants', postgresql.JSONB),
        sa.Column('air_contaminants', postgresql.JSONB),
        sa.Column('soil_contaminants', postgresql.JSONB),
        sa.Column('health_indicators', postgresql.JSONB),
        sa.Column('socioeconomic_factors', postgresql.JSONB),
        sa.Column('location', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table('environmental_health_analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('region_id', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('overall_risk_score', sa.Float),
        sa.Column('risk_level', sa.String(20)),
        sa.Column('health_outcomes', postgresql.JSONB),
        sa.Column('vulnerable_populations', postgresql.JSONB),
        sa.Column('exposure_pathways', postgresql.JSONB),
        sa.Column('intervention_recommendations', postgresql.ARRAY(sa.String)),
        sa.Column('public_health_impact', postgresql.JSONB),
        sa.Column('processing_time', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # ============================================================================
    # SYSTEM TABLES
    # ============================================================================
    
    # Analysis results summary
    op.create_table('analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('module_name', sa.String(100), nullable=False),
        sa.Column('analysis_type', sa.String(100), nullable=False),
        sa.Column('input_data', postgresql.JSONB),
        sa.Column('output_data', postgresql.JSONB),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('processing_time', sa.Float)
    )
    
    # Alerts
    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('module_name', sa.String(100), nullable=False),
        sa.Column('alert_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('location', sa.Text),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Data sources
    op.create_table('data_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('url', sa.String(500)),
        sa.Column('api_key', sa.String(255)),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('last_updated', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # File uploads
    op.create_table('file_uploads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.BigInteger),
        sa.Column('file_type', sa.String(50)),
        sa.Column('upload_status', sa.String(20), default='uploading'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Reports
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', postgresql.JSONB),
        sa.Column('file_path', sa.String(500)),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Audit log
    op.create_table('audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(100)),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('details', postgresql.JSONB),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # ============================================================================
    # INDEXES
    # ============================================================================
    
    # Core system indexes
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_country_code', 'users', ['country_code'])
    op.create_index('idx_organizations_country_code', 'organizations', ['country_code'])
    op.create_index('idx_user_organizations_user_id', 'user_organizations', ['user_id'])
    op.create_index('idx_user_organizations_org_id', 'user_organizations', ['organization_id'])
    
    # Module-specific indexes
    op.create_index('idx_insar_subsidence_region_date', 'insar_subsidence_data', ['region_id', 'acquisition_date'])
    op.create_index('idx_insar_results_user_region', 'insar_analysis_results', ['user_id', 'region_id'])
    
    op.create_index('idx_flood_modeling_region', 'flood_modeling_data', ['region_id'])
    op.create_index('idx_flood_results_user_region', 'flood_analysis_results', ['user_id', 'region_id'])
    
    op.create_index('idx_groundwater_well_date', 'groundwater_data', ['well_id', 'sampling_date'])
    op.create_index('idx_groundwater_results_user_aquifer', 'groundwater_analysis_results', ['user_id', 'aquifer_id'])
    
    op.create_index('idx_iot_sensor_timestamp', 'iot_sensor_data', ['sensor_id', 'timestamp'])
    op.create_index('idx_iot_results_user_facility', 'iot_analysis_results', ['user_id', 'facility_id'])
    
    op.create_index('idx_drought_region_date', 'drought_data', ['region_id', 'date'])
    op.create_index('idx_drought_results_user_region', 'drought_analysis_results', ['user_id', 'region_id'])
    
    op.create_index('idx_water_network_node_timestamp', 'water_network_data', ['node_id', 'timestamp'])
    op.create_index('idx_water_network_results_user_network', 'water_network_analysis_results', ['user_id', 'network_id'])
    
    op.create_index('idx_drinking_water_sample_date', 'drinking_water_data', ['sample_id', 'sampling_date'])
    op.create_index('idx_drinking_water_results_user_system', 'drinking_water_analysis_results', ['user_id', 'water_system_id'])
    
    op.create_index('idx_transboundary_basin_id', 'transboundary_basin_data', ['basin_id'])
    op.create_index('idx_transboundary_results_user_basin', 'transboundary_analysis_results', ['user_id', 'basin_id'])
    
    op.create_index('idx_dust_storm_region_timestamp', 'dust_storm_data', ['region_id', 'timestamp'])
    op.create_index('idx_dust_storm_results_user_region', 'dust_storm_analysis_results', ['user_id', 'region_id'])
    
    op.create_index('idx_datacenter_water_timestamp', 'datacenter_water_data', ['datacenter_id', 'timestamp'])
    op.create_index('idx_datacenter_results_user_datacenter', 'datacenter_analysis_results', ['user_id', 'datacenter_id'])
    
    op.create_index('idx_agricultural_reservoir_timestamp', 'agricultural_reservoir_data', ['reservoir_id', 'timestamp'])
    op.create_index('idx_agricultural_results_user_reservoir', 'agricultural_reservoir_analysis_results', ['user_id', 'reservoir_id'])
    
    op.create_index('idx_urban_green_space_id', 'urban_green_space_data', ['green_space_id'])
    op.create_index('idx_urban_green_space_results_user_space', 'urban_green_space_analysis_results', ['user_id', 'green_space_id'])
    
    op.create_index('idx_environmental_health_region_date', 'environmental_health_data', ['region_id', 'sampling_date'])
    op.create_index('idx_environmental_health_results_user_region', 'environmental_health_analysis_results', ['user_id', 'region_id'])
    
    # System indexes
    op.create_index('idx_analysis_results_user_module', 'analysis_results', ['user_id', 'module_name'])
    op.create_index('idx_alerts_user_severity', 'alerts', ['user_id', 'severity'])
    op.create_index('idx_file_uploads_user_status', 'file_uploads', ['user_id', 'upload_status'])
    op.create_index('idx_audit_log_user_created', 'audit_log', ['user_id', 'created_at'])
    
    # ============================================================================
    # INITIAL DATA
    # ============================================================================
    
    # Insert default admin user
    op.execute("""
        INSERT INTO users (username, email, hashed_password, full_name, roles, country_code, language)
        VALUES (
            'admin',
            'admin@aquatrak.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G',
            'Administrator',
            ARRAY['admin'],
            'IR',
            'en'
        )
    """)
    
    # Insert default organization
    op.execute("""
        INSERT INTO organizations (name, type, country_code, contact_email, subscription_plan)
        VALUES (
            'AquaTrak Organization',
            'government',
            'IR',
            'contact@aquatrak.com',
            'premium'
        )
    """)
    
    # Link admin to organization
    op.execute("""
        INSERT INTO user_organizations (user_id, organization_id, role)
        SELECT u.id, o.id, 'admin'
        FROM users u, organizations o
        WHERE u.username = 'admin' AND o.name = 'AquaTrak Organization'
    """)
    
    # Insert default data sources
    op.execute("""
        INSERT INTO data_sources (name, type, url, status)
        VALUES 
            ('NOAA', 'weather', 'https://api.weather.gov', 'active'),
            ('Copernicus', 'satellite', 'https://scihub.copernicus.eu', 'active'),
            ('ECMWF', 'forecast', 'https://api.ecmwf.int', 'active'),
            ('USGS', 'hydrology', 'https://waterdata.usgs.gov', 'active'),
            ('NASA', 'satellite', 'https://earthdata.nasa.gov', 'active')
    """)

def downgrade():
    """Downgrade database from this revision"""
    
    # Drop all tables in reverse order
    tables = [
        'environmental_health_analysis_results', 'environmental_health_data',
        'urban_green_space_analysis_results', 'urban_green_space_data',
        'agricultural_reservoir_analysis_results', 'agricultural_reservoir_data',
        'datacenter_analysis_results', 'datacenter_water_data',
        'dust_storm_analysis_results', 'dust_storm_data',
        'transboundary_analysis_results', 'transboundary_basin_data',
        'drinking_water_analysis_results', 'drinking_water_data',
        'water_network_analysis_results', 'water_network_data',
        'drought_analysis_results', 'drought_data',
        'iot_analysis_results', 'iot_sensor_data',
        'groundwater_analysis_results', 'groundwater_data',
        'flood_analysis_results', 'flood_modeling_data',
        'insar_analysis_results', 'insar_subsidence_data',
        'audit_log', 'reports', 'file_uploads', 'data_sources',
        'alerts', 'analysis_results', 'user_organizations',
        'organizations', 'users'
    ]
    
    for table in tables:
        op.drop_table(table)
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "postgis"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"') 