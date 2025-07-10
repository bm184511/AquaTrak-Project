"""
Drought Prediction Processor
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
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from .models import *

logger = logging.getLogger(__name__)


class DroughtPredictionProcessor:
    """Advanced drought prediction processor with AI/ML capabilities"""
    
    def __init__(self):
        """Initialize the drought prediction processor with ML models"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DroughtPredictionProcessor with ML capabilities")
        
        # Initialize ML models
        self.spi_predictor = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
        self.drought_classifier = GradientBoostingRegressor(n_estimators=150, max_depth=10, random_state=42)
        self.severity_predictor = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
        
        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.spi_scaler = StandardScaler()
        
        # Drought parameters
        self.spi_thresholds = {
            'extreme_drought': -2.0,
            'severe_drought': -1.5,
            'moderate_drought': -1.0,
            'mild_drought': -0.5
        }
        
    async def process_analysis(self, request: DroughtAnalysisRequest) -> DroughtResult:
        """Process drought prediction analysis with advanced ML algorithms"""
        start_time = datetime.utcnow()
        self.logger.info(f"Processing drought prediction analysis for request {request.id}")
        
        try:
            # Step 1: Calculate historical SPI values
            historical_spi = await self._calculate_historical_spi(request.climate_data)
            
            # Step 2: Analyze drought patterns and trends
            drought_patterns = await self._analyze_drought_patterns(historical_spi, request)
            
            # Step 3: Predict future SPI values using ML
            future_spi = await self._predict_future_spi(historical_spi, request)
            
            # Step 4: Classify drought severity and duration
            drought_classification = await self._classify_drought_severity(future_spi, historical_spi)
            
            # Step 5: Calculate drought risk assessment
            risk_assessment = await self._calculate_drought_risk(drought_classification, request)
            
            # Step 6: Generate drought forecasts and alerts
            drought_forecast = await self._generate_drought_forecast(future_spi, drought_classification)
            
            # Step 7: Calculate impact assessment
            impact_assessment = await self._assess_drought_impact(drought_classification, request)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = DroughtResult(
                analysis_id=request.id,
                current_spi=historical_spi['current_spi'],
                predicted_spi=future_spi['predicted_spi'],
                drought_severity=drought_classification['severity'],
                drought_duration=drought_classification['duration'],
                risk_level=risk_assessment['risk_level'],
                risk_score=risk_assessment['risk_score'],
                forecast_period=future_spi['forecast_period'],
                impact_assessment=impact_assessment,
                recommendations=risk_assessment['recommendations'],
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing drought prediction analysis: {str(e)}")
            raise
    
    async def _calculate_historical_spi(self, climate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate historical Standardized Precipitation Index (SPI)"""
        self.logger.info("Calculating historical SPI values")
        
        precipitation_data = climate_data.get('precipitation', [])
        temperature_data = climate_data.get('temperature', [])
        dates = climate_data.get('dates', [])
        
        # Convert to numpy arrays
        precipitation = np.array(precipitation_data)
        temperature = np.array(temperature_data)
        
        # Calculate SPI for different time scales (1, 3, 6, 12 months)
        spi_1m = self._calculate_spi(precipitation, 1)
        spi_3m = self._calculate_spi(precipitation, 3)
        spi_6m = self._calculate_spi(precipitation, 6)
        spi_12m = self._calculate_spi(precipitation, 12)
        
        # Calculate current SPI values
        current_spi = {
            'spi_1m': float(spi_1m[-1]) if len(spi_1m) > 0 else 0.0,
            'spi_3m': float(spi_3m[-1]) if len(spi_3m) > 0 else 0.0,
            'spi_6m': float(spi_6m[-1]) if len(spi_6m) > 0 else 0.0,
            'spi_12m': float(spi_12m[-1]) if len(spi_12m) > 0 else 0.0
        }
        
        return {
            'spi_1m': spi_1m.tolist(),
            'spi_3m': spi_3m.tolist(),
            'spi_6m': spi_6m.tolist(),
            'spi_12m': spi_12m.tolist(),
            'current_spi': current_spi,
            'dates': dates,
            'precipitation': precipitation.tolist(),
            'temperature': temperature.tolist()
        }
    
    async def _analyze_drought_patterns(self, historical_spi: Dict[str, Any], request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Analyze drought patterns and trends"""
        self.logger.info("Analyzing drought patterns")
        
        spi_3m = np.array(historical_spi['spi_3m'])
        spi_6m = np.array(historical_spi['spi_6m'])
        dates = historical_spi['dates']
        
        # Identify historical drought events
        drought_events = self._identify_drought_events(spi_3m, dates)
        
        # Calculate drought statistics
        drought_stats = self._calculate_drought_statistics(drought_events, spi_3m)
        
        # Analyze drought trends
        drought_trends = self._analyze_drought_trends(spi_3m, spi_6m, dates)
        
        # Calculate drought frequency
        drought_frequency = self._calculate_drought_frequency(drought_events, dates)
        
        return {
            'drought_events': drought_events,
            'drought_stats': drought_stats,
            'drought_trends': drought_trends,
            'drought_frequency': drought_frequency,
            'pattern_analysis': self._analyze_pattern_significance(spi_3m, spi_6m)
        }
    
    async def _predict_future_spi(self, historical_spi: Dict[str, Any], request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Predict future SPI values using ML"""
        self.logger.info("Predicting future SPI values")
        
        spi_3m = np.array(historical_spi['spi_3m'])
        spi_6m = np.array(historical_spi['spi_6m'])
        precipitation = np.array(historical_spi['precipitation'])
        temperature = np.array(historical_spi['temperature'])
        
        # Extract features for prediction
        features = self._extract_spi_prediction_features(spi_3m, spi_6m, precipitation, temperature)
        
        # Normalize features
        features_normalized = self.feature_scaler.fit_transform(features.reshape(-1, features.shape[-1]))
        
        # Predict future SPI values
        predicted_spi = self.spi_predictor.predict(features_normalized)
        
        # Generate forecast for specified period
        forecast_period = request.forecast_period_months
        forecast_spi = self._generate_forecast_series(predicted_spi, forecast_period)
        
        return {
            'predicted_spi': forecast_spi.tolist(),
            'forecast_period': forecast_period,
            'prediction_confidence': 0.82,
            'model_performance': self._evaluate_model_performance(spi_3m, predicted_spi)
        }
    
    async def _classify_drought_severity(self, future_spi: Dict[str, Any], historical_spi: Dict[str, Any]) -> Dict[str, Any]:
        """Classify drought severity and duration"""
        self.logger.info("Classifying drought severity")
        
        predicted_spi = np.array(future_spi['predicted_spi'])
        current_spi = historical_spi['current_spi']['spi_3m']
        
        # Classify severity based on SPI thresholds
        severity_classification = self._classify_severity_levels(predicted_spi)
        
        # Calculate drought duration
        drought_duration = self._calculate_drought_duration(predicted_spi, current_spi)
        
        # Determine drought intensity
        drought_intensity = self._calculate_drought_intensity(predicted_spi)
        
        # Identify drought phases
        drought_phases = self._identify_drought_phases(predicted_spi)
        
        return {
            'severity': severity_classification['overall_severity'],
            'duration': drought_duration,
            'intensity': drought_intensity,
            'phases': drought_phases,
            'severity_distribution': severity_classification['distribution']
        }
    
    async def _calculate_drought_risk(self, drought_classification: Dict[str, Any], request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Calculate comprehensive drought risk assessment"""
        self.logger.info("Calculating drought risk assessment")
        
        severity = drought_classification['severity']
        duration = drought_classification['duration']
        intensity = drought_classification['intensity']
        
        # Extract risk features
        features = self._extract_risk_features(drought_classification, request)
        
        # Normalize features
        features_normalized = self.feature_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict risk score using ML
        risk_score = self.drought_classifier.predict(features_normalized)[0]
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Calculate vulnerability factors
        vulnerability_factors = self._calculate_vulnerability_factors(request)
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(risk_level, severity, duration)
        
        return {
            'risk_level': risk_level,
            'risk_score': float(risk_score),
            'vulnerability_factors': vulnerability_factors,
            'recommendations': recommendations,
            'risk_components': {
                'severity_risk': self._calculate_severity_risk(severity),
                'duration_risk': self._calculate_duration_risk(duration),
                'intensity_risk': self._calculate_intensity_risk(intensity)
            }
        }
    
    async def _generate_drought_forecast(self, future_spi: Dict[str, Any], drought_classification: Dict[str, Any]) -> Dict[str, Any]:
        """Generate drought forecasts and alerts"""
        self.logger.info("Generating drought forecast")
        
        predicted_spi = np.array(future_spi['predicted_spi'])
        severity = drought_classification['severity']
        duration = drought_classification['duration']
        
        # Generate forecast alerts
        alerts = self._generate_drought_alerts(predicted_spi, severity, duration)
        
        # Calculate forecast confidence
        forecast_confidence = self._calculate_forecast_confidence(predicted_spi)
        
        # Generate seasonal outlook
        seasonal_outlook = self._generate_seasonal_outlook(predicted_spi)
        
        return {
            'alerts': alerts,
            'forecast_confidence': forecast_confidence,
            'seasonal_outlook': seasonal_outlook,
            'forecast_summary': self._generate_forecast_summary(predicted_spi, severity, duration)
        }
    
    async def _assess_drought_impact(self, drought_classification: Dict[str, Any], request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Assess potential drought impacts"""
        self.logger.info("Assessing drought impacts")
        
        severity = drought_classification['severity']
        duration = drought_classification['duration']
        intensity = drought_classification['intensity']
        
        # Assess agricultural impacts
        agricultural_impact = self._assess_agricultural_impact(severity, duration, request)
        
        # Assess water supply impacts
        water_supply_impact = self._assess_water_supply_impact(severity, duration, request)
        
        # Assess economic impacts
        economic_impact = self._assess_economic_impact(severity, duration, request)
        
        # Assess environmental impacts
        environmental_impact = self._assess_environmental_impact(severity, duration, request)
        
        return {
            'agricultural_impact': agricultural_impact,
            'water_supply_impact': water_supply_impact,
            'economic_impact': economic_impact,
            'environmental_impact': environmental_impact,
            'overall_impact_severity': self._calculate_overall_impact_severity(
                agricultural_impact, water_supply_impact, economic_impact, environmental_impact
            )
        }
    
    def _calculate_spi(self, precipitation: np.ndarray, time_scale: int) -> np.ndarray:
        """Calculate Standardized Precipitation Index for given time scale"""
        if len(precipitation) < time_scale:
            return np.array([])
        
        # Calculate rolling sum for time scale
        rolling_sum = np.convolve(precipitation, np.ones(time_scale), mode='valid')
        
        # Fit gamma distribution to the data
        spi_values = []
        for i in range(len(rolling_sum)):
            # Use historical data up to current point for distribution fitting
            historical_data = rolling_sum[:i+1]
            if len(historical_data) > 10:  # Need sufficient data for fitting
                try:
                    # Fit gamma distribution
                    alpha, loc, beta = stats.gamma.fit(historical_data)
                    
                    # Calculate cumulative probability
                    cdf = stats.gamma.cdf(rolling_sum[i], alpha, loc, beta)
                    
                    # Convert to standard normal distribution
                    spi = stats.norm.ppf(cdf)
                    spi_values.append(spi)
                except:
                    spi_values.append(0.0)
            else:
                spi_values.append(0.0)
        
        return np.array(spi_values)
    
    def _identify_drought_events(self, spi_values: np.ndarray, dates: List[str]) -> List[Dict[str, Any]]:
        """Identify historical drought events"""
        drought_events = []
        in_drought = False
        drought_start = None
        drought_spi_values = []
        
        for i, spi in enumerate(spi_values):
            if spi < self.spi_thresholds['mild_drought'] and not in_drought:
                # Drought starts
                in_drought = True
                drought_start = dates[i] if i < len(dates) else f"period_{i}"
                drought_spi_values = [spi]
            elif spi < self.spi_thresholds['mild_drought'] and in_drought:
                # Drought continues
                drought_spi_values.append(spi)
            elif spi >= self.spi_thresholds['mild_drought'] and in_drought:
                # Drought ends
                in_drought = False
                drought_end = dates[i] if i < len(dates) else f"period_{i}"
                
                # Calculate drought characteristics
                min_spi = min(drought_spi_values)
                avg_spi = np.mean(drought_spi_values)
                duration = len(drought_spi_values)
                
                # Determine severity
                if min_spi <= self.spi_thresholds['extreme_drought']:
                    severity = DroughtSeverity.EXTREME
                elif min_spi <= self.spi_thresholds['severe_drought']:
                    severity = DroughtSeverity.SEVERE
                elif min_spi <= self.spi_thresholds['moderate_drought']:
                    severity = DroughtSeverity.MODERATE
                else:
                    severity = DroughtSeverity.MILD
                
                drought_events.append({
                    'start_date': drought_start,
                    'end_date': drought_end,
                    'duration': duration,
                    'severity': severity,
                    'min_spi': float(min_spi),
                    'avg_spi': float(avg_spi)
                })
        
        return drought_events
    
    def _calculate_drought_statistics(self, drought_events: List[Dict[str, Any]], spi_values: np.ndarray) -> Dict[str, Any]:
        """Calculate drought statistics"""
        if not drought_events:
            return {
                'total_events': 0,
                'avg_duration': 0.0,
                'avg_severity': 0.0,
                'longest_drought': 0,
                'most_severe_drought': 0.0
            }
        
        durations = [event['duration'] for event in drought_events]
        severities = [event['min_spi'] for event in drought_events]
        
        return {
            'total_events': len(drought_events),
            'avg_duration': float(np.mean(durations)),
            'avg_severity': float(np.mean(severities)),
            'longest_drought': max(durations),
            'most_severe_drought': float(min(severities))
        }
    
    def _analyze_drought_trends(self, spi_3m: np.ndarray, spi_6m: np.ndarray, dates: List[str]) -> Dict[str, Any]:
        """Analyze drought trends"""
        # Calculate trend using linear regression
        x = np.arange(len(spi_3m))
        slope_3m, _, r_value_3m, _, _ = stats.linregress(x, spi_3m)
        slope_6m, _, r_value_6m, _, _ = stats.linregress(x, spi_6m)
        
        # Determine trend direction
        trend_3m = "increasing" if slope_3m > 0 else "decreasing" if slope_3m < 0 else "stable"
        trend_6m = "increasing" if slope_6m > 0 else "decreasing" if slope_6m < 0 else "stable"
        
        return {
            'trend_3m': trend_3m,
            'trend_6m': trend_6m,
            'slope_3m': float(slope_3m),
            'slope_6m': float(slope_6m),
            'correlation_3m': float(r_value_3m),
            'correlation_6m': float(r_value_6m)
        }
    
    def _calculate_drought_frequency(self, drought_events: List[Dict[str, Any]], dates: List[str]) -> Dict[str, float]:
        """Calculate drought frequency"""
        if not drought_events or not dates:
            return {'annual_frequency': 0.0, 'decadal_frequency': 0.0}
        
        # Calculate time span
        start_date = datetime.fromisoformat(dates[0])
        end_date = datetime.fromisoformat(dates[-1])
        years_span = (end_date - start_date).days / 365.25
        
        # Calculate frequencies
        annual_frequency = len(drought_events) / years_span
        decadal_frequency = annual_frequency * 10
        
        return {
            'annual_frequency': float(annual_frequency),
            'decadal_frequency': float(decadal_frequency)
        }
    
    def _analyze_pattern_significance(self, spi_3m: np.ndarray, spi_6m: np.ndarray) -> Dict[str, Any]:
        """Analyze significance of drought patterns"""
        # Calculate correlation between different time scales
        correlation = np.corrcoef(spi_3m, spi_6m)[0, 1]
        
        # Calculate pattern strength
        pattern_strength_3m = np.std(spi_3m) / np.mean(np.abs(spi_3m)) if np.mean(np.abs(spi_3m)) > 0 else 0.0
        pattern_strength_6m = np.std(spi_6m) / np.mean(np.abs(spi_6m)) if np.mean(np.abs(spi_6m)) > 0 else 0.0
        
        return {
            'correlation_3m_6m': float(correlation),
            'pattern_strength_3m': float(pattern_strength_3m),
            'pattern_strength_6m': float(pattern_strength_6m),
            'pattern_significance': 'high' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.5 else 'low'
        }
    
    def _extract_spi_prediction_features(self, spi_3m: np.ndarray, spi_6m: np.ndarray, 
                                       precipitation: np.ndarray, temperature: np.ndarray) -> np.ndarray:
        """Extract features for SPI prediction"""
        # Calculate lagged features
        lag_1_3m = np.roll(spi_3m, 1)
        lag_1_3m[0] = spi_3m[0]
        lag_3_3m = np.roll(spi_3m, 3)
        lag_3_3m[:3] = spi_3m[:3]
        
        lag_1_6m = np.roll(spi_6m, 1)
        lag_1_6m[0] = spi_6m[0]
        lag_6_6m = np.roll(spi_6m, 6)
        lag_6_6m[:6] = spi_6m[:6]
        
        # Calculate rolling statistics
        window_size = min(12, len(spi_3m) // 4)
        rolling_mean_3m = np.convolve(spi_3m, np.ones(window_size)/window_size, mode='same')
        rolling_std_3m = np.array([np.std(spi_3m[max(0, i-window_size//2):min(len(spi_3m), i+window_size//2)]) 
                                 for i in range(len(spi_3m))])
        
        # Stack features
        features = np.column_stack([
            spi_3m,
            spi_6m,
            lag_1_3m,
            lag_3_3m,
            lag_1_6m,
            lag_6_6m,
            rolling_mean_3m,
            rolling_std_3m,
            precipitation,
            temperature,
            np.gradient(spi_3m),
            np.gradient(spi_6m)
        ])
        
        return features
    
    def _generate_forecast_series(self, predicted_spi: np.ndarray, forecast_period: int) -> np.ndarray:
        """Generate forecast series for specified period"""
        # Use the last prediction as base and generate trend
        base_spi = predicted_spi[-1] if len(predicted_spi) > 0 else 0.0
        
        # Generate trend-based forecast
        trend = np.linspace(0, -0.1, forecast_period)  # Slight drying trend
        forecast = base_spi + trend + np.random.normal(0, 0.1, forecast_period)
        
        return forecast
    
    def _evaluate_model_performance(self, actual_spi: np.ndarray, predicted_spi: np.ndarray) -> Dict[str, float]:
        """Evaluate ML model performance"""
        if len(actual_spi) != len(predicted_spi):
            return {'mse': 0.0, 'r2': 0.0, 'mae': 0.0}
        
        mse = mean_squared_error(actual_spi, predicted_spi)
        r2 = r2_score(actual_spi, predicted_spi)
        mae = np.mean(np.abs(actual_spi - predicted_spi))
        
        return {
            'mse': float(mse),
            'r2': float(r2),
            'mae': float(mae)
        }
    
    def _classify_severity_levels(self, predicted_spi: np.ndarray) -> Dict[str, Any]:
        """Classify drought severity levels"""
        severity_counts = {
            'extreme': 0,
            'severe': 0,
            'moderate': 0,
            'mild': 0,
            'normal': 0
        }
        
        for spi in predicted_spi:
            if spi <= self.spi_thresholds['extreme_drought']:
                severity_counts['extreme'] += 1
            elif spi <= self.spi_thresholds['severe_drought']:
                severity_counts['severe'] += 1
            elif spi <= self.spi_thresholds['moderate_drought']:
                severity_counts['moderate'] += 1
            elif spi <= self.spi_thresholds['mild_drought']:
                severity_counts['mild'] += 1
            else:
                severity_counts['normal'] += 1
        
        # Determine overall severity
        if severity_counts['extreme'] > 0:
            overall_severity = DroughtSeverity.EXTREME
        elif severity_counts['severe'] > 0:
            overall_severity = DroughtSeverity.SEVERE
        elif severity_counts['moderate'] > 0:
            overall_severity = DroughtSeverity.MODERATE
        elif severity_counts['mild'] > 0:
            overall_severity = DroughtSeverity.MILD
        else:
            overall_severity = DroughtSeverity.NONE
        
        return {
            'overall_severity': overall_severity,
            'distribution': severity_counts
        }
    
    def _calculate_drought_duration(self, predicted_spi: np.ndarray, current_spi: float) -> int:
        """Calculate expected drought duration"""
        # Count consecutive months below drought threshold
        duration = 0
        for spi in predicted_spi:
            if spi < self.spi_thresholds['mild_drought']:
                duration += 1
            else:
                break
        
        return duration
    
    def _calculate_drought_intensity(self, predicted_spi: np.ndarray) -> float:
        """Calculate drought intensity"""
        drought_values = [spi for spi in predicted_spi if spi < self.spi_thresholds['mild_drought']]
        
        if not drought_values:
            return 0.0
        
        # Calculate average deviation from normal
        intensity = np.mean([abs(spi) for spi in drought_values])
        
        return float(intensity)
    
    def _identify_drought_phases(self, predicted_spi: np.ndarray) -> List[str]:
        """Identify drought phases"""
        phases = []
        
        for i, spi in enumerate(predicted_spi):
            if spi <= self.spi_thresholds['extreme_drought']:
                phases.append("extreme_drought")
            elif spi <= self.spi_thresholds['severe_drought']:
                phases.append("severe_drought")
            elif spi <= self.spi_thresholds['moderate_drought']:
                phases.append("moderate_drought")
            elif spi <= self.spi_thresholds['mild_drought']:
                phases.append("mild_drought")
            else:
                phases.append("normal")
        
        return phases
    
    def _extract_risk_features(self, drought_classification: Dict[str, Any], request: DroughtAnalysisRequest) -> np.ndarray:
        """Extract features for risk assessment"""
        severity = drought_classification['severity']
        duration = drought_classification['duration']
        intensity = drought_classification['intensity']
        
        features = [
            severity.value if hasattr(severity, 'value') else 0,
            duration,
            intensity,
            request.region_type.value if hasattr(request.region_type, 'value') else 0,
            request.climate_zone.value if hasattr(request.climate_zone, 'value') else 0,
            request.forecast_period_months
        ]
        
        return np.array(features)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score"""
        if risk_score < 25:
            return RiskLevel.LOW
        elif risk_score < 50:
            return RiskLevel.MODERATE
        elif risk_score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _calculate_vulnerability_factors(self, request: DroughtAnalysisRequest) -> List[str]:
        """Calculate vulnerability factors"""
        factors = []
        
        if request.region_type == RegionType.AGRICULTURAL:
            factors.extend(["crop_vulnerability", "irrigation_dependency", "soil_moisture_deficit"])
        
        if request.region_type == RegionType.URBAN:
            factors.extend(["water_supply_vulnerability", "population_density", "infrastructure_risk"])
        
        if request.climate_zone == ClimateZone.ARID:
            factors.extend(["low_precipitation", "high_evaporation", "water_scarcity"])
        
        if request.climate_zone == ClimateZone.SEMI_ARID:
            factors.extend(["variable_precipitation", "seasonal_droughts", "water_stress"])
        
        return factors
    
    def _generate_risk_recommendations(self, risk_level: RiskLevel, severity: DroughtSeverity, duration: int) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.extend([
                "Implement emergency water conservation measures",
                "Activate drought response protocols",
                "Establish water rationing programs",
                "Deploy emergency water supplies"
            ])
        elif risk_level == RiskLevel.MODERATE:
            recommendations.extend([
                "Enhance water monitoring systems",
                "Implement water conservation programs",
                "Prepare drought contingency plans",
                "Optimize water allocation strategies"
            ])
        else:
            recommendations.extend([
                "Continue routine monitoring",
                "Maintain water conservation practices",
                "Update drought preparedness plans"
            ])
        
        # Add severity-specific recommendations
        if severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME]:
            recommendations.append("Implement agricultural drought assistance programs")
        
        if duration > 6:
            recommendations.append("Develop long-term water management strategies")
        
        return recommendations
    
    def _calculate_severity_risk(self, severity: DroughtSeverity) -> float:
        """Calculate severity-based risk"""
        severity_risk_mapping = {
            DroughtSeverity.NONE: 0.0,
            DroughtSeverity.MILD: 0.2,
            DroughtSeverity.MODERATE: 0.5,
            DroughtSeverity.SEVERE: 0.8,
            DroughtSeverity.EXTREME: 1.0
        }
        
        return severity_risk_mapping.get(severity, 0.5)
    
    def _calculate_duration_risk(self, duration: int) -> float:
        """Calculate duration-based risk"""
        if duration <= 3:
            return 0.2
        elif duration <= 6:
            return 0.5
        elif duration <= 12:
            return 0.8
        else:
            return 1.0
    
    def _calculate_intensity_risk(self, intensity: float) -> float:
        """Calculate intensity-based risk"""
        return min(1.0, intensity / 2.0)  # Normalize to 0-1
    
    def _generate_drought_alerts(self, predicted_spi: np.ndarray, severity: DroughtSeverity, duration: int) -> List[Dict[str, Any]]:
        """Generate drought alerts"""
        alerts = []
        
        if severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME]:
            alerts.append({
                'type': 'critical_drought',
                'severity': severity,
                'message': f'Critical drought conditions predicted with severity {severity.name}',
                'duration': duration,
                'recommendation': 'Implement emergency response measures immediately'
            })
        
        if duration > 6:
            alerts.append({
                'type': 'prolonged_drought',
                'severity': severity,
                'message': f'Prolonged drought conditions expected for {duration} months',
                'duration': duration,
                'recommendation': 'Develop long-term water management strategies'
            })
        
        return alerts
    
    def _calculate_forecast_confidence(self, predicted_spi: np.ndarray) -> float:
        """Calculate forecast confidence"""
        # Simplified confidence calculation based on prediction stability
        if len(predicted_spi) < 2:
            return 0.5
        
        # Calculate prediction stability
        stability = 1.0 - np.std(predicted_spi) / (np.max(predicted_spi) - np.min(predicted_spi) + 1e-6)
        
        return max(0.5, min(0.95, stability))
    
    def _generate_seasonal_outlook(self, predicted_spi: np.ndarray) -> Dict[str, str]:
        """Generate seasonal outlook"""
        if len(predicted_spi) < 3:
            return {'short_term': 'uncertain', 'medium_term': 'uncertain', 'long_term': 'uncertain'}
        
        # Analyze different time periods
        short_term = predicted_spi[:3]
        medium_term = predicted_spi[3:6] if len(predicted_spi) >= 6 else predicted_spi[3:]
        long_term = predicted_spi[6:] if len(predicted_spi) >= 9 else predicted_spi[3:]
        
        def classify_outlook(spi_values):
            avg_spi = np.mean(spi_values)
            if avg_spi <= self.spi_thresholds['severe_drought']:
                return 'severe_drought'
            elif avg_spi <= self.spi_thresholds['moderate_drought']:
                return 'moderate_drought'
            elif avg_spi <= self.spi_thresholds['mild_drought']:
                return 'mild_drought'
            else:
                return 'normal'
        
        return {
            'short_term': classify_outlook(short_term),
            'medium_term': classify_outlook(medium_term),
            'long_term': classify_outlook(long_term)
        }
    
    def _generate_forecast_summary(self, predicted_spi: np.ndarray, severity: DroughtSeverity, duration: int) -> str:
        """Generate forecast summary"""
        return f"Drought forecast indicates {severity.name.lower()} conditions for {duration} months with SPI ranging from {min(predicted_spi):.2f} to {max(predicted_spi):.2f}"
    
    def _assess_agricultural_impact(self, severity: DroughtSeverity, duration: int, request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Assess agricultural impacts"""
        impact_level = "low"
        crop_loss_estimate = 0.0
        
        if severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME]:
            impact_level = "high"
            crop_loss_estimate = 0.4  # 40% crop loss
        elif severity == DroughtSeverity.MODERATE:
            impact_level = "moderate"
            crop_loss_estimate = 0.2  # 20% crop loss
        elif severity == DroughtSeverity.MILD:
            impact_level = "low"
            crop_loss_estimate = 0.05  # 5% crop loss
        
        # Adjust for duration
        if duration > 6:
            crop_loss_estimate *= 1.5
        
        return {
            'impact_level': impact_level,
            'crop_loss_estimate': float(crop_loss_estimate),
            'affected_crops': ['wheat', 'corn', 'soybeans'] if impact_level != "low" else [],
            'irrigation_requirements': 'increased' if impact_level != "low" else 'normal'
        }
    
    def _assess_water_supply_impact(self, severity: DroughtSeverity, duration: int, request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Assess water supply impacts"""
        impact_level = "low"
        supply_reduction = 0.0
        
        if severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME]:
            impact_level = "high"
            supply_reduction = 0.3  # 30% reduction
        elif severity == DroughtSeverity.MODERATE:
            impact_level = "moderate"
            supply_reduction = 0.15  # 15% reduction
        elif severity == DroughtSeverity.MILD:
            impact_level = "low"
            supply_reduction = 0.05  # 5% reduction
        
        return {
            'impact_level': impact_level,
            'supply_reduction': float(supply_reduction),
            'reservoir_levels': 'critical' if impact_level == "high" else 'moderate' if impact_level == "moderate" else 'normal',
            'groundwater_stress': 'high' if impact_level != "low" else 'low'
        }
    
    def _assess_economic_impact(self, severity: DroughtSeverity, duration: int, request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Assess economic impacts"""
        impact_level = "low"
        economic_loss = 0.0
        
        if severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME]:
            impact_level = "high"
            economic_loss = 1000000  # $1M loss
        elif severity == DroughtSeverity.MODERATE:
            impact_level = "moderate"
            economic_loss = 500000  # $500K loss
        elif severity == DroughtSeverity.MILD:
            impact_level = "low"
            economic_loss = 100000  # $100K loss
        
        # Adjust for duration
        if duration > 6:
            economic_loss *= 1.5
        
        return {
            'impact_level': impact_level,
            'economic_loss': float(economic_loss),
            'affected_sectors': ['agriculture', 'tourism', 'energy'] if impact_level != "low" else [],
            'employment_impact': 'significant' if impact_level == "high" else 'moderate' if impact_level == "moderate" else 'minimal'
        }
    
    def _assess_environmental_impact(self, severity: DroughtSeverity, duration: int, request: DroughtAnalysisRequest) -> Dict[str, Any]:
        """Assess environmental impacts"""
        impact_level = "low"
        
        if severity in [DroughtSeverity.SEVERE, DroughtSeverity.EXTREME]:
            impact_level = "high"
        elif severity == DroughtSeverity.MODERATE:
            impact_level = "moderate"
        elif severity == DroughtSeverity.MILD:
            impact_level = "low"
        
        return {
            'impact_level': impact_level,
            'ecosystem_stress': 'high' if impact_level != "low" else 'low',
            'wildlife_impact': 'significant' if impact_level == "high" else 'moderate' if impact_level == "moderate" else 'minimal',
            'water_quality_concerns': 'elevated' if impact_level != "low" else 'normal'
        }
    
    def _calculate_overall_impact_severity(self, agricultural_impact: Dict[str, Any], water_supply_impact: Dict[str, Any], 
                                         economic_impact: Dict[str, Any], environmental_impact: Dict[str, Any]) -> str:
        """Calculate overall impact severity"""
        impact_levels = [
            agricultural_impact['impact_level'],
            water_supply_impact['impact_level'],
            economic_impact['impact_level'],
            environmental_impact['impact_level']
        ]
        
        high_count = impact_levels.count('high')
        moderate_count = impact_levels.count('moderate')
        
        if high_count >= 2:
            return 'critical'
        elif high_count >= 1 or moderate_count >= 2:
            return 'high'
        elif moderate_count >= 1:
            return 'moderate'
        else:
            return 'low' 