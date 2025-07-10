// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Authentication Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: UserRole;
  organization_id?: string;
  country: string;
  language: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type UserRole = 'admin' | 'manager' | 'analyst' | 'viewer';

// Module Types
export interface Module {
  id: string;
  name: string;
  description: string;
  category: ModuleCategory;
  status: ModuleStatus;
  version: string;
  last_updated: string;
  config: ModuleConfig;
}

export type ModuleCategory = 
  | 'water_quality'
  | 'flood_modeling'
  | 'groundwater'
  | 'iot_monitoring'
  | 'drought_prediction'
  | 'urban_planning'
  | 'environmental_health'
  | 'data_center'
  | 'agricultural'
  | 'transboundary'
  | 'dust_storm'
  | 'subsidence'
  | 'green_space';

export type ModuleStatus = 'active' | 'inactive' | 'maintenance' | 'error';

export interface ModuleConfig {
  enabled: boolean;
  parameters: Record<string, any>;
  data_sources: string[];
  update_frequency: number;
}

// Analysis Result Types
export interface AnalysisResult {
  id: string;
  module_id: string;
  module_name: string;
  analysis_type: string;
  status: AnalysisStatus;
  parameters: Record<string, any>;
  results: Record<string, any>;
  metadata: AnalysisMetadata;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface AnalysisMetadata {
  data_sources: string[];
  processing_time?: number;
  data_points: number;
  geographic_scope: GeographicScope;
  confidence_score?: number;
  model_version: string;
}

export interface GeographicScope {
  country: string;
  region?: string;
  city?: string;
  coordinates?: {
    lat: number;
    lng: number;
    radius?: number;
  };
  bounding_box?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
}

// IoT Water Consumption Types
export interface IoTWaterData {
  device_id: string;
  timestamp: string;
  consumption: number;
  flow_rate: number;
  pressure: number;
  temperature: number;
  quality_metrics: WaterQualityMetrics;
  location: {
    lat: number;
    lng: number;
  };
}

export interface WaterQualityMetrics {
  ph: number;
  turbidity: number;
  conductivity: number;
  dissolved_oxygen: number;
  temperature: number;
}

export interface IoTAnalysisResult extends AnalysisResult {
  results: {
    consumption_trends: ConsumptionTrend[];
    anomalies: Anomaly[];
    efficiency_score: number;
    recommendations: Recommendation[];
    cost_savings: CostSavings;
    forecasting: ForecastData;
  };
}

export interface ConsumptionTrend {
  period: string;
  average_consumption: number;
  peak_consumption: number;
  trend_direction: 'increasing' | 'decreasing' | 'stable';
  change_percentage: number;
}

export interface Anomaly {
  timestamp: string;
  type: 'high_consumption' | 'low_consumption' | 'quality_issue' | 'pressure_drop';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  value: number;
  threshold: number;
}

export interface Recommendation {
  category: 'efficiency' | 'maintenance' | 'optimization' | 'cost_savings';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  potential_savings?: number;
  implementation_cost?: number;
  roi_percentage?: number;
}

export interface CostSavings {
  monthly_savings: number;
  annual_savings: number;
  potential_savings: number;
  current_cost: number;
  optimized_cost: number;
  roi_percentage: number;
}

export interface ForecastData {
  predictions: ForecastPoint[];
  confidence_interval: {
    upper: number[];
    lower: number[];
  };
  accuracy_metrics: {
    mae: number;
    rmse: number;
    mape: number;
  };
}

export interface ForecastPoint {
  timestamp: string;
  predicted_consumption: number;
  confidence: number;
}

// Environmental Health Types
export interface EnvironmentalHealthData {
  location: {
    lat: number;
    lng: number;
    address: string;
  };
  timestamp: string;
  air_quality: AirQualityMetrics;
  water_quality: WaterQualityMetrics;
  soil_quality: SoilQualityMetrics;
  noise_levels: NoiseMetrics;
  environmental_indicators: EnvironmentalIndicators;
}

export interface AirQualityMetrics {
  pm25: number;
  pm10: number;
  no2: number;
  o3: number;
  co: number;
  so2: number;
  aqi: number;
}

export interface SoilQualityMetrics {
  ph: number;
  organic_matter: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  heavy_metals: HeavyMetalConcentrations;
}

export interface HeavyMetalConcentrations {
  lead: number;
  cadmium: number;
  mercury: number;
  arsenic: number;
  chromium: number;
}

export interface NoiseMetrics {
  day_level: number;
  night_level: number;
  peak_level: number;
  equivalent_level: number;
}

export interface EnvironmentalIndicators {
  biodiversity_index: number;
  green_coverage: number;
  air_pollution_index: number;
  water_pollution_index: number;
  soil_contamination_index: number;
  overall_health_score: number;
}

// Urban Green Space Types
export interface GreenSpaceData {
  location: {
    lat: number;
    lng: number;
    area: number;
  };
  green_space_type: GreenSpaceType;
  vegetation_data: VegetationMetrics;
  ecosystem_services: EcosystemServices;
  accessibility: AccessibilityMetrics;
  maintenance_status: MaintenanceStatus;
}

export type GreenSpaceType = 'park' | 'garden' | 'forest' | 'wetland' | 'urban_farm' | 'green_roof' | 'green_wall';

export interface VegetationMetrics {
  tree_density: number;
  canopy_cover: number;
  species_diversity: number;
  vegetation_health: number;
  seasonal_changes: SeasonalData[];
}

export interface SeasonalData {
  season: string;
  vegetation_index: number;
  flowering_period: boolean;
  maintenance_needs: string[];
}

export interface EcosystemServices {
  carbon_sequestration: number;
  air_purification: number;
  water_filtration: number;
  temperature_regulation: number;
  biodiversity_support: number;
  recreational_value: number;
}

export interface AccessibilityMetrics {
  walking_distance: number;
  public_transport: boolean;
  parking_available: boolean;
  wheelchair_accessible: boolean;
  opening_hours: string;
  visitor_capacity: number;
}

export interface MaintenanceStatus {
  overall_condition: 'excellent' | 'good' | 'fair' | 'poor';
  last_maintenance: string;
  next_maintenance: string;
  maintenance_needs: string[];
  budget_allocated: number;
}

// Urban Water Network Types
export interface WaterNetworkData {
  network_id: string;
  location: {
    lat: number;
    lng: number;
  };
  timestamp: string;
  pressure: number;
  flow_rate: number;
  water_quality: WaterQualityMetrics;
  infrastructure_status: InfrastructureStatus;
  performance_metrics: PerformanceMetrics;
}

export interface InfrastructureStatus {
  pipe_condition: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  age_years: number;
  material: string;
  diameter: number;
  last_inspection: string;
  maintenance_history: MaintenanceRecord[];
}

export interface MaintenanceRecord {
  date: string;
  type: string;
  description: string;
  cost: number;
  contractor: string;
}

export interface PerformanceMetrics {
  efficiency_score: number;
  reliability_index: number;
  water_loss_percentage: number;
  customer_satisfaction: number;
  response_time_minutes: number;
}

// Alert Types
export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  module_id?: string;
  analysis_id?: string;
  location?: {
    lat: number;
    lng: number;
  };
  metadata: Record<string, any>;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  status: AlertStatus;
}

