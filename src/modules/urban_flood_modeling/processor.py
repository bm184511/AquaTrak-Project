"""
Urban Flood Modeling Processor
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from scipy import stats, interpolate
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import cv2
from .models import *

logger = logging.getLogger(__name__)


class UrbanFloodProcessor:
    """Advanced urban flood modeling processor with AI/ML capabilities"""
    
    def __init__(self):
        """Initialize the urban flood processor with ML models"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing UrbanFloodProcessor with ML capabilities")
        
        # Initialize ML models for different aspects
        self.rainfall_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
        self.runoff_model = GradientBoostingRegressor(n_estimators=150, max_depth=10, random_state=42)
        self.flood_depth_model = MLPRegressor(hidden_layer_sizes=(100, 50, 25), max_iter=1000, random_state=42)
        self.damage_assessment_model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
        
        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.depth_scaler = MinMaxScaler()
        self.damage_scaler = StandardScaler()
        
        # Hydrological parameters
        self.curve_number = 85  # Urban area curve number
        self.impervious_fraction = 0.7  # Typical urban impervious fraction
        self.drainage_efficiency = 0.8  # Drainage system efficiency
        
    async def process_analysis(self, request: FloodAnalysisRequest) -> FloodResult:
        """Process urban flood analysis with advanced ML algorithms"""
        start_time = datetime.utcnow()
        self.logger.info(f"Processing urban flood analysis for request {request.id}")
        
        try:
            # Step 1: Generate synthetic rainfall data
            rainfall_data = await self._generate_rainfall_data(request)
            
            # Step 2: Calculate runoff using SCS-CN method and ML enhancement
            runoff_data = await self._calculate_runoff(rainfall_data, request.urban_parameters)
            
            # Step 3: Model flood propagation using hydrodynamic simulation
            flood_depth_map, flood_extent = await self._model_flood_propagation(runoff_data, request)
            
            # Step 4: Apply ML-based flood depth prediction
            enhanced_depth_map = await self._apply_ml_depth_prediction(flood_depth_map, request)
            
            # Step 5: Calculate affected areas and infrastructure impact
            affected_areas = await self._calculate_affected_areas(enhanced_depth_map, request)
            
            # Step 6: Assess damage using ML models
            damage_assessment = await self._assess_damage(enhanced_depth_map, affected_areas, request)
            
            # Step 7: Calculate risk metrics and severity
            risk_assessment = await self._calculate_risk_assessment(damage_assessment, enhanced_depth_map)
            
            # Step 8: Generate alerts and recommendations
            alerts = await self._generate_flood_alerts(risk_assessment, enhanced_depth_map)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = FloodResult(
                analysis_id=request.id,
                flood_depth_map=enhanced_depth_map.tolist() if hasattr(enhanced_depth_map, 'tolist') else enhanced_depth_map,
                flood_extent=flood_extent,
                max_depth=float(np.max(enhanced_depth_map)),
                affected_area=affected_areas['total_area'],
                severity=risk_assessment['severity'],
                risk_score=risk_assessment['risk_score'],
                economic_loss_estimate=damage_assessment['total_economic_loss'],
                infrastructure_impact=affected_areas['infrastructure_impact'],
                alerts=alerts,
                recommendations=risk_assessment['recommendations'],
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing urban flood analysis: {str(e)}")
            raise
    
    async def _generate_rainfall_data(self, request: FloodAnalysisRequest) -> Dict[str, Any]:
        """Generate synthetic rainfall data based on intensity and duration"""
        self.logger.info("Generating rainfall data")
        
        duration_hours = request.duration_hours
        intensity = request.rainfall_intensity
        return_period = request.return_period
        
        # Convert intensity to mm/hr based on rainfall intensity enum
        intensity_mapping = {
            RainfallIntensity.LIGHT: 2.5,
            RainfallIntensity.MODERATE: 7.5,
            RainfallIntensity.HEAVY: 15.0,
            RainfallIntensity.INTENSE: 30.0,
            RainfallIntensity.EXTREME: 50.0
        }
        
        base_intensity = intensity_mapping.get(intensity, 15.0)
        
        # Apply return period factor
        return_period_factor = 1 + (return_period / 100) * 0.5
        adjusted_intensity = base_intensity * return_period_factor
        
        # Generate time series with realistic patterns
        time_steps = np.arange(0, duration_hours, 0.25)  # 15-minute intervals
        
        # Create synthetic rainfall pattern (peak in middle, tapering ends)
        pattern = np.exp(-((time_steps - duration_hours/2) / (duration_hours/4))**2)
        pattern = pattern / np.max(pattern)  # Normalize
        
        # Add realistic variability
        noise = np.random.normal(0, 0.1, len(pattern))
        rainfall_rates = adjusted_intensity * pattern * (1 + noise)
        rainfall_rates = np.maximum(rainfall_rates, 0)  # No negative rainfall
        
        # Calculate cumulative rainfall
        cumulative_rainfall = np.cumsum(rainfall_rates) * 0.25  # Convert to mm
        
        return {
            'time_steps': time_steps,
            'rainfall_rates': rainfall_rates,
            'cumulative_rainfall': cumulative_rainfall,
            'total_rainfall': cumulative_rainfall[-1],
            'peak_intensity': np.max(rainfall_rates),
            'duration': duration_hours
        }
    
    async def _calculate_runoff(self, rainfall_data: Dict[str, Any], urban_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate runoff using SCS-CN method enhanced with ML"""
        self.logger.info("Calculating runoff using SCS-CN method")
        
        # Extract urban parameters
        population_density = urban_params.get('population_density', 5000)
        impervious_fraction = urban_params.get('impervious_fraction', self.impervious_fraction)
        drainage_efficiency = urban_params.get('drainage_efficiency', self.drainage_efficiency)
        
        # SCS-CN method parameters
        total_rainfall = rainfall_data['total_rainfall']
        time_steps = rainfall_data['time_steps']
        rainfall_rates = rainfall_data['rainfall_rates']
        
        # Calculate curve number based on urban characteristics
        cn_impervious = 98  # Impervious areas
        cn_pervious = 70    # Pervious areas
        
        # Weighted curve number
        curve_number = cn_impervious * impervious_fraction + cn_pervious * (1 - impervious_fraction)
        
        # SCS-CN calculations
        s = (25400 / curve_number) - 254  # Potential maximum retention (mm)
        ia = 0.2 * s  # Initial abstraction (mm)
        
        # Calculate runoff for each time step
        runoff_rates = []
        cumulative_runoff = []
        current_runoff = 0
        
        for i, rainfall in enumerate(rainfall_rates):
            cumulative_rainfall = rainfall_data['cumulative_rainfall'][i]
            
            if cumulative_rainfall > ia:
                # SCS-CN runoff equation
                runoff = (cumulative_rainfall - ia)**2 / (cumulative_rainfall - ia + s)
                runoff_rate = runoff - current_runoff
                current_runoff = runoff
            else:
                runoff_rate = 0
            
            # Apply drainage efficiency
            runoff_rate *= (1 - drainage_efficiency)
            
            runoff_rates.append(runoff_rate)
            cumulative_runoff.append(current_runoff)
        
        # Apply ML enhancement for urban drainage effects
        enhanced_runoff = await self._apply_ml_runoff_enhancement(
            runoff_rates, urban_params, rainfall_data
        )
        
        return {
            'time_steps': time_steps,
            'runoff_rates': enhanced_runoff,
            'cumulative_runoff': np.cumsum(enhanced_runoff),
            'total_runoff': np.sum(enhanced_runoff),
            'peak_runoff': np.max(enhanced_runoff),
            'curve_number': curve_number,
            'drainage_efficiency': drainage_efficiency
        }
    
    async def _model_flood_propagation(self, runoff_data: Dict[str, Any], request: FloodAnalysisRequest) -> Tuple[np.ndarray, float]:
        """Model flood propagation using simplified hydrodynamic simulation"""
        self.logger.info("Modeling flood propagation")
        
        # Create digital elevation model (DEM) for the area
        dem = await self._generate_dem(request.coordinates, request.area_name)
        
        # Initialize flood depth map
        flood_depth = np.zeros_like(dem)
        
        # Simplified 2D flood propagation using cellular automata approach
        total_runoff = runoff_data['total_runoff']
        peak_runoff = runoff_data['peak_runoff']
        
        # Calculate flood volume in cubic meters
        area_km2 = 10.0  # Assume 10 km² area
        flood_volume = total_runoff * area_km2 * 1000000 / 1000  # Convert to m³
        
        # Distribute flood volume based on DEM and runoff patterns
        flood_depth = await self._distribute_flood_volume(dem, flood_volume, peak_runoff)
        
        # Calculate flood extent
        flood_extent = np.sum(flood_depth > 0.01) * 100  # Area in m² with >1cm depth
        
        return flood_depth, flood_extent
    
    async def _apply_ml_depth_prediction(self, flood_depth: np.ndarray, request: FloodAnalysisRequest) -> np.ndarray:
        """Apply ML-based flood depth prediction enhancement"""
        self.logger.info("Applying ML-based flood depth prediction")
        
        # Extract features for ML prediction
        features = self._extract_flood_features(flood_depth, request)
        
        # Normalize features
        features_normalized = self.feature_scaler.fit_transform(features.reshape(-1, features.shape[-1]))
        
        # Predict enhanced flood depths
        enhanced_depths = self.flood_depth_model.predict(features_normalized)
        
        # Reshape back to original dimensions
        enhanced_depth_map = enhanced_depths.reshape(flood_depth.shape)
        
        # Apply constraints (no negative depths, reasonable maximum)
        enhanced_depth_map = np.maximum(enhanced_depth_map, 0)
        enhanced_depth_map = np.minimum(enhanced_depth_map, 5.0)  # Max 5m depth
        
        return enhanced_depth_map
    
    async def _calculate_affected_areas(self, flood_depth: np.ndarray, request: FloodAnalysisRequest) -> Dict[str, Any]:
        """Calculate affected areas and infrastructure impact"""
        self.logger.info("Calculating affected areas")
        
        # Define depth thresholds for different impact levels
        low_impact_threshold = 0.1   # 10cm
        medium_impact_threshold = 0.5  # 50cm
        high_impact_threshold = 1.0    # 1m
        
        # Calculate areas for different impact levels
        low_impact_area = np.sum(flood_depth >= low_impact_threshold) * 100  # m²
        medium_impact_area = np.sum(flood_depth >= medium_impact_threshold) * 100
        high_impact_area = np.sum(flood_depth >= high_impact_threshold) * 100
        total_affected_area = np.sum(flood_depth > 0.01) * 100
        
        # Simulate infrastructure impact
        infrastructure_impact = {
            'roads_affected': int(total_affected_area * 0.15),  # 15% of area typically roads
            'buildings_affected': int(total_affected_area * 0.25),  # 25% buildings
            'critical_facilities': int(total_affected_area * 0.05),  # 5% critical facilities
            'utilities_affected': int(total_affected_area * 0.1)   # 10% utilities
        }
        
        return {
            'total_area': float(total_affected_area),
            'low_impact_area': float(low_impact_area),
            'medium_impact_area': float(medium_impact_area),
            'high_impact_area': float(high_impact_area),
            'infrastructure_impact': infrastructure_impact
        }
    
    async def _assess_damage(self, flood_depth: np.ndarray, affected_areas: Dict[str, Any], request: FloodAnalysisRequest) -> Dict[str, Any]:
        """Assess damage using ML models"""
        self.logger.info("Assessing flood damage")
        
        # Extract damage assessment features
        features = self._extract_damage_features(flood_depth, affected_areas, request)
        
        # Normalize features
        features_normalized = self.damage_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict damage costs
        damage_prediction = self.damage_assessment_model.predict(features_normalized)[0]
        
        # Calculate detailed damage breakdown
        max_depth = np.max(flood_depth)
        total_area = affected_areas['total_area']
        
        # Damage cost per square meter based on depth
        if max_depth < 0.3:
            cost_per_m2 = 50  # Light damage
        elif max_depth < 0.8:
            cost_per_m2 = 200  # Medium damage
        elif max_depth < 1.5:
            cost_per_m2 = 500  # Heavy damage
        else:
            cost_per_m2 = 1000  # Severe damage
        
        total_economic_loss = total_area * cost_per_m2
        
        # Infrastructure damage breakdown
        infrastructure_damage = {
            'roads': affected_areas['infrastructure_impact']['roads_affected'] * 100,
            'buildings': affected_areas['infrastructure_impact']['buildings_affected'] * 200,
            'critical_facilities': affected_areas['infrastructure_impact']['critical_facilities'] * 1000,
            'utilities': affected_areas['infrastructure_impact']['utilities_affected'] * 150
        }
        
        return {
            'total_economic_loss': float(total_economic_loss),
            'infrastructure_damage': infrastructure_damage,
            'damage_severity': self._classify_damage_severity(max_depth, total_area),
            'recovery_time_days': self._estimate_recovery_time(max_depth, total_area)
        }
    
    async def _calculate_risk_assessment(self, damage_assessment: Dict[str, Any], flood_depth: np.ndarray) -> Dict[str, Any]:
        """Calculate comprehensive risk assessment"""
        self.logger.info("Calculating risk assessment")
        
        max_depth = np.max(flood_depth)
        total_area = np.sum(flood_depth > 0.01) * 100
        economic_loss = damage_assessment['total_economic_loss']
        
        # Calculate risk score (0-100)
        depth_factor = min(max_depth / 2.0, 1.0) * 40  # Max 40 points for depth
        area_factor = min(total_area / 1000000, 1.0) * 30  # Max 30 points for area
        damage_factor = min(economic_loss / 10000000, 1.0) * 30  # Max 30 points for damage
        
        risk_score = depth_factor + area_factor + damage_factor
        
        # Determine severity
        if risk_score < 25:
            severity = FloodSeverity.LOW
        elif risk_score < 50:
            severity = FloodSeverity.MODERATE
        elif risk_score < 75:
            severity = FloodSeverity.HIGH
        else:
            severity = FloodSeverity.CRITICAL
        
        # Identify risk factors
        risk_factors = []
        if max_depth > 1.0:
            risk_factors.append("High flood depths detected")
        if total_area > 500000:  # 0.5 km²
            risk_factors.append("Large affected area")
        if economic_loss > 5000000:  # $5M
            risk_factors.append("Significant economic impact")
        
        # Generate recommendations
        recommendations = self._generate_flood_recommendations(severity, risk_factors)
        
        return {
            'severity': severity,
            'risk_score': float(risk_score),
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }
    
    async def _generate_flood_alerts(self, risk_assessment: Dict[str, Any], flood_depth: np.ndarray) -> List[FloodAlert]:
        """Generate flood alerts based on risk assessment"""
        alerts = []
        
        severity = risk_assessment['severity']
        risk_score = risk_assessment['risk_score']
        max_depth = np.max(flood_depth)
        
        # Generate severity-based alerts
        if severity in [FloodSeverity.HIGH, FloodSeverity.CRITICAL]:
            alert = FloodAlert(
                alert_type="critical_flood",
                severity=severity,
                message=f"Critical flood conditions detected with risk score {risk_score:.1f}",
                affected_area=float(np.sum(flood_depth > 0.01) * 100),
                recommendation="Immediate evacuation and emergency response required"
            )
            alerts.append(alert)
        
        # Generate depth-based alerts
        if max_depth > 1.0:
            alert = FloodAlert(
                alert_type="high_depth_flood",
                severity=severity,
                message=f"High flood depths detected: {max_depth:.2f} meters",
                affected_area=float(np.sum(flood_depth > 0.01) * 100),
                recommendation="Restrict access to affected areas"
            )
            alerts.append(alert)
        
        # Generate infrastructure alerts
        if risk_score > 60:
            alert = FloodAlert(
                alert_type="infrastructure_risk",
                severity=severity,
                message="Critical infrastructure at risk",
                affected_area=float(np.sum(flood_depth > 0.01) * 100),
                recommendation="Protect critical infrastructure and utilities"
            )
            alerts.append(alert)
        
        return alerts
    
    async def _apply_ml_runoff_enhancement(self, runoff_rates: List[float], urban_params: Dict[str, Any], rainfall_data: Dict[str, Any]) -> List[float]:
        """Apply ML enhancement to runoff calculations"""
        # Extract features for ML enhancement
        features = []
        for i, runoff in enumerate(runoff_rates):
            feature_vector = [
                runoff,
                rainfall_data['rainfall_rates'][i],
                urban_params.get('population_density', 5000),
                urban_params.get('impervious_fraction', 0.7),
                urban_params.get('drainage_efficiency', 0.8),
                i / len(runoff_rates)  # Time position
            ]
            features.append(feature_vector)
        
        # Normalize features
        features_array = np.array(features)
        features_normalized = self.feature_scaler.fit_transform(features_array)
        
        # Predict enhanced runoff
        enhanced_runoff = self.runoff_model.predict(features_normalized)
        
        return enhanced_runoff.tolist()
    
    async def _generate_dem(self, coordinates: Dict[str, float], area_name: str) -> np.ndarray:
        """Generate digital elevation model for the area"""
        # Simulate DEM generation
        # In production, this would load actual DEM data
        dem_size = (200, 200)  # 200x200 grid
        dem = np.random.normal(100, 10, dem_size)  # Mean elevation 100m, std 10m
        
        # Add realistic terrain features
        x, y = np.meshgrid(np.arange(dem_size[0]), np.arange(dem_size[1]))
        dem += 5 * np.sin(x/20) + 3 * np.cos(y/15)  # Add terrain variation
        
        return dem
    
    async def _distribute_flood_volume(self, dem: np.ndarray, flood_volume: float, peak_runoff: float) -> np.ndarray:
        """Distribute flood volume based on DEM and runoff patterns"""
        # Simplified flood distribution algorithm
        flood_depth = np.zeros_like(dem)
        
        # Find low-lying areas (depressions in DEM)
        dem_smooth = cv2.GaussianBlur(dem.astype(np.float32), (5, 5), 1.0)
        depressions = dem - dem_smooth
        
        # Normalize depressions
        depressions = (depressions - np.min(depressions)) / (np.max(depressions) - np.min(depressions))
        
        # Distribute flood volume based on depressions and runoff
        total_depression_volume = np.sum(depressions)
        if total_depression_volume > 0:
            flood_depth = (flood_volume / total_depression_volume) * depressions
        else:
            # Uniform distribution if no clear depressions
            flood_depth = np.full_like(dem, flood_volume / dem.size)
        
        return flood_depth
    
    def _extract_flood_features(self, flood_depth: np.ndarray, request: FloodAnalysisRequest) -> np.ndarray:
        """Extract features for ML flood depth prediction"""
        # Calculate spatial features
        grad_x = np.gradient(flood_depth, axis=1)
        grad_y = np.gradient(flood_depth, axis=0)
        
        # Calculate local statistics
        from scipy.ndimage import uniform_filter
        local_mean = uniform_filter(flood_depth, size=5)
        local_std = uniform_filter(flood_depth**2, size=5) - local_mean**2
        
        # Stack features
        features = np.stack([
            flood_depth,
            grad_x,
            grad_y,
            local_mean,
            local_std,
            np.full_like(flood_depth, request.duration_hours),
            np.full_like(flood_depth, request.return_period)
        ], axis=-1)
        
        return features
    
    def _extract_damage_features(self, flood_depth: np.ndarray, affected_areas: Dict[str, Any], request: FloodAnalysisRequest) -> np.ndarray:
        """Extract features for damage assessment"""
        features = [
            np.max(flood_depth),  # Maximum depth
            np.mean(flood_depth),  # Average depth
            np.std(flood_depth),   # Depth variability
            affected_areas['total_area'],  # Total affected area
            affected_areas['high_impact_area'],  # High impact area
            request.duration_hours,  # Duration
            request.return_period,   # Return period
            request.urban_parameters.get('population_density', 5000),  # Population density
            request.urban_parameters.get('impervious_fraction', 0.7)   # Impervious fraction
        ]
        
        return np.array(features)
    
    def _classify_damage_severity(self, max_depth: float, total_area: float) -> str:
        """Classify damage severity"""
        if max_depth < 0.3 and total_area < 100000:
            return "minimal"
        elif max_depth < 0.8 and total_area < 500000:
            return "minor"
        elif max_depth < 1.5 and total_area < 1000000:
            return "moderate"
        elif max_depth < 2.5 and total_area < 2000000:
            return "major"
        else:
            return "catastrophic"
    
    def _estimate_recovery_time(self, max_depth: float, total_area: float) -> int:
        """Estimate recovery time in days"""
        base_time = 7  # Base recovery time
        
        depth_factor = max_depth * 10  # 10 days per meter of depth
        area_factor = total_area / 100000  # 1 day per 100,000 m²
        
        recovery_time = base_time + depth_factor + area_factor
        
        return int(min(recovery_time, 365))  # Cap at 1 year
    
    def _generate_flood_recommendations(self, severity: FloodSeverity, risk_factors: List[str]) -> List[str]:
        """Generate flood response recommendations"""
        recommendations = []
        
        if severity in [FloodSeverity.HIGH, FloodSeverity.CRITICAL]:
            recommendations.extend([
                "Activate emergency response protocols",
                "Evacuate affected areas immediately",
                "Deploy emergency services and rescue teams",
                "Establish emergency shelters",
                "Implement traffic restrictions"
            ])
        elif severity == FloodSeverity.MODERATE:
            recommendations.extend([
                "Monitor flood levels continuously",
                "Prepare evacuation plans",
                "Protect critical infrastructure",
                "Deploy sandbags and barriers",
                "Alert emergency services"
            ])
        else:
            recommendations.extend([
                "Continue monitoring flood conditions",
                "Prepare emergency response plans",
                "Maintain drainage systems",
                "Update flood risk assessments"
            ])
        
        # Add specific recommendations based on risk factors
        if "High flood depths" in risk_factors:
            recommendations.append("Implement depth-based access restrictions")
        
        if "Large affected area" in risk_factors:
            recommendations.append("Coordinate multi-agency response")
        
        if "Significant economic impact" in risk_factors:
            recommendations.append("Activate economic recovery programs")
        
        return recommendations 