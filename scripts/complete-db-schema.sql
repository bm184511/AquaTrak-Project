-- This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

-- Complete Database Schema for AquaTrak Platform
-- PostgreSQL database schema for all 13 modules

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- CORE SYSTEM TABLES
-- ============================================================================

-- Users and authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    roles TEXT[] DEFAULT ARRAY['user'],
    is_active BOOLEAN DEFAULT TRUE,
    country_code VARCHAR(2),
    language VARCHAR(5) DEFAULT 'en',
    organization VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- government, private, academic, etc.
    country_code VARCHAR(2),
    address TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User organization relationships
CREATE TABLE user_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- admin, member, viewer
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, organization_id)
);

-- ============================================================================
-- MODULE 1: INSAR SUBSIDENCE MONITORING
-- ============================================================================

CREATE TABLE insar_subsidence_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id VARCHAR(100) NOT NULL,
    satellite_source VARCHAR(50), -- Sentinel-1, ALOS, etc.
    acquisition_date DATE NOT NULL,
    interferogram_path VARCHAR(500),
    coherence_threshold FLOAT DEFAULT 0.3,
    deformation_rate FLOAT, -- mm/year
    uncertainty FLOAT,
    geometry GEOMETRY(POLYGON, 4326),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE insar_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    region_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    subsidence_rate FLOAT,
    risk_level VARCHAR(20), -- low, medium, high, critical
    affected_area_km2 FLOAT,
    population_at_risk INTEGER,
    infrastructure_risk JSONB,
    recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 2: URBAN FLOOD MODELING
-- ============================================================================

CREATE TABLE flood_modeling_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id VARCHAR(100) NOT NULL,
    rainfall_intensity FLOAT, -- mm/hour
    duration_hours FLOAT,
    return_period INTEGER, -- years
    elevation_data_path VARCHAR(500),
    land_use_data JSONB,
    soil_type_data JSONB,
    drainage_network JSONB,
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE flood_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    region_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    flood_depth_max FLOAT, -- meters
    flood_extent_km2 FLOAT,
    affected_population INTEGER,
    infrastructure_damage_estimate FLOAT, -- USD
    evacuation_required BOOLEAN,
    risk_zones JSONB,
    mitigation_measures TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 3: GROUNDWATER POLLUTION ANALYSIS
-- ============================================================================

CREATE TABLE groundwater_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_id VARCHAR(100) NOT NULL,
    sampling_date DATE NOT NULL,
    depth_m FLOAT,
    ph FLOAT,
    conductivity FLOAT, -- μS/cm
    temperature FLOAT, -- °C
    dissolved_oxygen FLOAT, -- mg/L
    turbidity FLOAT, -- NTU
    contaminants JSONB, -- {contaminant: concentration}
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE groundwater_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    aquifer_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    pollution_index FLOAT,
    risk_level VARCHAR(20),
    affected_area_km2 FLOAT,
    contaminant_sources JSONB,
    remediation_priority TEXT[],
    monitoring_recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 4: IOT WATER CONSUMPTION
-- ============================================================================

CREATE TABLE iot_sensor_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    flow_rate FLOAT, -- L/min
    pressure FLOAT, -- bar
    temperature FLOAT, -- °C
    conductivity FLOAT, -- μS/cm
    ph FLOAT,
    location GEOMETRY(POINT, 4326),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE iot_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    facility_id VARCHAR(100) NOT NULL,
    analysis_period_start TIMESTAMP WITH TIME ZONE,
    analysis_period_end TIMESTAMP WITH TIME ZONE,
    total_consumption FLOAT, -- L
    average_flow_rate FLOAT,
    efficiency_score FLOAT,
    anomalies_detected INTEGER,
    cost_savings_potential FLOAT, -- USD
    optimization_recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 5: DROUGHT PREDICTION
-- ============================================================================

CREATE TABLE drought_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    precipitation_mm FLOAT,
    temperature_celsius FLOAT,
    humidity_percent FLOAT,
    wind_speed_ms FLOAT,
    soil_moisture FLOAT, -- %
    vegetation_index FLOAT, -- NDVI
    evapotranspiration FLOAT, -- mm/day
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE drought_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    region_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    spi_index FLOAT, -- Standardized Precipitation Index
    drought_severity VARCHAR(20), -- none, mild, moderate, severe, extreme
    drought_duration_days INTEGER,
    affected_area_km2 FLOAT,
    agricultural_impact FLOAT, -- % crop loss
    water_shortage_risk FLOAT,
    mitigation_strategies TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 6: URBAN WATER NETWORK MONITORING
