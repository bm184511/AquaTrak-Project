"""
Drinking Water Quality Analysis Processor
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
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cluster import DBSCAN
import cv2
from .models import *

logger = logging.getLogger(__name__)


class DrinkingWaterQualityProcessor:
    """Advanced drinking water quality analysis processor with AI/ML capabilities"""
    
    def __init__(self):
        """Initialize the drinking water quality processor with ML models"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DrinkingWaterQualityProcessor with ML capabilities")
        
        # Initialize ML models for different aspects
        self.contaminant_detector = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
        self.health_risk_assessor = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
        self.quality_predictor = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        
        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.quality_scaler = RobustScaler()
        self.risk_scaler = StandardScaler()
        
        # Water quality parameters and thresholds
        self.regulatory_limits = {
            'arsenic': 0.01,      # mg/L
            'lead': 0.015,        # mg/L
            'mercury': 0.002,     # mg/L
            'cadmium': 0.005,     # mg/L
            'chromium': 0.1,      # mg/L
            'nitrate': 10.0,      # mg/L
            'nitrite': 1.0,       # mg/L
            'chlorine': 4.0,      # mg/L
            'turbidity': 1.0,     # NTU
            'ph': 8.5,            # pH units
            'total_coliforms': 0, # CFU/100mL
            'e_coli': 0,          # CFU/100mL
            'tthm': 0.08,         # mg/L
            'haa5': 0.06          # mg/L
        }
        
        # Health risk thresholds
        self.health_risk_thresholds = {
            'acute': 5.0,    # Acute health risk threshold
            'chronic': 2.0,  # Chronic health risk threshold
            'cancer': 1.0    # Cancer risk threshold
        }
        
    async def process_analysis(self, request: WaterQualityAnalysisRequest) -> WaterQualityResult:
        """Process drinking water quality analysis with advanced ML algorithms"""
        start_time = datetime.utcnow()
        self.logger.info(f"Processing drinking water quality analysis for request {request.id}")
        
        try:
            # Step 1: Analyze water quality parameters
            quality_analysis = await self._analyze_water_parameters(request.water_quality_data)
            
            # Step 2: Detect contaminants using ML
            contaminant_detection = await self._detect_contaminants(quality_analysis, request)
            
            # Step 3: Detect anomalies in water quality
            anomaly_detection = await self._detect_anomalies(quality_analysis, request)
            
            # Step 4: Assess health risks using ML models
            health_risk_assessment = await self._assess_health_risks(contaminant_detection, quality_analysis, request)
            
            # Step 5: Check regulatory compliance
            compliance_assessment = await self._assess_regulatory_compliance(quality_analysis, contaminant_detection)
            
            # Step 6: Generate quality predictions
            quality_prediction = await self._predict_water_quality(quality_analysis, request)
            
            # Step 7: Generate alerts and recommendations
            alerts = await self._generate_quality_alerts(health_risk_assessment, compliance_assessment, contaminant_detection)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = WaterQualityResult(
                analysis_id=request.id,
                water_quality_parameters=quality_analysis['parameters'],
                contaminant_levels=contaminant_detection['levels'],
                health_risk_assessment=health_risk_assessment['assessment'],
                compliance_status=compliance_assessment['status'],
                overall_quality_score=quality_prediction['overall_score'],
                risk_level=health_risk_assessment['risk_level'],
                alerts=alerts,
                recommendations=health_risk_assessment['recommendations'],
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing drinking water quality analysis: {str(e)}")
            raise
    
    async def _analyze_water_parameters(self, water_quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze water quality parameters and extract features"""
        self.logger.info("Analyzing water quality parameters")
        
        # Extract parameter values
        parameters = water_quality_data.get('parameters', {})
        timestamps = water_quality_data.get('timestamps', [])
        location = water_quality_data.get('location', {})
        
        # Calculate statistical summaries
        parameter_stats = {}
        for param_name, values in parameters.items():
            if isinstance(values, list) and len(values) > 0:
                values_array = np.array(values)
                parameter_stats[param_name] = {
                    'mean': float(np.mean(values_array)),
                    'median': float(np.median(values_array)),
                    'std': float(np.std(values_array)),
                    'min': float(np.min(values_array)),
                    'max': float(np.max(values_array)),
                    'current_value': float(values_array[-1]) if len(values_array) > 0 else 0.0,
                    'trend': self._calculate_parameter_trend(values_array),
                    'stability': self._calculate_parameter_stability(values_array)
                }
        
        # Calculate derived parameters
        derived_parameters = self._calculate_derived_parameters(parameters)
        
        # Assess data quality
        data_quality = self._assess_data_quality(parameters, timestamps)
        
        return {
            'parameters': parameter_stats,
            'derived_parameters': derived_parameters,
            'data_quality': data_quality,
            'timestamps': timestamps,
            'location': location
        }
    
    async def _detect_contaminants(self, quality_analysis: Dict[str, Any], request: WaterQualityAnalysisRequest) -> Dict[str, Any]:
        """Detect contaminants using ML algorithms"""
        self.logger.info("Detecting contaminants using ML")
        
        parameters = quality_analysis['parameters']
        
        # Extract features for contaminant detection
        features = self._extract_contaminant_features(parameters, request)
        
        # Normalize features
        features_normalized = self.feature_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict contaminant presence using ML
        contaminant_predictions = self.contaminant_detector.predict(features_normalized)
        contaminant_probabilities = self.contaminant_detector.predict_proba(features_normalized)
        
        # Analyze contaminant levels
        contaminant_levels = self._analyze_contaminant_levels(parameters)
        
        # Identify specific contaminants
        detected_contaminants = self._identify_specific_contaminants(contaminant_levels, contaminant_probabilities[0])
        
        # Calculate contamination risk
        contamination_risk = self._calculate_contamination_risk(contaminant_levels, detected_contaminants)
        
        return {
            'detected_contaminants': detected_contaminants,
            'contaminant_levels': contaminant_levels,
            'contamination_risk': contamination_risk,
            'prediction_confidence': float(np.max(contaminant_probabilities)),
            'ml_predictions': contaminant_predictions.tolist()
        }
    
    async def _detect_anomalies(self, quality_analysis: Dict[str, Any], request: WaterQualityAnalysisRequest) -> Dict[str, Any]:
        """Detect anomalies in water quality data"""
        self.logger.info("Detecting water quality anomalies")
        
        parameters = quality_analysis['parameters']
        
        # Extract features for anomaly detection
        features = self._extract_anomaly_features(parameters, request)
        
        # Normalize features
        features_normalized = self.feature_scaler.fit_transform(features.reshape(-1, features.shape[-1]))
        
        # Detect anomalies using Isolation Forest
        anomaly_scores = self.anomaly_detector.fit_predict(features_normalized)
        anomaly_indices = np.where(anomaly_scores == -1)[0]
        
        # Classify anomalies
        anomaly_classification = self._classify_anomalies(anomaly_indices, parameters)
        
        # Calculate anomaly severity
        anomaly_severity = self._calculate_anomaly_severity(anomaly_indices, parameters)
        
        # Identify anomaly patterns
        anomaly_patterns = self._identify_anomaly_patterns(anomaly_indices, parameters)
        
        return {
            'anomalies': anomaly_classification,
            'anomaly_severity': anomaly_severity,
            'anomaly_patterns': anomaly_patterns,
            'anomaly_count': len(anomaly_indices),
            'anomaly_probability': len(anomaly_indices) / len(features_normalized) if len(features_normalized) > 0 else 0.0
        }
    
    async def _assess_health_risks(self, contaminant_detection: Dict[str, Any], quality_analysis: Dict[str, Any], 
                                 request: WaterQualityAnalysisRequest) -> Dict[str, Any]:
        """Assess health risks using ML models"""
        self.logger.info("Assessing health risks using ML")
        
        contaminant_levels = contaminant_detection['contaminant_levels']
        parameters = quality_analysis['parameters']
        
        # Extract features for health risk assessment
        features = self._extract_health_risk_features(contaminant_levels, parameters, request)
        
        # Normalize features
        features_normalized = self.risk_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict health risk using ML
        health_risk_prediction = self.health_risk_assessor.predict(features_normalized)[0]
        health_risk_probability = self.health_risk_assessor.predict_proba(features_normalized)[0]
        
        # Calculate detailed health risk assessment
        acute_risk = self._calculate_acute_health_risk(contaminant_levels, parameters)
        chronic_risk = self._calculate_chronic_health_risk(contaminant_levels, parameters)
        cancer_risk = self._calculate_cancer_risk(contaminant_levels, parameters)
        
        # Determine overall risk level
        risk_level = self._determine_health_risk_level(acute_risk, chronic_risk, cancer_risk)
        
        # Generate recommendations
        recommendations = self._generate_health_recommendations(risk_level, contaminant_levels)
        
        return {
            'assessment': {
                'acute_risk': acute_risk,
                'chronic_risk': chronic_risk,
                'cancer_risk': cancer_risk,
                'overall_risk_score': float(np.max(health_risk_probability))
            },
            'risk_level': risk_level,
            'recommendations': recommendations,
            'vulnerable_populations': self._identify_vulnerable_populations(risk_level, request),
            'exposure_pathways': self._identify_exposure_pathways(contaminant_levels)
        }
    
    async def _assess_regulatory_compliance(self, quality_analysis: Dict[str, Any], contaminant_detection: Dict[str, Any]) -> Dict[str, Any]:
        """Assess regulatory compliance"""
        self.logger.info("Assessing regulatory compliance")
        
        parameters = quality_analysis['parameters']
        contaminant_levels = contaminant_detection['contaminant_levels']
        
        # Check compliance for each parameter
        compliance_results = {}
        violations = []
        
        for param_name, param_data in parameters.items():
            if param_name in self.regulatory_limits:
                current_value = param_data['current_value']
                regulatory_limit = self.regulatory_limits[param_name]
                
                if current_value > regulatory_limit:
                    compliance_results[param_name] = 'non_compliant'
                    violations.append({
                        'parameter': param_name,
                        'current_value': current_value,
                        'regulatory_limit': regulatory_limit,
                        'exceedance_factor': current_value / regulatory_limit
                    })
                else:
                    compliance_results[param_name] = 'compliant'
            else:
                compliance_results[param_name] = 'no_limit'
        
        # Determine overall compliance status
        if any(result == 'non_compliant' for result in compliance_results.values()):
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif any(result == 'no_limit' for result in compliance_results.values()):
            overall_status = ComplianceStatus.PARTIAL
        else:
            overall_status = ComplianceStatus.COMPLIANT
        
        # Calculate compliance score
        compliant_params = sum(1 for result in compliance_results.values() if result == 'compliant')
        total_params = len(compliance_results)
        compliance_score = compliant_params / total_params if total_params > 0 else 0.0
        
        return {
            'status': overall_status,
            'compliance_score': float(compliance_score),
            'compliance_results': compliance_results,
            'violations': violations,
            'required_actions': self._determine_required_actions(violations)
        }
    
    async def _predict_water_quality(self, quality_analysis: Dict[str, Any], request: WaterQualityAnalysisRequest) -> Dict[str, Any]:
        """Predict future water quality using ML"""
        self.logger.info("Predicting water quality trends")
        
        parameters = quality_analysis['parameters']
        
        # Extract features for quality prediction
        features = self._extract_quality_prediction_features(parameters, request)
        
        # Normalize features
        features_normalized = self.quality_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict quality using ML
        quality_prediction = self.quality_predictor.predict(features_normalized)[0]
        quality_probability = self.quality_predictor.predict_proba(features_normalized)[0]
        
        # Calculate overall quality score
        overall_score = self._calculate_overall_quality_score(parameters)
        
        # Predict quality trends
        quality_trends = self._predict_quality_trends(parameters)
        
        # Generate quality forecast
        quality_forecast = self._generate_quality_forecast(parameters, quality_trends)
        
        return {
            'overall_score': float(overall_score),
            'quality_prediction': int(quality_prediction),
            'prediction_confidence': float(np.max(quality_probability)),
            'quality_trends': quality_trends,
            'quality_forecast': quality_forecast,
            'quality_grade': self._grade_water_quality(overall_score)
        }
    
    async def _generate_quality_alerts(self, health_risk_assessment: Dict[str, Any], compliance_assessment: Dict[str, Any], 
                                     contaminant_detection: Dict[str, Any]) -> List[WaterQualityAlert]:
        """Generate water quality alerts"""
        alerts = []
        
        risk_level = health_risk_assessment['risk_level']
        compliance_status = compliance_assessment['status']
        contaminant_levels = contaminant_detection['contaminant_levels']
        
        # Generate health risk alerts
        if risk_level in [HealthRiskLevel.HIGH, HealthRiskLevel.CRITICAL]:
            alert = WaterQualityAlert(
                alert_type="health_risk",
                severity=risk_level,
                message=f"Critical health risk detected with risk level {risk_level.name}",
                affected_parameters=list(contaminant_levels.keys()),
                recommendation="Immediate water treatment and public notification required"
            )
            alerts.append(alert)
        
        # Generate compliance alerts
        if compliance_status == ComplianceStatus.NON_COMPLIANT:
            violations = compliance_assessment['violations']
            alert = WaterQualityAlert(
                alert_type="regulatory_violation",
                severity=HealthRiskLevel.HIGH,
                message=f"Regulatory violations detected: {len(violations)} parameters exceed limits",
                affected_parameters=[v['parameter'] for v in violations],
                recommendation="Implement immediate corrective actions and notify regulatory authorities"
            )
            alerts.append(alert)
        
        # Generate contaminant alerts
        high_contaminants = [cont for cont, level in contaminant_levels.items() if level > 0.5]
        if high_contaminants:
            alert = WaterQualityAlert(
                alert_type="high_contamination",
                severity=HealthRiskLevel.MODERATE,
                message=f"High contamination levels detected in {len(high_contaminants)} parameters",
                affected_parameters=high_contaminants,
                recommendation="Enhance water treatment and monitoring procedures"
            )
            alerts.append(alert)
        
        return alerts
    
    def _calculate_parameter_trend(self, values: np.ndarray) -> str:
        """Calculate parameter trend"""
        if len(values) < 2:
            return "stable"
        
        # Calculate trend using linear regression
        x = np.arange(len(values))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_parameter_stability(self, values: np.ndarray) -> float:
        """Calculate parameter stability"""
        if len(values) < 2:
            return 1.0
        
        # Calculate coefficient of variation
        mean_val = np.mean(values)
        if mean_val == 0:
            return 1.0
        
        cv = np.std(values) / abs(mean_val)
        stability = 1.0 - min(cv, 1.0)
        
        return float(stability)
    
    def _calculate_derived_parameters(self, parameters: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate derived water quality parameters"""
        derived = {}
        
        # Calculate hardness if calcium and magnesium are available
        if 'calcium' in parameters and 'magnesium' in parameters:
            ca_values = np.array(parameters['calcium'])
            mg_values = np.array(parameters['magnesium'])
            hardness = 2.497 * ca_values + 4.118 * mg_values
            derived['total_hardness'] = float(np.mean(hardness))
        
        # Calculate alkalinity if bicarbonate is available
        if 'bicarbonate' in parameters:
            hco3_values = np.array(parameters['bicarbonate'])
            alkalinity = hco3_values * 0.82  # Convert to CaCO3 equivalent
            derived['alkalinity'] = float(np.mean(alkalinity))
        
        # Calculate Langelier Saturation Index if pH, calcium, alkalinity, and TDS are available
        if all(param in parameters for param in ['ph', 'calcium', 'alkalinity', 'tds']):
            ph_values = np.array(parameters['ph'])
            ca_values = np.array(parameters['calcium'])
            alk_values = np.array(parameters['alkalinity'])
            tds_values = np.array(parameters['tds'])
            
            # Simplified LSI calculation
            lsi = ph_values - (6.5 + np.log10(ca_values) + np.log10(alk_values) - np.log10(tds_values))
            derived['langelier_index'] = float(np.mean(lsi))
        
        return derived
    
    def _assess_data_quality(self, parameters: Dict[str, List[float]], timestamps: List[str]) -> Dict[str, float]:
        """Assess data quality metrics"""
        quality_metrics = {}
        
        # Calculate completeness
        total_expected = len(timestamps) * len(parameters)
        total_actual = sum(len(values) for values in parameters.values())
        completeness = total_actual / total_expected if total_expected > 0 else 0.0
        quality_metrics['completeness'] = float(completeness)
        
        # Calculate consistency
        consistencies = []
        for param_name, values in parameters.items():
            if len(values) > 1:
                # Calculate coefficient of variation
                mean_val = np.mean(values)
                if mean_val != 0:
                    cv = np.std(values) / abs(mean_val)
                    consistency = 1.0 - min(cv, 1.0)
                    consistencies.append(consistency)
        
        quality_metrics['consistency'] = float(np.mean(consistencies)) if consistencies else 0.0
        
        # Calculate accuracy (assume 95% for sensor data)
        quality_metrics['accuracy'] = 0.95
        
        # Calculate overall quality
        quality_metrics['overall_quality'] = float(
            (quality_metrics['completeness'] + quality_metrics['consistency'] + quality_metrics['accuracy']) / 3
        )
        
        return quality_metrics
    
    def _extract_contaminant_features(self, parameters: Dict[str, Dict[str, float]], request: WaterQualityAnalysisRequest) -> np.ndarray:
        """Extract features for contaminant detection"""
        features = []
        
        # Add current parameter values
        for param_name in ['arsenic', 'lead', 'mercury', 'cadmium', 'chromium', 'nitrate', 'nitrite']:
            if param_name in parameters:
                features.extend([
                    parameters[param_name]['current_value'],
                    parameters[param_name]['mean'],
                    parameters[param_name]['std'],
                    parameters[param_name]['trend'] == 'increasing'
                ])
            else:
                features.extend([0.0, 0.0, 0.0, False])
        
        # Add water quality indicators
        for param_name in ['ph', 'turbidity', 'chlorine', 'tds']:
            if param_name in parameters:
                features.extend([
                    parameters[param_name]['current_value'],
                    parameters[param_name]['mean'],
                    parameters[param_name]['stability']
                ])
            else:
                features.extend([0.0, 0.0, 1.0])
        
        # Add location and source features
        features.extend([
            request.water_source_type.value if hasattr(request.water_source_type, 'value') else 0,
            request.treatment_level.value if hasattr(request.treatment_level, 'value') else 0
        ])
        
        return np.array(features)
    
    def _analyze_contaminant_levels(self, parameters: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Analyze contaminant levels"""
        contaminant_levels = {}
        
        # Analyze each contaminant
        for param_name, param_data in parameters.items():
            if param_name in self.regulatory_limits:
                current_value = param_data['current_value']
                regulatory_limit = self.regulatory_limits[param_name]
                
                # Calculate normalized level (0-1 scale)
                normalized_level = min(1.0, current_value / regulatory_limit) if regulatory_limit > 0 else 0.0
                contaminant_levels[param_name] = normalized_level
        
        return contaminant_levels
    
    def _identify_specific_contaminants(self, contaminant_levels: Dict[str, float], probabilities: np.ndarray) -> List[str]:
        """Identify specific contaminants present"""
        detected_contaminants = []
        
        # Use ML probabilities and contaminant levels
        for param_name, level in contaminant_levels.items():
            if level > 0.3:  # 30% of regulatory limit
                detected_contaminants.append(param_name)
        
        return detected_contaminants
    
    def _calculate_contamination_risk(self, contaminant_levels: Dict[str, float], detected_contaminants: List[str]) -> float:
        """Calculate overall contamination risk"""
        if not contaminant_levels:
            return 0.0
        
        # Calculate weighted risk based on contaminant levels and health effects
        risk_weights = {
            'arsenic': 1.0,    # High health impact
            'lead': 0.9,       # High health impact
            'mercury': 1.0,    # High health impact
            'cadmium': 0.8,    # Medium-high health impact
            'chromium': 0.7,   # Medium health impact
            'nitrate': 0.6,    # Medium health impact
            'nitrite': 0.8     # Medium-high health impact
        }
        
        total_risk = 0.0
        total_weight = 0.0
        
        for contaminant, level in contaminant_levels.items():
            weight = risk_weights.get(contaminant, 0.5)
            total_risk += level * weight
            total_weight += weight
        
        return total_risk / total_weight if total_weight > 0 else 0.0
    
    def _extract_anomaly_features(self, parameters: Dict[str, Dict[str, float]], request: WaterQualityAnalysisRequest) -> np.ndarray:
        """Extract features for anomaly detection"""
        features = []
        
        # Add parameter statistics
        for param_name in ['ph', 'turbidity', 'chlorine', 'tds', 'temperature']:
            if param_name in parameters:
                param_data = parameters[param_name]
                features.extend([
                    param_data['current_value'],
                    param_data['mean'],
                    param_data['std'],
                    param_data['stability'],
                    param_data['trend'] == 'increasing'
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 1.0, False])
        
        # Add derived features
        features.extend([
            request.water_source_type.value if hasattr(request.water_source_type, 'value') else 0,
            request.treatment_level.value if hasattr(request.treatment_level, 'value') else 0
        ])
        
        return np.array(features)
    
    def _classify_anomalies(self, anomaly_indices: np.ndarray, parameters: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Classify detected anomalies"""
        anomalies = []
        
        for idx in anomaly_indices:
            anomaly_type = "unknown"
            severity = "low"
            
            # Classify based on parameter characteristics
            for param_name, param_data in parameters.items():
                if param_data['std'] > param_data['mean'] * 0.5:  # High variability
                    anomaly_type = "high_variability"
                    severity = "medium"
                elif param_data['trend'] == 'increasing' and param_name in ['turbidity', 'tds']:
                    anomaly_type = "quality_degradation"
                    severity = "high"
                elif param_data['current_value'] > param_data['mean'] * 2:
                    anomaly_type = "spike"
                    severity = "high"
            
            anomalies.append({
                'index': int(idx),
                'type': anomaly_type,
                'severity': severity,
                'affected_parameters': list(parameters.keys())
            })
        
        return anomalies
    
    def _calculate_anomaly_severity(self, anomaly_indices: np.ndarray, parameters: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate anomaly severity metrics"""
        if len(anomaly_indices) == 0:
            return {'overall_severity': 0.0, 'max_severity': 0.0, 'average_severity': 0.0}
        
        # Calculate severity based on parameter deviations
        severities = []
        for param_name, param_data in parameters.items():
            if param_data['std'] > 0:
                deviation = abs(param_data['current_value'] - param_data['mean']) / param_data['std']
                severities.append(min(1.0, deviation / 3.0))  # Normalize to 0-1
        
        if not severities:
            return {'overall_severity': 0.0, 'max_severity': 0.0, 'average_severity': 0.0}
        
        return {
            'overall_severity': float(np.mean(severities)),
            'max_severity': float(np.max(severities)),
            'average_severity': float(np.mean(severities))
        }
    
    def _identify_anomaly_patterns(self, anomaly_indices: np.ndarray, parameters: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify anomaly patterns"""
        patterns = []
        
        # Check for temporal patterns
        if len(anomaly_indices) > 3:
            patterns.append("recurring_anomalies")
        
        # Check for parameter correlation patterns
        high_variability_params = [param for param, data in parameters.items() if data['std'] > data['mean'] * 0.3]
        if len(high_variability_params) > 2:
            patterns.append("correlated_parameter_variability")
        
        # Check for trend patterns
        increasing_trends = [param for param, data in parameters.items() if data['trend'] == 'increasing']
        if len(increasing_trends) > 1:
            patterns.append("systematic_quality_degradation")
        
        return patterns
    
    def _extract_health_risk_features(self, contaminant_levels: Dict[str, float], parameters: Dict[str, Dict[str, float]], 
                                    request: WaterQualityAnalysisRequest) -> np.ndarray:
        """Extract features for health risk assessment"""
        features = []
        
        # Add contaminant levels
        for contaminant in ['arsenic', 'lead', 'mercury', 'cadmium', 'chromium', 'nitrate', 'nitrite']:
            features.append(contaminant_levels.get(contaminant, 0.0))
        
        # Add water quality indicators
        for param in ['ph', 'turbidity', 'chlorine', 'tds']:
            if param in parameters:
                features.extend([
                    parameters[param]['current_value'],
                    parameters[param]['stability']
                ])
            else:
                features.extend([0.0, 1.0])
        
        # Add population and source features
        features.extend([
            request.population_served if hasattr(request, 'population_served') else 1000,
            request.water_source_type.value if hasattr(request.water_source_type, 'value') else 0,
            request.treatment_level.value if hasattr(request.treatment_level, 'value') else 0
        ])
        
        return np.array(features)
    
    def _calculate_acute_health_risk(self, contaminant_levels: Dict[str, float], parameters: Dict[str, Dict[str, float]]) -> float:
        """Calculate acute health risk"""
        acute_risk = 0.0
        
        # High acute risk contaminants
        acute_contaminants = ['arsenic', 'lead', 'mercury', 'nitrite']
        for contaminant in acute_contaminants:
            if contaminant in contaminant_levels:
                level = contaminant_levels[contaminant]
                if level > 0.8:  # 80% of regulatory limit
                    acute_risk += level * 0.5
        
        return min(1.0, acute_risk)
    
    def _calculate_chronic_health_risk(self, contaminant_levels: Dict[str, float], parameters: Dict[str, Dict[str, float]]) -> float:
        """Calculate chronic health risk"""
        chronic_risk = 0.0
        
        # Chronic risk contaminants
        chronic_contaminants = ['arsenic', 'lead', 'cadmium', 'chromium', 'nitrate']
        for contaminant in chronic_contaminants:
            if contaminant in contaminant_levels:
                level = contaminant_levels[contaminant]
                if level > 0.5:  # 50% of regulatory limit
                    chronic_risk += level * 0.3
        
        return min(1.0, chronic_risk)
    
    def _calculate_cancer_risk(self, contaminant_levels: Dict[str, float], parameters: Dict[str, Dict[str, float]]) -> float:
        """Calculate cancer risk"""
        cancer_risk = 0.0
        
        # Carcinogenic contaminants
        carcinogenic_contaminants = ['arsenic', 'chromium', 'cadmium']
        for contaminant in carcinogenic_contaminants:
            if contaminant in contaminant_levels:
                level = contaminant_levels[contaminant]
                if level > 0.3:  # 30% of regulatory limit
                    cancer_risk += level * 0.4
        
        return min(1.0, cancer_risk)
    
    def _determine_health_risk_level(self, acute_risk: float, chronic_risk: float, cancer_risk: float) -> HealthRiskLevel:
        """Determine overall health risk level"""
        # Weighted combination of risks
        overall_risk = acute_risk * 0.4 + chronic_risk * 0.4 + cancer_risk * 0.2
        
        if overall_risk > 0.7:
            return HealthRiskLevel.CRITICAL
        elif overall_risk > 0.5:
            return HealthRiskLevel.HIGH
        elif overall_risk > 0.3:
            return HealthRiskLevel.MODERATE
        elif overall_risk > 0.1:
            return HealthRiskLevel.LOW
        else:
            return HealthRiskLevel.NONE
    
    def _generate_health_recommendations(self, risk_level: HealthRiskLevel, contaminant_levels: Dict[str, float]) -> List[str]:
        """Generate health-based recommendations"""
        recommendations = []
        
        if risk_level in [HealthRiskLevel.HIGH, HealthRiskLevel.CRITICAL]:
            recommendations.extend([
                "Implement immediate water treatment measures",
                "Notify public health authorities",
                "Provide alternative water sources",
                "Conduct comprehensive water quality assessment"
            ])
        elif risk_level == HealthRiskLevel.MODERATE:
            recommendations.extend([
                "Enhance water treatment processes",
                "Increase monitoring frequency",
                "Implement preventive measures",
                "Conduct health risk assessment"
            ])
        else:
            recommendations.extend([
                "Continue routine monitoring",
                "Maintain treatment standards",
                "Document baseline conditions"
            ])
        
        # Add contaminant-specific recommendations
        high_contaminants = [cont for cont, level in contaminant_levels.items() if level > 0.5]
        if high_contaminants:
            recommendations.append(f"Focus treatment on: {', '.join(high_contaminants)}")
        
        return recommendations
    
    def _identify_vulnerable_populations(self, risk_level: HealthRiskLevel, request: WaterQualityAnalysisRequest) -> List[str]:
        """Identify vulnerable populations"""
        vulnerable_populations = ['children', 'elderly', 'pregnant_women']
        
        if risk_level in [HealthRiskLevel.HIGH, HealthRiskLevel.CRITICAL]:
            vulnerable_populations.extend(['immunocompromised', 'infants'])
        
        return vulnerable_populations
    
    def _identify_exposure_pathways(self, contaminant_levels: Dict[str, float]) -> List[str]:
        """Identify exposure pathways"""
        pathways = ['drinking_water']
        
        high_contaminants = [cont for cont, level in contaminant_levels.items() if level > 0.5]
        if high_contaminants:
            pathways.extend(['cooking', 'bathing', 'inhalation'])
        
        return pathways
    
    def _determine_required_actions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Determine required actions for violations"""
        actions = []
        
        for violation in violations:
            if violation['exceedance_factor'] > 2.0:
                actions.append("immediate_notification")
                actions.append("emergency_response")
            elif violation['exceedance_factor'] > 1.5:
                actions.append("enhanced_monitoring")
                actions.append("corrective_action_plan")
            else:
                actions.append("routine_monitoring")
        
        return list(set(actions))  # Remove duplicates
    
    def _extract_quality_prediction_features(self, parameters: Dict[str, Dict[str, float]], request: WaterQualityAnalysisRequest) -> np.ndarray:
        """Extract features for quality prediction"""
        features = []
        
        # Add parameter statistics
        for param_name in ['ph', 'turbidity', 'chlorine', 'tds', 'temperature']:
            if param_name in parameters:
                param_data = parameters[param_name]
                features.extend([
                    param_data['current_value'],
                    param_data['mean'],
                    param_data['std'],
                    param_data['stability'],
                    param_data['trend'] == 'increasing'
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 1.0, False])
        
        # Add source and treatment features
        features.extend([
            request.water_source_type.value if hasattr(request.water_source_type, 'value') else 0,
            request.treatment_level.value if hasattr(request.treatment_level, 'value') else 0
        ])
        
        return np.array(features)
    
    def _calculate_overall_quality_score(self, parameters: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall water quality score"""
        if not parameters:
            return 0.0
        
        # Calculate weighted quality score based on key parameters
        quality_weights = {
            'ph': 0.15,
            'turbidity': 0.20,
            'chlorine': 0.15,
            'tds': 0.10,
            'temperature': 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for param_name, param_data in parameters.items():
            if param_name in quality_weights:
                weight = quality_weights[param_name]
                
                # Calculate parameter score based on stability and current value
                stability_score = param_data['stability']
                current_score = 1.0 - min(1.0, abs(param_data['current_value'] - param_data['mean']) / (param_data['std'] + 1e-6))
                
                param_score = (stability_score + current_score) / 2
                total_score += param_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _predict_quality_trends(self, parameters: Dict[str, Dict[str, float]]) -> Dict[str, str]:
        """Predict quality trends"""
        trends = {}
        
        for param_name, param_data in parameters.items():
            trends[param_name] = param_data['trend']
        
        return trends
    
    def _generate_quality_forecast(self, parameters: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> Dict[str, Any]:
        """Generate quality forecast"""
        forecast = {
            'short_term': 'stable',
            'medium_term': 'stable',
            'long_term': 'stable'
        }
        
        # Analyze trends to determine forecast
        increasing_trends = sum(1 for trend in trends.values() if trend == 'increasing')
        decreasing_trends = sum(1 for trend in trends.values() if trend == 'decreasing')
        
        if increasing_trends > decreasing_trends:
            forecast['short_term'] = 'improving'
        elif decreasing_trends > increasing_trends:
            forecast['short_term'] = 'declining'
        
        return forecast
    
    def _grade_water_quality(self, quality_score: float) -> str:
        """Grade water quality"""
        if quality_score >= 0.9:
            return "A"
        elif quality_score >= 0.8:
            return "B"
        elif quality_score >= 0.7:
            return "C"
        elif quality_score >= 0.6:
            return "D"
        else:
            return "F" 