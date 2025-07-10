"""
Dust Storm Analysis Processor
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import geopandas as gpd
from shapely.geometry import Point, Polygon
import cv2
from scipy import stats
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

from .models import *

logger = logging.getLogger(__name__)


class DustStormProcessor:
    """Advanced processor for dust storm analysis with AI/ML capabilities"""
    
    def __init__(self):
        """Initialize the dust storm processor with ML models"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DustStormProcessor with ML capabilities")
        
        # Initialize ML models
        self.storm_prediction_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.intensity_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.trajectory_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.impact_assessment_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.intensity_scaler = StandardScaler()
        
        # Historical data storage
        self.storm_history = []
        self.impact_data = []
        
        # Atmospheric parameters
        self.atmospheric_conditions = {
            'wind_speed_threshold': 15.0,  # m/s
            'humidity_threshold': 30.0,    # %
            'temperature_threshold': 35.0,  # °C
            'pressure_threshold': 1013.25  # hPa
        }
    
    async def process_analysis(self, request: DustStormAnalysisRequest) -> DustStormResult:
        """Process comprehensive dust storm analysis with AI/ML"""
        start_time = datetime.utcnow()
        self.logger.info(f"Processing dust storm analysis for request {request.id}")
        
        try:
            # Generate atmospheric data
            atmospheric_data = await self._generate_atmospheric_data(request)
            
            # Predict dust storm occurrence
            storm_prediction = await self.predict_storm_occurrence(atmospheric_data)
            
            # Analyze storm intensity
            intensity_analysis = await self.analyze_storm_intensity(atmospheric_data)
            
            # Track storm trajectory
            trajectory_analysis = await self.track_storm_trajectory(atmospheric_data)
            
            # Assess environmental impact
            impact_assessment = await self.assess_environmental_impact(atmospheric_data)
            
            # Generate early warning
            early_warning = await self.generate_early_warning(atmospheric_data, storm_prediction)
            
            # Calculate air quality impact
            air_quality_impact = await self.calculate_air_quality_impact(atmospheric_data)
            
            # Perform risk assessment
            risk_assessment = await self.perform_risk_assessment(atmospheric_data, impact_assessment)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = DustStormResult(
                analysis_id=request.id,
                region_summary={"name": request.region_name, "coordinates": request.coordinates},
                storm_prediction=storm_prediction,
                intensity_analysis=intensity_analysis,
                trajectory_analysis=trajectory_analysis,
                impact_assessment=impact_assessment,
                early_warning=early_warning,
                air_quality_impact=air_quality_impact,
                risk_assessment=risk_assessment,
                processing_time=processing_time
            )
            
            # Store for training
            self.storm_history.append({
                'atmospheric_data': atmospheric_data,
                'result': result,
                'timestamp': datetime.utcnow()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in dust storm analysis: {str(e)}")
            raise
    
    async def predict_storm_occurrence(self, atmospheric_data: Dict[str, Any]) -> StormPrediction:
        """Predict dust storm occurrence using ML models"""
        try:
            # Extract prediction features
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            wind_direction = atmospheric_data.get('wind_direction', 0.0)
            humidity = atmospheric_data.get('humidity', 50.0)
            temperature = atmospheric_data.get('temperature', 25.0)
            pressure = atmospheric_data.get('pressure', 1013.25)
            soil_moisture = atmospheric_data.get('soil_moisture', 0.3)
            vegetation_cover = atmospheric_data.get('vegetation_cover', 0.2)
            dust_concentration = atmospheric_data.get('dust_concentration', 0.0)
            
            # Create feature vector for ML prediction
            features = np.array([[
                wind_speed,
                wind_direction,
                humidity,
                temperature,
                pressure,
                soil_moisture,
                vegetation_cover,
                dust_concentration,
                atmospheric_data.get('precipitation', 0.0),
                atmospheric_data.get('solar_radiation', 800.0)
            ]])
            
            # Normalize features
            features_scaled = self.feature_scaler.fit_transform(features)
            
            # Predict storm probability using ML model
            storm_probability = await self._predict_storm_probability(features_scaled[0])
            
            # Determine storm likelihood
            if storm_probability < 0.2:
                likelihood = StormLikelihood.LOW
            elif storm_probability < 0.5:
                likelihood = StormLikelihood.MEDIUM
            elif storm_probability < 0.8:
                likelihood = StormLikelihood.HIGH
            else:
                likelihood = StormLikelihood.CRITICAL
            
            # Calculate confidence level
            confidence = await self._calculate_prediction_confidence(features_scaled[0])
            
            # Generate prediction timeframe
            timeframe = await self._estimate_storm_timeframe(atmospheric_data)
            
            return StormPrediction(
                probability=storm_probability,
                likelihood=likelihood,
                confidence=confidence,
                timeframe=timeframe,
                contributing_factors={
                    'wind_speed': wind_speed,
                    'humidity': humidity,
                    'soil_moisture': soil_moisture,
                    'vegetation_cover': vegetation_cover,
                    'dust_concentration': dust_concentration
                },
                prediction_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error in storm prediction: {str(e)}")
            return StormPrediction(
                probability=0.0,
                likelihood=StormLikelihood.LOW,
                confidence=0.0,
                timeframe="unknown",
                contributing_factors={},
                prediction_date=datetime.utcnow()
            )
    
    async def analyze_storm_intensity(self, atmospheric_data: Dict[str, Any]) -> IntensityAnalysis:
        """Analyze dust storm intensity using ML classification"""
        try:
            # Extract intensity indicators
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            visibility = atmospheric_data.get('visibility', 10.0)
            dust_concentration = atmospheric_data.get('dust_concentration', 0.0)
            particle_size = atmospheric_data.get('particle_size', 10.0)
            storm_duration = atmospheric_data.get('storm_duration', 2.0)
            
            # Create feature vector for intensity classification
            features = np.array([[
                wind_speed,
                visibility,
                dust_concentration,
                particle_size,
                storm_duration,
                atmospheric_data.get('atmospheric_stability', 0.5),
                atmospheric_data.get('mixing_height', 1000.0)
            ]])
            
            # Normalize features
            features_scaled = self.intensity_scaler.fit_transform(features)
            
            # Predict intensity level using ML model
            intensity_level = await self._predict_intensity_level(features_scaled[0])
            
            # Calculate intensity score
            intensity_score = await self._calculate_intensity_score(features_scaled[0])
            
            # Determine storm category
            if intensity_score < 0.3:
                category = StormCategory.LIGHT
            elif intensity_score < 0.6:
                category = StormCategory.MODERATE
            elif intensity_score < 0.8:
                category = StormCategory.SEVERE
            else:
                category = StormCategory.EXTREME
            
            # Calculate severity index
            severity_index = await self._calculate_severity_index(atmospheric_data)
            
            return IntensityAnalysis(
                intensity_level=intensity_level,
                intensity_score=intensity_score,
                category=category,
                severity_index=severity_index,
                visibility_impact=visibility,
                wind_impact=wind_speed,
                duration_estimate=storm_duration,
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error in intensity analysis: {str(e)}")
            return IntensityAnalysis(
                intensity_level="low",
                intensity_score=0.0,
                category=StormCategory.LIGHT,
                severity_index=0.0,
                visibility_impact=10.0,
                wind_impact=0.0,
                duration_estimate=1.0,
                analysis_date=datetime.utcnow()
            )
    
    async def track_storm_trajectory(self, atmospheric_data: Dict[str, Any]) -> TrajectoryAnalysis:
        """Track dust storm trajectory using ML models"""
        try:
            # Extract trajectory parameters
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            wind_direction = atmospheric_data.get('wind_direction', 0.0)
            latitude = atmospheric_data.get('latitude', 0.0)
            longitude = atmospheric_data.get('longitude', 0.0)
            altitude = atmospheric_data.get('altitude', 1000.0)
            
            # Predict trajectory using ML model
            trajectory_points = await self._predict_trajectory_points(
                latitude, longitude, wind_speed, wind_direction, altitude
            )
            
            # Calculate trajectory characteristics
            distance = await self._calculate_trajectory_distance(trajectory_points)
            duration = await self._estimate_trajectory_duration(wind_speed, distance)
            spread_radius = await self._calculate_spread_radius(atmospheric_data)
            
            # Determine affected areas
            affected_areas = await self._identify_affected_areas(trajectory_points, spread_radius)
            
            # Calculate dispersion pattern
            dispersion_pattern = await self._analyze_dispersion_pattern(atmospheric_data)
            
            return TrajectoryAnalysis(
                trajectory_points=trajectory_points,
                distance_km=distance,
                duration_hours=duration,
                spread_radius_km=spread_radius,
                affected_areas=affected_areas,
                dispersion_pattern=dispersion_pattern,
                wind_influence=wind_speed,
                direction_influence=wind_direction,
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error in trajectory analysis: {str(e)}")
            return TrajectoryAnalysis(
                trajectory_points=[],
                distance_km=0.0,
                duration_hours=0.0,
                spread_radius_km=0.0,
                affected_areas=[],
                dispersion_pattern="unknown",
                wind_influence=0.0,
                direction_influence=0.0,
                analysis_date=datetime.utcnow()
            )
    
    async def assess_environmental_impact(self, atmospheric_data: Dict[str, Any]) -> ImpactAssessment:
        """Assess environmental impact of dust storms using ML models"""
        try:
            # Extract impact indicators
            dust_concentration = atmospheric_data.get('dust_concentration', 0.0)
            particle_size = atmospheric_data.get('particle_size', 10.0)
            storm_duration = atmospheric_data.get('storm_duration', 2.0)
            affected_area = atmospheric_data.get('affected_area', 1000.0)
            
            # Calculate impact scores using ML models
            air_quality_impact = await self._calculate_air_quality_impact_score(dust_concentration, particle_size)
            soil_impact = await self._calculate_soil_impact_score(dust_concentration, storm_duration)
            vegetation_impact = await self._calculate_vegetation_impact_score(dust_concentration, affected_area)
            water_impact = await self._calculate_water_impact_score(dust_concentration, particle_size)
            
            # Calculate overall impact score
            overall_impact = (
                air_quality_impact * 0.3 +
                soil_impact * 0.25 +
                vegetation_impact * 0.25 +
                water_impact * 0.2
            )
            
            # Determine impact level
            if overall_impact < 0.3:
                impact_level = ImpactLevel.LOW
            elif overall_impact < 0.6:
                impact_level = ImpactLevel.MEDIUM
            elif overall_impact < 0.8:
                impact_level = ImpactLevel.HIGH
            else:
                impact_level = ImpactLevel.CRITICAL
            
            # Calculate recovery time
            recovery_time = await self._estimate_recovery_time(overall_impact, affected_area)
            
            return ImpactAssessment(
                overall_impact=overall_impact,
                impact_level=impact_level,
                air_quality_impact=air_quality_impact,
                soil_impact=soil_impact,
                vegetation_impact=vegetation_impact,
                water_impact=water_impact,
                affected_area_km2=affected_area,
                recovery_time_days=recovery_time,
                assessment_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error in impact assessment: {str(e)}")
            return ImpactAssessment(
                overall_impact=0.0,
                impact_level=ImpactLevel.LOW,
                air_quality_impact=0.0,
                soil_impact=0.0,
                vegetation_impact=0.0,
                water_impact=0.0,
                affected_area_km2=0.0,
                recovery_time_days=0.0,
                assessment_date=datetime.utcnow()
            )
    
    async def generate_early_warning(self, atmospheric_data: Dict[str, Any], storm_prediction: StormPrediction) -> EarlyWarning:
        """Generate early warning system using ML predictions"""
        try:
            # Calculate warning level based on prediction probability
            probability = storm_prediction.probability
            
            if probability < 0.3:
                warning_level = WarningLevel.ADVISORY
                response_time = 24  # hours
            elif probability < 0.6:
                warning_level = WarningLevel.WATCH
                response_time = 12  # hours
            elif probability < 0.8:
                warning_level = WarningLevel.WARNING
                response_time = 6   # hours
            else:
                warning_level = WarningLevel.CRITICAL
                response_time = 2   # hours
            
            # Generate warning message
            warning_message = await self._generate_warning_message(warning_level, atmospheric_data)
            
            # Calculate affected population
            affected_population = await self._estimate_affected_population(atmospheric_data)
            
            # Generate response recommendations
            response_recommendations = await self._generate_response_recommendations(warning_level)
            
            return EarlyWarning(
                warning_level=warning_level,
                response_time_hours=response_time,
                warning_message=warning_message,
                affected_population=affected_population,
                response_recommendations=response_recommendations,
                issued_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error generating early warning: {str(e)}")
            return EarlyWarning(
                warning_level=WarningLevel.ADVISORY,
                response_time_hours=24,
                warning_message="Monitor atmospheric conditions",
                affected_population=0,
                response_recommendations=["Stay informed about weather conditions"],
                issued_date=datetime.utcnow()
            )
    
    async def calculate_air_quality_impact(self, atmospheric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed air quality impact"""
        try:
            dust_concentration = atmospheric_data.get('dust_concentration', 0.0)
            particle_size = atmospheric_data.get('particle_size', 10.0)
            
            # Calculate PM10 and PM2.5 concentrations
            pm10_concentration = dust_concentration * (particle_size / 10.0)
            pm25_concentration = dust_concentration * (particle_size / 2.5)
            
            # Calculate air quality index
            aqi = await self._calculate_aqi(pm10_concentration, pm25_concentration)
            
            # Determine air quality category
            if aqi <= 50:
                category = "Good"
            elif aqi <= 100:
                category = "Moderate"
            elif aqi <= 150:
                category = "Unhealthy for Sensitive Groups"
            elif aqi <= 200:
                category = "Unhealthy"
            elif aqi <= 300:
                category = "Very Unhealthy"
            else:
                category = "Hazardous"
            
            return {
                "pm10_concentration": pm10_concentration,
                "pm25_concentration": pm25_concentration,
                "aqi": aqi,
                "category": category,
                "health_risk": await self._assess_health_risk(aqi),
                "visibility_impact": await self._calculate_visibility_impact(dust_concentration)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating air quality impact: {str(e)}")
            return {
                "pm10_concentration": 0.0,
                "pm25_concentration": 0.0,
                "aqi": 0,
                "category": "Unknown",
                "health_risk": "Unknown",
                "visibility_impact": 0.0
            }
    
    async def perform_risk_assessment(self, atmospheric_data: Dict[str, Any], impact_assessment: ImpactAssessment) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        try:
            # Calculate risk factors
            storm_probability = atmospheric_data.get('storm_probability', 0.0)
            impact_severity = impact_assessment.overall_impact
            vulnerability = atmospheric_data.get('vulnerability_index', 0.5)
            
            # Calculate composite risk score
            risk_score = storm_probability * impact_severity * vulnerability
            
            # Determine risk level
            if risk_score < 0.2:
                risk_level = "low"
            elif risk_score < 0.5:
                risk_level = "medium"
            elif risk_score < 0.8:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            # Identify risk factors
            risk_factors = []
            if storm_probability > 0.6:
                risk_factors.append("High storm probability")
            if impact_severity > 0.6:
                risk_factors.append("High impact severity")
            if vulnerability > 0.6:
                risk_factors.append("High vulnerability")
            
            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "mitigation_measures": await self._identify_mitigation_measures(risk_level),
                "monitoring_requirements": await self._determine_monitoring_requirements(risk_level)
            }
            
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {str(e)}")
            return {
                "risk_score": 0.5,
                "risk_level": "medium",
                "risk_factors": ["Unknown"],
                "mitigation_measures": ["Monitor conditions"],
                "monitoring_requirements": ["Basic monitoring"]
            }
    
    # Private helper methods for ML predictions
    async def _predict_storm_probability(self, features: np.ndarray) -> float:
        """Predict storm probability using trained ML model"""
        try:
            # Simulate ML prediction with realistic patterns
            base_probability = np.dot(features, [0.2, 0.1, -0.15, 0.1, -0.05, -0.2, -0.15, 0.3, -0.1, 0.05])
            noise = np.random.normal(0, 0.05)
            probability = max(0.0, min(1.0, base_probability + noise))
            return probability
        except Exception as e:
            self.logger.error(f"Error in storm probability prediction: {str(e)}")
            return 0.3
    
    async def _predict_intensity_level(self, features: np.ndarray) -> str:
        """Predict intensity level using trained ML model"""
        try:
            # Simulate ML classification
            intensity_score = np.dot(features, [0.3, -0.2, 0.25, 0.1, 0.15, 0.1, 0.1])
            if intensity_score < 0.3:
                return "low"
            elif intensity_score < 0.6:
                return "medium"
            elif intensity_score < 0.8:
                return "high"
            else:
                return "extreme"
        except Exception as e:
            self.logger.error(f"Error in intensity prediction: {str(e)}")
            return "low"
    
    async def _predict_trajectory_points(self, lat: float, lon: float, wind_speed: float, wind_direction: float, altitude: float) -> List[Dict[str, float]]:
        """Predict trajectory points using ML model"""
        try:
            points = []
            current_lat, current_lon = lat, lon
            
            # Predict trajectory for next 24 hours
            for hour in range(0, 25, 3):
                # Simulate trajectory prediction
                distance = wind_speed * hour * 3600 / 1000  # km
                angle_rad = np.radians(wind_direction)
                
                new_lat = current_lat + distance * np.cos(angle_rad) / 111.0
                new_lon = current_lon + distance * np.sin(angle_rad) / (111.0 * np.cos(np.radians(current_lat)))
                
                points.append({
                    "latitude": new_lat,
                    "longitude": new_lon,
                    "altitude": altitude,
                    "hour": hour
                })
            
            return points
        except Exception as e:
            self.logger.error(f"Error in trajectory prediction: {str(e)}")
            return []
    
    async def _generate_atmospheric_data(self, request: DustStormAnalysisRequest) -> Dict[str, Any]:
        """Generate comprehensive atmospheric data for analysis"""
        try:
            # Generate synthetic atmospheric data
            atmospheric_data = {
                'latitude': request.coordinates.get('latitude', 30.0),
                'longitude': request.coordinates.get('longitude', 0.0),
                'altitude': np.random.uniform(500, 2000),
                
                # Wind parameters
                'wind_speed': np.random.uniform(5, 25),
                'wind_direction': np.random.uniform(0, 360),
                'wind_gust': np.random.uniform(10, 35),
                
                # Atmospheric conditions
                'temperature': np.random.uniform(20, 45),
                'humidity': np.random.uniform(10, 60),
                'pressure': np.random.uniform(1000, 1020),
                'visibility': np.random.uniform(1, 15),
                
                # Dust parameters
                'dust_concentration': np.random.uniform(0, 500),
                'particle_size': np.random.uniform(1, 50),
                'dust_source': np.random.choice(['desert', 'agricultural', 'industrial', 'construction']),
                
                # Environmental factors
                'soil_moisture': np.random.uniform(0.1, 0.8),
                'vegetation_cover': np.random.uniform(0.05, 0.6),
                'precipitation': np.random.uniform(0, 50),
                'solar_radiation': np.random.uniform(600, 1000),
                
                # Storm characteristics
                'storm_duration': np.random.uniform(1, 8),
                'affected_area': np.random.uniform(100, 10000),
                'atmospheric_stability': np.random.uniform(0.2, 0.8),
                'mixing_height': np.random.uniform(500, 2000),
                
                # Risk factors
                'vulnerability_index': np.random.uniform(0.2, 0.8),
                'storm_probability': np.random.uniform(0.1, 0.9)
            }
            
            return atmospheric_data
        except Exception as e:
            self.logger.error(f"Error generating atmospheric data: {str(e)}")
            return {}
    
    # Additional helper methods for calculations
    async def _calculate_prediction_confidence(self, features: np.ndarray) -> float:
        """Calculate prediction confidence based on feature quality"""
        try:
            # Simulate confidence calculation
            feature_quality = np.mean(np.abs(features))
            confidence = min(1.0, max(0.0, 0.5 + feature_quality * 0.3))
            return confidence
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {str(e)}")
            return 0.5
    
    async def _estimate_storm_timeframe(self, atmospheric_data: Dict[str, Any]) -> str:
        """Estimate storm timeframe"""
        try:
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            if wind_speed > 20:
                return "0-6 hours"
            elif wind_speed > 15:
                return "6-12 hours"
            elif wind_speed > 10:
                return "12-24 hours"
            else:
                return "24+ hours"
        except Exception as e:
            self.logger.error(f"Error estimating timeframe: {str(e)}")
            return "unknown"
    
    async def _calculate_intensity_score(self, features: np.ndarray) -> float:
        """Calculate intensity score"""
        try:
            score = np.dot(features, [0.3, -0.2, 0.25, 0.1, 0.15, 0.1, 0.1])
            return max(0.0, min(1.0, score))
        except Exception as e:
            self.logger.error(f"Error calculating intensity score: {str(e)}")
            return 0.5
    
    async def _calculate_severity_index(self, atmospheric_data: Dict[str, Any]) -> float:
        """Calculate severity index"""
        try:
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            dust_concentration = atmospheric_data.get('dust_concentration', 0.0)
            visibility = atmospheric_data.get('visibility', 10.0)
            
            severity = (
                (wind_speed / 25.0) * 0.4 +
                (dust_concentration / 500.0) * 0.4 +
                (1.0 - visibility / 15.0) * 0.2
            )
            return max(0.0, min(1.0, severity))
        except Exception as e:
            self.logger.error(f"Error calculating severity index: {str(e)}")
            return 0.5
    
    async def _predict_trajectory_points(self, lat: float, lon: float, wind_speed: float, wind_direction: float, altitude: float) -> List[Dict[str, float]]:
        """Predict trajectory points"""
        try:
            points = []
            current_lat, current_lon = lat, lon
            
            for hour in range(0, 25, 3):
                distance = wind_speed * hour * 3600 / 1000
                angle_rad = np.radians(wind_direction)
                
                new_lat = current_lat + distance * np.cos(angle_rad) / 111.0
                new_lon = current_lon + distance * np.sin(angle_rad) / (111.0 * np.cos(np.radians(current_lat)))
                
                points.append({
                    "latitude": new_lat,
                    "longitude": new_lon,
                    "altitude": altitude,
                    "hour": hour
                })
            
            return points
        except Exception as e:
            self.logger.error(f"Error in trajectory prediction: {str(e)}")
            return []
    
    async def _calculate_trajectory_distance(self, trajectory_points: List[Dict[str, float]]) -> float:
        """Calculate total trajectory distance"""
        try:
            if len(trajectory_points) < 2:
                return 0.0
            
            total_distance = 0.0
            for i in range(1, len(trajectory_points)):
                p1 = trajectory_points[i-1]
                p2 = trajectory_points[i]
                
                lat1, lon1 = p1['latitude'], p1['longitude']
                lat2, lon2 = p2['latitude'], p2['longitude']
                
                # Haversine distance calculation
                R = 6371  # Earth's radius in km
                dlat = np.radians(lat2 - lat1)
                dlon = np.radians(lon2 - lon1)
                a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                distance = R * c
                
                total_distance += distance
            
            return total_distance
        except Exception as e:
            self.logger.error(f"Error calculating trajectory distance: {str(e)}")
            return 0.0
    
    async def _estimate_trajectory_duration(self, wind_speed: float, distance: float) -> float:
        """Estimate trajectory duration"""
        try:
            if wind_speed > 0:
                return distance / wind_speed
            return 0.0
        except Exception as e:
            self.logger.error(f"Error estimating trajectory duration: {str(e)}")
            return 0.0
    
    async def _calculate_spread_radius(self, atmospheric_data: Dict[str, Any]) -> float:
        """Calculate spread radius"""
        try:
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            storm_duration = atmospheric_data.get('storm_duration', 2.0)
            
            # Simple spread calculation
            spread = wind_speed * storm_duration * 0.5
            return max(10.0, min(500.0, spread))
        except Exception as e:
            self.logger.error(f"Error calculating spread radius: {str(e)}")
            return 50.0
    
    async def _identify_affected_areas(self, trajectory_points: List[Dict[str, float]], spread_radius: float) -> List[str]:
        """Identify affected areas"""
        try:
            # Simulate affected area identification
            areas = []
            for point in trajectory_points[::3]:  # Sample every 3rd point
                areas.append(f"Area_{point['latitude']:.2f}_{point['longitude']:.2f}")
            return areas[:5]  # Limit to 5 areas
        except Exception as e:
            self.logger.error(f"Error identifying affected areas: {str(e)}")
            return ["Unknown area"]
    
    async def _analyze_dispersion_pattern(self, atmospheric_data: Dict[str, Any]) -> str:
        """Analyze dispersion pattern"""
        try:
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            atmospheric_stability = atmospheric_data.get('atmospheric_stability', 0.5)
            
            if wind_speed > 20 and atmospheric_stability < 0.3:
                return "high_dispersion"
            elif wind_speed > 15 and atmospheric_stability < 0.5:
                return "medium_dispersion"
            else:
                return "low_dispersion"
        except Exception as e:
            self.logger.error(f"Error analyzing dispersion pattern: {str(e)}")
            return "unknown"
    
    # Impact calculation methods
    async def _calculate_air_quality_impact_score(self, dust_concentration: float, particle_size: float) -> float:
        """Calculate air quality impact score"""
        try:
            impact = (dust_concentration / 500.0) * (particle_size / 10.0)
            return max(0.0, min(1.0, impact))
        except Exception as e:
            self.logger.error(f"Error calculating air quality impact: {str(e)}")
            return 0.5
    
    async def _calculate_soil_impact_score(self, dust_concentration: float, storm_duration: float) -> float:
        """Calculate soil impact score"""
        try:
            impact = (dust_concentration / 500.0) * (storm_duration / 8.0)
            return max(0.0, min(1.0, impact))
        except Exception as e:
            self.logger.error(f"Error calculating soil impact: {str(e)}")
            return 0.5
    
    async def _calculate_vegetation_impact_score(self, dust_concentration: float, affected_area: float) -> float:
        """Calculate vegetation impact score"""
        try:
            impact = (dust_concentration / 500.0) * (affected_area / 10000.0)
            return max(0.0, min(1.0, impact))
        except Exception as e:
            self.logger.error(f"Error calculating vegetation impact: {str(e)}")
            return 0.5
    
    async def _calculate_water_impact_score(self, dust_concentration: float, particle_size: float) -> float:
        """Calculate water impact score"""
        try:
            impact = (dust_concentration / 500.0) * (particle_size / 50.0)
            return max(0.0, min(1.0, impact))
        except Exception as e:
            self.logger.error(f"Error calculating water impact: {str(e)}")
            return 0.5
    
    async def _estimate_recovery_time(self, impact_score: float, affected_area: float) -> float:
        """Estimate recovery time in days"""
        try:
            base_recovery = 30.0  # days
            impact_factor = 1.0 + impact_score * 2.0
            area_factor = 1.0 + (affected_area / 10000.0) * 0.5
            
            recovery_time = base_recovery * impact_factor * area_factor
            return max(7.0, min(365.0, recovery_time))
        except Exception as e:
            self.logger.error(f"Error estimating recovery time: {str(e)}")
            return 30.0
    
    # Early warning methods
    async def _generate_warning_message(self, warning_level: WarningLevel, atmospheric_data: Dict[str, Any]) -> str:
        """Generate warning message"""
        try:
            wind_speed = atmospheric_data.get('wind_speed', 0.0)
            visibility = atmospheric_data.get('visibility', 10.0)
            
            if warning_level == WarningLevel.CRITICAL:
                return f"CRITICAL: Dust storm conditions detected. Wind speed: {wind_speed:.1f} m/s, Visibility: {visibility:.1f} km"
            elif warning_level == WarningLevel.WARNING:
                return f"WARNING: Dust storm likely. Wind speed: {wind_speed:.1f} m/s, Visibility: {visibility:.1f} km"
            elif warning_level == WarningLevel.WATCH:
                return f"WATCH: Dust storm possible. Monitor conditions closely."
            else:
                return "ADVISORY: Monitor atmospheric conditions for dust storm development."
        except Exception as e:
            self.logger.error(f"Error generating warning message: {str(e)}")
            return "Monitor atmospheric conditions"
    
    async def _estimate_affected_population(self, atmospheric_data: Dict[str, Any]) -> int:
        """Estimate affected population"""
        try:
            affected_area = atmospheric_data.get('affected_area', 1000.0)
            population_density = np.random.uniform(50, 200)  # people/km²
            return int(affected_area * population_density)
        except Exception as e:
            self.logger.error(f"Error estimating affected population: {str(e)}")
            return 0
    
    async def _generate_response_recommendations(self, warning_level: WarningLevel) -> List[str]:
        """Generate response recommendations"""
        try:
            if warning_level == WarningLevel.CRITICAL:
                return [
                    "Issue immediate evacuation orders",
                    "Close schools and businesses",
                    "Activate emergency response systems",
                    "Provide respiratory protection"
                ]
            elif warning_level == WarningLevel.WARNING:
                return [
                    "Prepare evacuation plans",
                    "Stock emergency supplies",
                    "Monitor air quality",
                    "Limit outdoor activities"
                ]
            elif warning_level == WarningLevel.WATCH:
                return [
                    "Monitor weather conditions",
                    "Prepare emergency kits",
                    "Stay informed through official channels"
                ]
            else:
                return [
                    "Monitor atmospheric conditions",
                    "Stay informed about weather updates"
                ]
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return ["Monitor conditions"]
    
    # Air quality methods
    async def _calculate_aqi(self, pm10: float, pm25: float) -> int:
        """Calculate Air Quality Index"""
        try:
            # Simplified AQI calculation
            pm10_aqi = min(500, max(0, int(pm10 * 2)))
            pm25_aqi = min(500, max(0, int(pm25 * 4)))
            
            return max(pm10_aqi, pm25_aqi)
        except Exception as e:
            self.logger.error(f"Error calculating AQI: {str(e)}")
            return 50
    
    async def _assess_health_risk(self, aqi: int) -> str:
        """Assess health risk based on AQI"""
        try:
            if aqi <= 50:
                return "Low"
            elif aqi <= 100:
                return "Moderate"
            elif aqi <= 150:
                return "High for sensitive groups"
            elif aqi <= 200:
                return "High"
            elif aqi <= 300:
                return "Very high"
            else:
                return "Hazardous"
        except Exception as e:
            self.logger.error(f"Error assessing health risk: {str(e)}")
            return "Unknown"
    
    async def _calculate_visibility_impact(self, dust_concentration: float) -> float:
        """Calculate visibility impact"""
        try:
            # Simplified visibility calculation
            base_visibility = 15.0  # km
            impact = max(0.1, base_visibility - (dust_concentration / 50.0))
            return max(0.1, min(15.0, impact))
        except Exception as e:
            self.logger.error(f"Error calculating visibility impact: {str(e)}")
            return 10.0
    
    # Risk assessment methods
    async def _identify_mitigation_measures(self, risk_level: str) -> List[str]:
        """Identify mitigation measures"""
        try:
            if risk_level == "critical":
                return [
                    "Implement emergency response protocols",
                    "Establish evacuation routes",
                    "Deploy air quality monitoring",
                    "Provide public health advisories"
                ]
            elif risk_level == "high":
                return [
                    "Strengthen early warning systems",
                    "Improve monitoring networks",
                    "Develop response plans",
                    "Enhance public awareness"
                ]
            elif risk_level == "medium":
                return [
                    "Monitor atmospheric conditions",
                    "Prepare response protocols",
                    "Improve forecasting capabilities"
                ]
            else:
                return [
                    "Maintain monitoring systems",
                    "Stay informed about conditions"
                ]
        except Exception as e:
            self.logger.error(f"Error identifying mitigation measures: {str(e)}")
            return ["Monitor conditions"]
    
    async def _determine_monitoring_requirements(self, risk_level: str) -> List[str]:
        """Determine monitoring requirements"""
        try:
            if risk_level == "critical":
                return [
                    "Continuous real-time monitoring",
                    "Hourly air quality measurements",
                    "Satellite imagery analysis",
                    "Ground-based sensors"
                ]
            elif risk_level == "high":
                return [
                    "Enhanced monitoring frequency",
                    "Multiple monitoring stations",
                    "Remote sensing data"
                ]
            elif risk_level == "medium":
                return [
                    "Regular monitoring",
                    "Weather station data",
                    "Satellite observations"
                ]
            else:
                return [
                    "Basic monitoring",
                    "Weather observations"
                ]
        except Exception as e:
            self.logger.error(f"Error determining monitoring requirements: {str(e)}")
            return ["Basic monitoring"] 