-- ============================================================================

CREATE TABLE water_network_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    flow_rate FLOAT, -- L/min
    pressure FLOAT, -- bar
    water_level FLOAT, -- meters
    quality_parameters JSONB, -- {turbidity, chlorine, ph, etc.}
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE water_network_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    network_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    leak_detection_count INTEGER,
    pressure_optimization_score FLOAT,
    flow_efficiency FLOAT,
    water_quality_score FLOAT,
    network_performance_score FLOAT,
    maintenance_priorities TEXT[],
    cost_savings_potential FLOAT, -- USD
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 7: DRINKING WATER QUALITY ANALYSIS
-- ============================================================================

CREATE TABLE drinking_water_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id VARCHAR(100) NOT NULL,
    sampling_date DATE NOT NULL,
    source_type VARCHAR(50), -- tap, well, spring, etc.
    location GEOMETRY(POINT, 4326),
    physical_parameters JSONB, -- {turbidity, color, taste, odor}
    chemical_parameters JSONB, -- {ph, hardness, alkalinity, etc.}
    microbiological_parameters JSONB, -- {coliform, e.coli, etc.}
    heavy_metals JSONB, -- {lead, mercury, arsenic, etc.}
    organic_compounds JSONB, -- {pesticides, herbicides, etc.}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE drinking_water_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    water_system_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    overall_quality_score FLOAT,
    compliance_status VARCHAR(20), -- compliant, non-compliant, marginal
    health_risk_assessment JSONB,
    contaminant_priority_list TEXT[],
    treatment_recommendations TEXT[],
    monitoring_frequency VARCHAR(50),
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 8: TRANSBOUNDARY WATER MODELING
-- ============================================================================

CREATE TABLE transboundary_basin_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    basin_id VARCHAR(100) NOT NULL,
    basin_name VARCHAR(255) NOT NULL,
    countries TEXT[], -- array of country codes
    area_km2 FLOAT,
    population INTEGER,
    water_resources JSONB, -- {surface_water, groundwater, etc.}
    agreements JSONB, -- {agreement_name, status, effectiveness}
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transboundary_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    basin_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    water_balance JSONB, -- {inflow, outflow, storage}
    conflict_risk_score FLOAT,
    cooperation_index FLOAT,
    sustainability_score FLOAT,
    allocation_analysis JSONB,
    risk_assessment JSONB,
    recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 9: DUST STORM ANALYSIS
-- ============================================================================

CREATE TABLE dust_storm_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    wind_speed_ms FLOAT,
    wind_direction_degrees FLOAT,
    visibility_km FLOAT,
    pm10_concentration FLOAT, -- μg/m³
    pm25_concentration FLOAT, -- μg/m³
    temperature_celsius FLOAT,
    humidity_percent FLOAT,
    atmospheric_pressure FLOAT, -- hPa
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dust_storm_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    region_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    storm_probability FLOAT,
    intensity_level VARCHAR(20), -- low, medium, high, extreme
    affected_area_km2 FLOAT,
    population_impact INTEGER,
    air_quality_index INTEGER,
    health_risk_level VARCHAR(20),
    early_warning_level VARCHAR(20), -- advisory, watch, warning, critical
    response_recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 10: DATA CENTER WATER CONSUMPTION
-- ============================================================================

CREATE TABLE datacenter_water_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    datacenter_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    cooling_water_consumption FLOAT, -- L/hour
    humidity_control_water FLOAT, -- L/hour
    fire_suppression_water FLOAT, -- L/hour
    total_water_consumption FLOAT, -- L/hour
    energy_consumption_kwh FLOAT,
    server_load_percent FLOAT,
    cooling_efficiency FLOAT,
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE datacenter_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    datacenter_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    water_use_efficiency FLOAT, -- L/kWh
    pue_ratio FLOAT, -- Power Usage Effectiveness
    wue_ratio FLOAT, -- Water Usage Effectiveness
    cooling_optimization_score FLOAT,
    sustainability_score FLOAT,
    cost_savings_potential FLOAT, -- USD
    optimization_recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 11: AGRICULTURAL RESERVOIR MANAGEMENT
