"""
Data Center Water Consumption Processor
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
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score
from .models import *

logger = logging.getLogger(__name__)


class DataCenterWaterProcessor:
    """Advanced data center water consumption processor with AI/ML capabilities"""
    
    def __init__(self):
        """Initialize the data center water processor with ML models"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DataCenterWaterProcessor with ML capabilities")
        
        # Initialize ML models for different aspects
        self.consumption_predictor = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
        self.efficiency_analyzer = GradientBoostingRegressor(n_estimators=150, max_depth=10, random_state=42)
        self.sustainability_assessor = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
        self.optimization_model = RandomForestRegressor(n_estimators=120, max_depth=10, random_state=42)
        
        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.consumption_scaler = MinMaxScaler()
        self.efficiency_scaler = StandardScaler()
        
        # Data center parameters
        self.pue_threshold = 1.5  # Power Usage Effectiveness threshold
        self.wue_threshold = 0.5  # Water Usage Effectiveness threshold (L/kWh)
        self.carbon_intensity = 0.5  # kg CO2/kWh (grid average)
        
    async def process_analysis(self, request: DataCenterAnalysisRequest) -> DataCenterResult:
        """Process data center water analysis with advanced ML algorithms"""
        start_time = datetime.utcnow()
        self.logger.info(f"Processing data center water analysis for request {request.id}")
        
        try:
            # Step 1: Analyze water consumption patterns
            consumption_analysis = await self._analyze_water_consumption(request.water_consumption_data, request)
            
            # Step 2: Calculate efficiency metrics using ML
            efficiency_analysis = await self._calculate_efficiency_metrics(consumption_analysis, request)
            
            # Step 3: Assess sustainability using ML models
            sustainability_assessment = await self._assess_sustainability(efficiency_analysis, request)
            
            # Step 4: Identify optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(consumption_analysis, efficiency_analysis, request)
            
            # Step 5: Calculate cost analysis
            cost_analysis = await self._calculate_cost_analysis(consumption_analysis, efficiency_analysis, request)
            
            # Step 6: Assess environmental impact
            environmental_impact = await self._assess_environmental_impact(consumption_analysis, efficiency_analysis, request)
            
            # Step 7: Generate facility summary
            facility_summary = await self._generate_facility_summary(request, consumption_analysis, efficiency_analysis)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = DataCenterResult(
                analysis_id=request.id,
                facility_summary=facility_summary,
                water_consumption_analysis=consumption_analysis,
                efficiency_analysis=efficiency_analysis,
                sustainability_assessment=sustainability_assessment,
                optimization_opportunities=optimization_opportunities,
                cost_analysis=cost_analysis,
                environmental_impact=environmental_impact,
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing data center water analysis: {str(e)}")
            raise
    
    async def _analyze_water_consumption(self, consumption_data: Dict[str, Any], request: DataCenterAnalysisRequest) -> Dict[str, Any]:
        """Analyze water consumption patterns"""
        self.logger.info("Analyzing water consumption patterns")
        
        # Extract consumption data
        water_usage = consumption_data.get('water_usage', [])
        energy_consumption = consumption_data.get('energy_consumption', [])
        it_load = consumption_data.get('it_load', [])
        timestamps = consumption_data.get('timestamps', [])
        
        # Convert to numpy arrays
        water_usage = np.array(water_usage)
        energy_consumption = np.array(energy_consumption)
        it_load = np.array(it_load)
        
        # Calculate consumption statistics
        consumption_stats = self._calculate_consumption_statistics(water_usage, energy_consumption, it_load)
        
        # Analyze consumption patterns
        consumption_patterns = self._analyze_consumption_patterns(water_usage, energy_consumption, it_load, timestamps)
        
        # Calculate water efficiency metrics
        water_efficiency_metrics = self._calculate_water_efficiency_metrics(water_usage, energy_consumption, it_load)
        
        # Detect consumption anomalies
        consumption_anomalies = self._detect_consumption_anomalies(water_usage, energy_consumption, it_load)
        
        return {
            'consumption_stats': consumption_stats,
            'consumption_patterns': consumption_patterns,
            'water_efficiency_metrics': water_efficiency_metrics,
            'consumption_anomalies': consumption_anomalies,
            'data_quality': self._assess_data_quality(water_usage, energy_consumption, it_load)
        }
    
    async def _calculate_efficiency_metrics(self, consumption_analysis: Dict[str, Any], request: DataCenterAnalysisRequest) -> Dict[str, Any]:
        """Calculate efficiency metrics using ML"""
        self.logger.info("Calculating efficiency metrics")
        
        consumption_stats = consumption_analysis['consumption_stats']
        water_efficiency_metrics = consumption_analysis['water_efficiency_metrics']
        
        # Extract efficiency features
        features = self._extract_efficiency_features(consumption_stats, water_efficiency_metrics, request)
        
        # Normalize features
        features_normalized = self.efficiency_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict efficiency metrics using ML
        efficiency_prediction = self.efficiency_analyzer.predict(features_normalized)[0]
        
        # Calculate detailed efficiency metrics
        pue = self._calculate_pue(consumption_stats['total_energy'], consumption_stats['it_energy'])
        wue = self._calculate_wue(consumption_stats['total_water'], consumption_stats['it_energy'])
        cue = self._calculate_cue(consumption_stats['total_energy'], request.facility_size)
        
        # Calculate efficiency trends
        efficiency_trends = self._calculate_efficiency_trends(consumption_stats)
        
        return {
            'pue': float(pue),
            'wue': float(wue),
            'cue': float(cue),
            'water_efficiency_score': float(water_efficiency_metrics['overall_efficiency']),
            'energy_efficiency_score': float(1.0 / pue if pue > 0 else 0.0),
            'efficiency_trends': efficiency_trends,
            'ml_predicted_efficiency': float(efficiency_prediction),
            'efficiency_grade': self._grade_efficiency(pue, wue)
        }
    
    async def _assess_sustainability(self, efficiency_analysis: Dict[str, Any], request: DataCenterAnalysisRequest) -> SustainabilityAssessment:
        """Assess sustainability using ML models"""
        self.logger.info("Assessing sustainability")
        
        # Extract sustainability features
        features = self._extract_sustainability_features(efficiency_analysis, request)
        
        # Normalize features
        features_normalized = self.feature_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict sustainability score using ML
        sustainability_score = self.sustainability_assessor.predict(features_normalized)[0]
        
        # Calculate detailed sustainability metrics
        water_efficiency_score = efficiency_analysis['water_efficiency_score']
        energy_efficiency_score = efficiency_analysis['energy_efficiency_score']
        carbon_efficiency_score = self._calculate_carbon_efficiency_score(efficiency_analysis, request)
        
        # Calculate renewable energy usage
        renewable_energy_usage = self._calculate_renewable_energy_usage(request)
        
        # Calculate water recycling rate
        water_recycling_rate = self._calculate_water_recycling_rate(request)
        
        # Calculate waste heat recovery
        waste_heat_recovery = self._calculate_waste_heat_recovery(efficiency_analysis, request)
        
        return SustainabilityAssessment(
            facility_id=request.id,
            assessment_date=datetime.utcnow(),
            sustainability_score=float(sustainability_score),
            water_efficiency_score=float(water_efficiency_score),
            energy_efficiency_score=float(energy_efficiency_score),
            carbon_efficiency_score=float(carbon_efficiency_score),
            renewable_energy_usage=float(renewable_energy_usage),
            water_recycling_rate=float(water_recycling_rate),
            waste_heat_recovery=float(waste_heat_recovery)
        )
    
    async def _identify_optimization_opportunities(self, consumption_analysis: Dict[str, Any], efficiency_analysis: Dict[str, Any], 
                                                 request: DataCenterAnalysisRequest) -> List[str]:
        """Identify optimization opportunities"""
        self.logger.info("Identifying optimization opportunities")
        
        # Extract optimization features
        features = self._extract_optimization_features(consumption_analysis, efficiency_analysis, request)
        
        # Normalize features
        features_normalized = self.feature_scaler.fit_transform(features.reshape(1, -1))
        
        # Predict optimization potential using ML
        optimization_potential = self.optimization_model.predict(features_normalized)[0]
        
        # Generate optimization recommendations
        recommendations = []
        
        # Efficiency-based recommendations
        if efficiency_analysis['pue'] > self.pue_threshold:
            recommendations.append("Implement advanced cooling systems")
            recommendations.append("Optimize airflow management")
            recommendations.append("Upgrade to energy-efficient IT equipment")
        
        if efficiency_analysis['wue'] > self.wue_threshold:
            recommendations.append("Implement water-efficient cooling technologies")
            recommendations.append("Optimize cooling tower operations")
            recommendations.append("Implement water recycling systems")
        
        # Consumption-based recommendations
        if consumption_analysis['consumption_anomalies']['anomaly_count'] > 5:
            recommendations.append("Implement real-time monitoring and alerting")
            recommendations.append("Optimize load distribution")
            recommendations.append("Implement predictive maintenance")
        
        # Sustainability-based recommendations
        if efficiency_analysis['efficiency_grade'] in ['D', 'F']:
            recommendations.append("Implement comprehensive efficiency improvement program")
            recommendations.append("Consider renewable energy integration")
            recommendations.append("Implement waste heat recovery systems")
        
        # Cooling system-specific recommendations
        cooling_recommendations = self._generate_cooling_specific_recommendations(request.cooling_system_type, efficiency_analysis)
        recommendations.extend(cooling_recommendations)
        
        return recommendations
    
    async def _calculate_cost_analysis(self, consumption_analysis: Dict[str, Any], efficiency_analysis: Dict[str, Any], 
                                     request: DataCenterAnalysisRequest) -> Dict[str, Any]:
        """Calculate cost analysis"""
        self.logger.info("Calculating cost analysis")
        
        consumption_stats = consumption_analysis['consumption_stats']
        
        # Calculate operational costs
        water_cost = consumption_stats['total_water'] * 0.001  # $0.001 per liter
        energy_cost = consumption_stats['total_energy'] * 0.12  # $0.12 per kWh
        total_operational_cost = water_cost + energy_cost
        
        # Calculate efficiency savings potential
        current_pue = efficiency_analysis['pue']
        target_pue = 1.3  # Target PUE
        energy_savings_potential = consumption_stats['it_energy'] * (current_pue - target_pue) * 0.12
        
        current_wue = efficiency_analysis['wue']
        target_wue = 0.3  # Target WUE
        water_savings_potential = consumption_stats['it_energy'] * (current_wue - target_wue) * 0.001
        
        total_savings_potential = energy_savings_potential + water_savings_potential
        
        # Calculate ROI for optimization measures
        optimization_cost = 500000  # Estimated optimization cost
        roi = (total_savings_potential / optimization_cost) * 100 if optimization_cost > 0 else 0
        
        return {
            'total_operational_cost': float(total_operational_cost),
            'water_cost': float(water_cost),
            'energy_cost': float(energy_cost),
            'energy_savings_potential': float(energy_savings_potential),
            'water_savings_potential': float(water_savings_potential),
            'total_savings_potential': float(total_savings_potential),
            'optimization_cost': float(optimization_cost),
            'roi_percentage': float(roi),
            'payback_period_years': float(optimization_cost / total_savings_potential) if total_savings_potential > 0 else 0
        }
    
    async def _assess_environmental_impact(self, consumption_analysis: Dict[str, Any], efficiency_analysis: Dict[str, Any], 
                                         request: DataCenterAnalysisRequest) -> Dict[str, Any]:
        """Assess environmental impact"""
        self.logger.info("Assessing environmental impact")
        
        consumption_stats = consumption_analysis['consumption_stats']
        
        # Calculate carbon footprint
        carbon_footprint = consumption_stats['total_energy'] * self.carbon_intensity
        
        # Calculate water footprint
        water_footprint = consumption_stats['total_water']
        
        # Calculate environmental efficiency
        carbon_efficiency = consumption_stats['it_energy'] / carbon_footprint if carbon_footprint > 0 else 0
        water_efficiency = consumption_stats['it_energy'] / water_footprint if water_footprint > 0 else 0
        
        # Calculate environmental impact score
        impact_score = self._calculate_environmental_impact_score(carbon_footprint, water_footprint, efficiency_analysis)
        
        return {
            'carbon_footprint': float(carbon_footprint),
            'water_footprint': float(water_footprint),
            'carbon_efficiency': float(carbon_efficiency),
            'water_efficiency': float(water_efficiency),
            'environmental_impact_score': float(impact_score),
            'impact_grade': self._grade_environmental_impact(impact_score)
        }
    
    async def _generate_facility_summary(self, request: DataCenterAnalysisRequest, consumption_analysis: Dict[str, Any], 
                                       efficiency_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate facility summary"""
        return {
            'name': request.facility_name,
            'type': request.cooling_system_type,
            'size': request.facility_size,
            'location': request.location,
            'total_water_consumption': consumption_analysis['consumption_stats']['total_water'],
            'total_energy_consumption': consumption_analysis['consumption_stats']['total_energy'],
            'pue': efficiency_analysis['pue'],
            'wue': efficiency_analysis['wue'],
            'efficiency_grade': efficiency_analysis['efficiency_grade']
        }
    
    def _calculate_consumption_statistics(self, water_usage: np.ndarray, energy_consumption: np.ndarray, it_load: np.ndarray) -> Dict[str, float]:
        """Calculate consumption statistics"""
        return {
            'total_water': float(np.sum(water_usage)),
            'total_energy': float(np.sum(energy_consumption)),
            'it_energy': float(np.sum(it_load)),
            'avg_water_usage': float(np.mean(water_usage)),
            'avg_energy_consumption': float(np.mean(energy_consumption)),
            'avg_it_load': float(np.mean(it_load)),
            'peak_water_usage': float(np.max(water_usage)),
            'peak_energy_consumption': float(np.max(energy_consumption)),
            'water_usage_variance': float(np.var(water_usage)),
            'energy_consumption_variance': float(np.var(energy_consumption))
        }
    
    def _analyze_consumption_patterns(self, water_usage: np.ndarray, energy_consumption: np.ndarray, 
                                    it_load: np.ndarray, timestamps: List[str]) -> Dict[str, Any]:
        """Analyze consumption patterns"""
        # Calculate correlation between water and energy usage
        water_energy_correlation = np.corrcoef(water_usage, energy_consumption)[0, 1]
        
        # Calculate correlation between IT load and water usage
        it_water_correlation = np.corrcoef(it_load, water_usage)[0, 1]
        
        # Identify peak usage periods
        peak_water_periods = np.where(water_usage > np.percentile(water_usage, 90))[0]
        peak_energy_periods = np.where(energy_consumption > np.percentile(energy_consumption, 90))[0]
        
        return {
            'water_energy_correlation': float(water_energy_correlation),
            'it_water_correlation': float(it_water_correlation),
            'peak_water_periods': len(peak_water_periods),
            'peak_energy_periods': len(peak_energy_periods),
            'consumption_efficiency': float(np.mean(it_load) / np.mean(water_usage)) if np.mean(water_usage) > 0 else 0.0
        }
    
    def _calculate_water_efficiency_metrics(self, water_usage: np.ndarray, energy_consumption: np.ndarray, it_load: np.ndarray) -> Dict[str, float]:
        """Calculate water efficiency metrics"""
        # Calculate Water Usage Effectiveness (WUE)
        wue = np.sum(water_usage) / np.sum(it_load) if np.sum(it_load) > 0 else 0
        
        # Calculate water efficiency score
        target_wue = 0.3  # Target WUE
        efficiency_score = max(0, 1 - (wue - target_wue) / target_wue) if target_wue > 0 else 0
        
        # Calculate water intensity
        water_intensity = np.mean(water_usage) / np.mean(energy_consumption) if np.mean(energy_consumption) > 0 else 0
        
        return {
            'wue': float(wue),
            'overall_efficiency': float(efficiency_score),
            'water_intensity': float(water_intensity),
            'efficiency_rating': 'excellent' if efficiency_score > 0.8 else 'good' if efficiency_score > 0.6 else 'fair' if efficiency_score > 0.4 else 'poor'
        }
    
    def _detect_consumption_anomalies(self, water_usage: np.ndarray, energy_consumption: np.ndarray, it_load: np.ndarray) -> Dict[str, Any]:
        """Detect consumption anomalies"""
        # Calculate z-scores for anomaly detection
        water_z_scores = np.abs((water_usage - np.mean(water_usage)) / np.std(water_usage))
        energy_z_scores = np.abs((energy_consumption - np.mean(energy_consumption)) / np.std(energy_consumption))
        
        # Identify anomalies (z-score > 2)
        water_anomalies = np.where(water_z_scores > 2)[0]
        energy_anomalies = np.where(energy_z_scores > 2)[0]
        
        # Calculate anomaly severity
        water_anomaly_severity = np.mean(water_z_scores[water_anomalies]) if len(water_anomalies) > 0 else 0
        energy_anomaly_severity = np.mean(energy_z_scores[energy_anomalies]) if len(energy_anomalies) > 0 else 0
        
        return {
            'water_anomalies': len(water_anomalies),
            'energy_anomalies': len(energy_anomalies),
            'total_anomalies': len(water_anomalies) + len(energy_anomalies),
            'water_anomaly_severity': float(water_anomaly_severity),
            'energy_anomaly_severity': float(energy_anomaly_severity),
            'anomaly_count': len(water_anomalies) + len(energy_anomalies)
        }
    
    def _assess_data_quality(self, water_usage: np.ndarray, energy_consumption: np.ndarray, it_load: np.ndarray) -> Dict[str, float]:
        """Assess data quality"""
        # Calculate completeness
        completeness = 1.0 - (np.sum(np.isnan(water_usage)) + np.sum(np.isnan(energy_consumption)) + np.sum(np.isnan(it_load))) / (len(water_usage) * 3)
        
        # Calculate consistency
        water_consistency = 1.0 - np.std(water_usage) / np.mean(water_usage) if np.mean(water_usage) > 0 else 0.0
        energy_consistency = 1.0 - np.std(energy_consumption) / np.mean(energy_consumption) if np.mean(energy_consumption) > 0 else 0.0
        
        consistency = (water_consistency + energy_consistency) / 2
        
        return {
            'completeness': float(completeness),
            'consistency': float(consistency),
            'overall_quality': float((completeness + consistency) / 2)
        }
    
    def _extract_efficiency_features(self, consumption_stats: Dict[str, float], water_efficiency_metrics: Dict[str, float], 
                                   request: DataCenterAnalysisRequest) -> np.ndarray:
        """Extract features for efficiency analysis"""
        features = [
            consumption_stats['total_water'],
            consumption_stats['total_energy'],
            consumption_stats['it_energy'],
            consumption_stats['avg_water_usage'],
            consumption_stats['avg_energy_consumption'],
            water_efficiency_metrics['wue'],
            water_efficiency_metrics['overall_efficiency'],
            request.facility_size.value if hasattr(request.facility_size, 'value') else 1,
            request.cooling_system_type.value if hasattr(request.cooling_system_type, 'value') else 1
        ]
        
        return np.array(features)
    
    def _calculate_pue(self, total_energy: float, it_energy: float) -> float:
        """Calculate Power Usage Effectiveness (PUE)"""
        return total_energy / it_energy if it_energy > 0 else 0.0
    
    def _calculate_wue(self, total_water: float, it_energy: float) -> float:
        """Calculate Water Usage Effectiveness (WUE)"""
        return total_water / it_energy if it_energy > 0 else 0.0
    
    def _calculate_cue(self, total_energy: float, facility_size: FacilitySize) -> float:
        """Calculate Carbon Usage Effectiveness (CUE)"""
        # Simplified CUE calculation
        carbon_footprint = total_energy * self.carbon_intensity
        facility_area = facility_size.value if hasattr(facility_size, 'value') else 1000
        return carbon_footprint / facility_area if facility_area > 0 else 0.0
    
    def _calculate_efficiency_trends(self, consumption_stats: Dict[str, float]) -> Dict[str, str]:
        """Calculate efficiency trends"""
        # Simplified trend analysis
        if consumption_stats['water_usage_variance'] < 0.1:
            water_trend = "stable"
        elif consumption_stats['avg_water_usage'] > consumption_stats['total_water'] / 1000:
            water_trend = "increasing"
        else:
            water_trend = "decreasing"
        
        if consumption_stats['energy_consumption_variance'] < 0.1:
            energy_trend = "stable"
        elif consumption_stats['avg_energy_consumption'] > consumption_stats['total_energy'] / 1000:
            energy_trend = "increasing"
        else:
            energy_trend = "decreasing"
        
        return {
            'water_trend': water_trend,
            'energy_trend': energy_trend
        }
    
    def _grade_efficiency(self, pue: float, wue: float) -> str:
        """Grade efficiency performance"""
        pue_score = 1.0 / pue if pue > 0 else 0.0
        wue_score = 1.0 - min(1.0, wue / 1.0)  # Normalize WUE
        
        overall_score = (pue_score + wue_score) / 2
        
        if overall_score >= 0.8:
            return "A"
        elif overall_score >= 0.6:
            return "B"
        elif overall_score >= 0.4:
            return "C"
        elif overall_score >= 0.2:
            return "D"
        else:
            return "F"
    
    def _extract_sustainability_features(self, efficiency_analysis: Dict[str, Any], request: DataCenterAnalysisRequest) -> np.ndarray:
        """Extract features for sustainability assessment"""
        features = [
            efficiency_analysis['pue'],
            efficiency_analysis['wue'],
            efficiency_analysis['water_efficiency_score'],
            efficiency_analysis['energy_efficiency_score'],
            request.facility_size.value if hasattr(request.facility_size, 'value') else 1,
            request.cooling_system_type.value if hasattr(request.cooling_system_type, 'value') else 1
        ]
        
        return np.array(features)
    
    def _calculate_carbon_efficiency_score(self, efficiency_analysis: Dict[str, Any], request: DataCenterAnalysisRequest) -> float:
        """Calculate carbon efficiency score"""
        pue = efficiency_analysis['pue']
        # Lower PUE means better carbon efficiency
        carbon_efficiency = max(0, 1 - (pue - 1.0) / 1.0)  # Normalize to 0-1
        return carbon_efficiency
    
    def _calculate_renewable_energy_usage(self, request: DataCenterAnalysisRequest) -> float:
        """Calculate renewable energy usage percentage"""
        # Simplified calculation based on facility type
        if request.cooling_system_type == CoolingSystemType.ADVANCED:
            return 0.3  # 30% renewable energy
        elif request.cooling_system_type == CoolingSystemType.MODERN:
            return 0.2  # 20% renewable energy
        else:
            return 0.1  # 10% renewable energy
    
    def _calculate_water_recycling_rate(self, request: DataCenterAnalysisRequest) -> float:
        """Calculate water recycling rate"""
        # Simplified calculation based on cooling system type
        if request.cooling_system_type == CoolingSystemType.ADVANCED:
            return 0.8  # 80% recycling rate
        elif request.cooling_system_type == CoolingSystemType.MODERN:
            return 0.6  # 60% recycling rate
        else:
            return 0.4  # 40% recycling rate
    
    def _calculate_waste_heat_recovery(self, efficiency_analysis: Dict[str, Any], request: DataCenterAnalysisRequest) -> float:
        """Calculate waste heat recovery percentage"""
        # Simplified calculation based on efficiency and cooling system
        base_recovery = 0.3  # 30% base recovery
        
        if efficiency_analysis['pue'] < 1.3:
            base_recovery += 0.2  # Additional recovery for efficient facilities
        
        if request.cooling_system_type == CoolingSystemType.ADVANCED:
            base_recovery += 0.2  # Additional recovery for advanced cooling
        
        return min(1.0, base_recovery)
    
    def _extract_optimization_features(self, consumption_analysis: Dict[str, Any], efficiency_analysis: Dict[str, Any], 
                                     request: DataCenterAnalysisRequest) -> np.ndarray:
        """Extract features for optimization analysis"""
        features = [
            efficiency_analysis['pue'],
            efficiency_analysis['wue'],
            efficiency_analysis['water_efficiency_score'],
            efficiency_analysis['energy_efficiency_score'],
            consumption_analysis['consumption_anomalies']['anomaly_count'],
            request.facility_size.value if hasattr(request.facility_size, 'value') else 1,
            request.cooling_system_type.value if hasattr(request.cooling_system_type, 'value') else 1
        ]
        
        return np.array(features)
    
    def _generate_cooling_specific_recommendations(self, cooling_system_type: CoolingSystemType, efficiency_analysis: Dict[str, Any]) -> List[str]:
        """Generate cooling system-specific recommendations"""
        recommendations = []
        
        if cooling_system_type == CoolingSystemType.TRADITIONAL:
            recommendations.extend([
                "Upgrade to modern cooling systems",
                "Implement free cooling technologies",
                "Optimize cooling tower operations"
            ])
        elif cooling_system_type == CoolingSystemType.MODERN:
            recommendations.extend([
                "Implement advanced cooling controls",
                "Optimize chiller operations",
                "Consider liquid cooling systems"
            ])
        elif cooling_system_type == CoolingSystemType.ADVANCED:
            recommendations.extend([
                "Implement AI-driven cooling optimization",
                "Consider immersion cooling",
                "Optimize thermal management systems"
            ])
        
        return recommendations
    
    def _calculate_environmental_impact_score(self, carbon_footprint: float, water_footprint: float, efficiency_analysis: Dict[str, Any]) -> float:
        """Calculate environmental impact score"""
        # Normalize impacts
        carbon_impact = min(1.0, carbon_footprint / 1000000)  # Normalize to 1M kg CO2
        water_impact = min(1.0, water_footprint / 1000000)    # Normalize to 1M liters
        
        # Weighted combination
        impact_score = carbon_impact * 0.6 + water_impact * 0.4
        
        # Adjust based on efficiency
        efficiency_factor = (efficiency_analysis['water_efficiency_score'] + efficiency_analysis['energy_efficiency_score']) / 2
        impact_score *= (1 - efficiency_factor * 0.3)  # Reduce impact for efficient facilities
        
        return max(0.0, min(1.0, impact_score))
    
    def _grade_environmental_impact(self, impact_score: float) -> str:
        """Grade environmental impact"""
        if impact_score < 0.2:
            return "A"
        elif impact_score < 0.4:
            return "B"
        elif impact_score < 0.6:
            return "C"
        elif impact_score < 0.8:
            return "D"
        else:
            return "F" 