export type AlertType = 
  | 'anomaly_detected'
  | 'threshold_exceeded'
  | 'system_error'
  | 'maintenance_required'
  | 'data_quality_issue'
  | 'security_alert';

export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed';

// Dashboard Types
export interface Dashboard {
  id: string;
  name: string;
  description: string;
  user_id: string;
  is_public: boolean;
  widgets: DashboardWidget[];
  layout: WidgetLayout[];
  created_at: string;
  updated_at: string;
}

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  config: WidgetConfig;
  data_source: string;
  refresh_interval: number;
}

export type WidgetType = 
  | 'chart'
  | 'map'
  | 'table'
  | 'metric'
  | 'gauge'
  | 'heatmap'
  | 'timeline'
  | 'alert_feed';

export interface WidgetConfig {
  chart_type?: 'line' | 'bar' | 'pie' | 'scatter' | 'area';
  metrics?: string[];
  time_range?: string;
  filters?: Record<string, any>;
  display_options?: Record<string, any>;
}

export interface WidgetLayout {
  widget_id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

// Organization Types
export interface Organization {
  id: string;
  name: string;
  description: string;
  country: string;
  industry: string;
  size: OrganizationSize;
  subscription_plan: SubscriptionPlan;
  settings: OrganizationSettings;
  created_at: string;
  updated_at: string;
}

export type OrganizationSize = 'small' | 'medium' | 'large' | 'enterprise';

export type SubscriptionPlan = 'basic' | 'professional' | 'enterprise' | 'custom';

export interface OrganizationSettings {
  default_language: string;
  default_country: string;
  timezone: string;
  data_retention_days: number;
  max_users: number;
  enabled_modules: string[];
  custom_branding?: {
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
  };
}

// Error Types
export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, any>;
  status_code: number;
  timestamp: string;
}

// Filter Types
export interface DataFilter {
  date_range?: {
    start: string;
    end: string;
  };
  location?: {
    country?: string;
    region?: string;
    city?: string;
    coordinates?: {
      lat: number;
      lng: number;
      radius: number;
    };
  };
  modules?: string[];
  status?: string[];
  severity?: string[];
  [key: string]: any;
}

// Export all types
export type {
  ApiResponse,
  PaginatedResponse,
  LoginRequest,
  LoginResponse,
  User,
  Module,
  AnalysisResult,
  IoTWaterData,
  IoTAnalysisResult,
  EnvironmentalHealthData,
  GreenSpaceData,
  WaterNetworkData,
  Alert,
  Dashboard,
  Organization,
  ApiError,
  DataFilter
}; 