-- ============================================================================

CREATE TABLE agricultural_reservoir_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reservoir_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    water_level_m FLOAT,
    storage_capacity_m3 FLOAT,
    inflow_rate_m3s FLOAT,
    outflow_rate_m3s FLOAT,
    evaporation_rate_mm FLOAT,
    water_temperature_celsius FLOAT,
    water_quality_parameters JSONB,
    weather_conditions JSONB,
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agricultural_reservoir_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    reservoir_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    water_availability_score FLOAT,
    irrigation_efficiency FLOAT,
    crop_water_requirement FLOAT, -- mm/day
    reservoir_optimization_score FLOAT,
    risk_assessment JSONB,
    forecasting_accuracy FLOAT,
    management_recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 12: URBAN GREEN SPACE OPTIMIZATION
-- ============================================================================

CREATE TABLE urban_green_space_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    green_space_id VARCHAR(100) NOT NULL,
    area_hectares FLOAT,
    vegetation_density FLOAT, -- 0-1
    tree_coverage_percent FLOAT,
    water_features JSONB, -- {ponds, streams, etc.}
    species_richness INTEGER,
    habitat_diversity FLOAT, -- 0-1
    accessibility_score FLOAT, -- 0-1
    recreation_facilities JSONB,
    location GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE urban_green_space_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    green_space_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    ecosystem_services_score FLOAT,
    biodiversity_level VARCHAR(20), -- low, medium, high
    climate_resilience_score FLOAT,
    optimization_potential FLOAT,
    health_benefits_score FLOAT,
    economic_value_usd FLOAT,
    recommendations TEXT[],
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODULE 13: ENVIRONMENTAL HEALTH RISK ANALYSIS
-- ============================================================================

CREATE TABLE environmental_health_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id VARCHAR(100) NOT NULL,
    sampling_date DATE NOT NULL,
    population_density INTEGER, -- people/km²
    exposure_duration_years FLOAT,
    water_contaminants JSONB,
    air_contaminants JSONB,
    soil_contaminants JSONB,
    health_indicators JSONB, -- {disease_rates, mortality, etc.}
    socioeconomic_factors JSONB,
    location GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE environmental_health_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    region_id VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    overall_risk_score FLOAT,
    risk_level VARCHAR(20), -- low, medium, high, critical
    health_outcomes JSONB,
    vulnerable_populations JSONB,
    exposure_pathways JSONB,
    intervention_recommendations TEXT[],
    public_health_impact JSONB,
    processing_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SYSTEM TABLES
-- ============================================================================

-- Analysis results summary
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    module_name VARCHAR(100) NOT NULL,
    analysis_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time FLOAT
);

-- Alerts and notifications
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    module_name VARCHAR(100) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    location GEOMETRY(POINT, 4326),
    metadata JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data sources
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    url VARCHAR(500),
    api_key VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- File uploads
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    upload_status VARCHAR(20) DEFAULT 'uploading',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content JSONB,
    file_path VARCHAR(500),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Core system indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_country_code ON users(country_code);
CREATE INDEX idx_organizations_country_code ON organizations(country_code);
CREATE INDEX idx_user_organizations_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_organizations_org_id ON user_organizations(organization_id);

-- Module-specific indexes
CREATE INDEX idx_insar_subsidence_region_date ON insar_subsidence_data(region_id, acquisition_date);
CREATE INDEX idx_insar_subsidence_geometry ON insar_subsidence_data USING GIST(geometry);
CREATE INDEX idx_insar_results_user_region ON insar_analysis_results(user_id, region_id);

CREATE INDEX idx_flood_modeling_region ON flood_modeling_data(region_id);
CREATE INDEX idx_flood_modeling_geometry ON flood_modeling_data USING GIST(geometry);
CREATE INDEX idx_flood_results_user_region ON flood_analysis_results(user_id, region_id);

CREATE INDEX idx_groundwater_well_date ON groundwater_data(well_id, sampling_date);
CREATE INDEX idx_groundwater_location ON groundwater_data USING GIST(location);
CREATE INDEX idx_groundwater_results_user_aquifer ON groundwater_analysis_results(user_id, aquifer_id);

CREATE INDEX idx_iot_sensor_timestamp ON iot_sensor_data(sensor_id, timestamp);
CREATE INDEX idx_iot_sensor_location ON iot_sensor_data USING GIST(location);
CREATE INDEX idx_iot_results_user_facility ON iot_analysis_results(user_id, facility_id);

CREATE INDEX idx_drought_region_date ON drought_data(region_id, date);
CREATE INDEX idx_drought_geometry ON drought_data USING GIST(geometry);
CREATE INDEX idx_drought_results_user_region ON drought_analysis_results(user_id, region_id);

CREATE INDEX idx_water_network_node_timestamp ON water_network_data(node_id, timestamp);
CREATE INDEX idx_water_network_location ON water_network_data USING GIST(location);
CREATE INDEX idx_water_network_results_user_network ON water_network_analysis_results(user_id, network_id);

CREATE INDEX idx_drinking_water_sample_date ON drinking_water_data(sample_id, sampling_date);
CREATE INDEX idx_drinking_water_location ON drinking_water_data USING GIST(location);
CREATE INDEX idx_drinking_water_results_user_system ON drinking_water_analysis_results(user_id, water_system_id);

CREATE INDEX idx_transboundary_basin_id ON transboundary_basin_data(basin_id);
CREATE INDEX idx_transboundary_geometry ON transboundary_basin_data USING GIST(geometry);
CREATE INDEX idx_transboundary_results_user_basin ON transboundary_analysis_results(user_id, basin_id);

CREATE INDEX idx_dust_storm_region_timestamp ON dust_storm_data(region_id, timestamp);
CREATE INDEX idx_dust_storm_location ON dust_storm_data USING GIST(location);
CREATE INDEX idx_dust_storm_results_user_region ON dust_storm_analysis_results(user_id, region_id);

CREATE INDEX idx_datacenter_water_timestamp ON datacenter_water_data(datacenter_id, timestamp);
CREATE INDEX idx_datacenter_water_location ON datacenter_water_data USING GIST(location);
CREATE INDEX idx_datacenter_results_user_datacenter ON datacenter_analysis_results(user_id, datacenter_id);

CREATE INDEX idx_agricultural_reservoir_timestamp ON agricultural_reservoir_data(reservoir_id, timestamp);
CREATE INDEX idx_agricultural_reservoir_location ON agricultural_reservoir_data USING GIST(location);
CREATE INDEX idx_agricultural_results_user_reservoir ON agricultural_reservoir_analysis_results(user_id, reservoir_id);

CREATE INDEX idx_urban_green_space_id ON urban_green_space_data(green_space_id);
CREATE INDEX idx_urban_green_space_geometry ON urban_green_space_data USING GIST(location);
CREATE INDEX idx_urban_green_space_results_user_space ON urban_green_space_analysis_results(user_id, green_space_id);

CREATE INDEX idx_environmental_health_region_date ON environmental_health_data(region_id, sampling_date);
CREATE INDEX idx_environmental_health_geometry ON environmental_health_data USING GIST(location);
CREATE INDEX idx_environmental_health_results_user_region ON environmental_health_analysis_results(user_id, region_id);

-- System indexes
CREATE INDEX idx_analysis_results_user_module ON analysis_results(user_id, module_name);
CREATE INDEX idx_alerts_user_severity ON alerts(user_id, severity);
CREATE INDEX idx_alerts_location ON alerts USING GIST(location);
CREATE INDEX idx_file_uploads_user_status ON file_uploads(user_id, upload_status);
CREATE INDEX idx_audit_log_user_created ON audit_log(user_id, created_at);

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default admin user
INSERT INTO users (username, email, hashed_password, full_name, roles, country_code, language)
VALUES (
    'admin',
    'admin@aquatrak.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G', -- admin123
    'Administrator',
    ARRAY['admin'],
    'IR',
    'en'
);

-- Insert default organization
INSERT INTO organizations (name, type, country_code, contact_email, subscription_plan)
VALUES (
    'AquaTrak Organization',
    'government',
    'IR',
    'contact@aquatrak.com',
    'premium'
);

-- Link admin to organization
INSERT INTO user_organizations (user_id, organization_id, role)
SELECT u.id, o.id, 'admin'
FROM users u, organizations o
WHERE u.username = 'admin' AND o.name = 'AquaTrak Organization';

-- Insert default data sources
INSERT INTO data_sources (name, type, url, status)
VALUES 
    ('NOAA', 'weather', 'https://api.weather.gov', 'active'),
    ('Copernicus', 'satellite', 'https://scihub.copernicus.eu', 'active'),
    ('ECMWF', 'forecast', 'https://api.ecmwf.int', 'active'),
    ('USGS', 'hydrology', 'https://waterdata.usgs.gov', 'active'),
    ('NASA', 'satellite', 'https://earthdata.nasa.gov', 'active');

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate spatial statistics
CREATE OR REPLACE FUNCTION calculate_spatial_statistics(geometry_column GEOMETRY)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'area_km2', ST_Area(geometry_column) / 1000000,
        'centroid', ST_AsGeoJSON(ST_Centroid(geometry_column)),
        'bounding_box', ST_AsGeoJSON(ST_Envelope(geometry_column))
    ) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to get analysis summary
CREATE OR REPLACE FUNCTION get_analysis_summary(user_uuid UUID, module_name VARCHAR)
RETURNS TABLE(
    total_analyses BIGINT,
    avg_processing_time FLOAT,
    last_analysis_date TIMESTAMP WITH TIME ZONE,
    success_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_analyses,
        AVG(processing_time) as avg_processing_time,
        MAX(created_at) as last_analysis_date,
        (COUNT(*) FILTER (WHERE status = 'completed')::FLOAT / COUNT(*)::FLOAT) * 100 as success_rate
    FROM analysis_results 
    WHERE user_id = user_uuid AND module_name = $2;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for user dashboard summary
CREATE VIEW user_dashboard_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.full_name,
    o.name as organization_name,
    COUNT(ar.id) as total_analyses,
    COUNT(DISTINCT ar.module_name) as modules_used,
    MAX(ar.created_at) as last_activity
FROM users u
LEFT JOIN user_organizations uo ON u.id = uo.user_id
LEFT JOIN organizations o ON uo.organization_id = o.id
LEFT JOIN analysis_results ar ON u.id = ar.user_id
GROUP BY u.id, u.username, u.full_name, o.name;

-- View for module usage statistics
CREATE VIEW module_usage_statistics AS
SELECT 
    module_name,
    COUNT(*) as total_analyses,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(processing_time) as avg_processing_time,
    COUNT(*) FILTER (WHERE status = 'completed') as successful_analyses,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_analyses
FROM analysis_results
GROUP BY module_name
ORDER BY total_analyses DESC;

-- View for recent alerts
CREATE VIEW recent_alerts AS
SELECT 
    a.id,
    a.severity,
    a.message,
    a.module_name,
    u.username,
    a.created_at,
    ST_AsGeoJSON(a.location) as location_geojson
FROM alerts a
JOIN users u ON a.user_id = u.id
WHERE a.created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY a.created_at DESC;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts and authentication information';
COMMENT ON TABLE organizations IS 'Organizations using the AquaTrak platform';
COMMENT ON TABLE insar_subsidence_data IS 'InSAR subsidence monitoring data';
COMMENT ON TABLE flood_modeling_data IS 'Urban flood modeling input data';
COMMENT ON TABLE groundwater_data IS 'Groundwater quality and quantity data';
COMMENT ON TABLE iot_sensor_data IS 'IoT sensor data for water consumption monitoring';
COMMENT ON TABLE drought_data IS 'Drought prediction input data';
COMMENT ON TABLE water_network_data IS 'Urban water network monitoring data';
COMMENT ON TABLE drinking_water_data IS 'Drinking water quality data';
COMMENT ON TABLE transboundary_basin_data IS 'Transboundary water basin information';
COMMENT ON TABLE dust_storm_data IS 'Dust storm monitoring data';
COMMENT ON TABLE datacenter_water_data IS 'Data center water consumption data';
COMMENT ON TABLE agricultural_reservoir_data IS 'Agricultural reservoir monitoring data';
COMMENT ON TABLE urban_green_space_data IS 'Urban green space characteristics';
COMMENT ON TABLE environmental_health_data IS 'Environmental health risk data';

COMMENT ON COLUMN users.roles IS 'Array of user roles: admin, user, analyst, viewer';
COMMENT ON COLUMN analysis_results.status IS 'Analysis status: pending, processing, completed, failed';
COMMENT ON COLUMN alerts.severity IS 'Alert severity: info, warning, error, critical'; 