"""
IoT Water Consumption Processor
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

from .models import *

logger = logging.getLogger(__name__)

class IoTWaterConsumptionProcessor:
    """Processor for IoT-based industrial water consumption analysis with advanced AI/ML"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing IoTWaterConsumptionProcessor with AI/ML capabilities")
        self.anomaly_model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.forecast_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.historical_data = []

    async def process_analysis(self, request: IoTConsumptionAnalysisRequest) -> IoTConsumptionResult:
        """Process IoT water consumption analysis with AI/ML"""
        start_time = datetime.utcnow()
        self.logger.info(f"Processing IoT water consumption analysis for request {request.id}")
        try:
            # Prepare time series data
            ts_data = await self._prepare_time_series(request)
            # Anomaly detection
            anomalies = await self.detect_anomalies(ts_data)
            # Forecasting
            forecast = await self.forecast_consumption(ts_data)
            # Efficiency metrics
            efficiency = await self.calculate_efficiency(ts_data)
            # Optimization recommendations
            recommendations = await self.generate_recommendations(ts_data, anomalies, efficiency)
            # Cost savings analysis
            cost_savings = await self.calculate_cost_savings(ts_data, efficiency)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result = IoTConsumptionResult(
                analysis_id=request.id,
                time_series_summary=await self._generate_summary(ts_data),
                anomalies=anomalies,
                forecast=forecast,
                efficiency_metrics=efficiency,
                recommendations=recommendations,
                cost_savings=cost_savings,
                processing_time=processing_time
            )
            self.historical_data.append({'ts_data': ts_data, 'result': result, 'timestamp': datetime.utcnow()})
            return result
        except Exception as e:
            self.logger.error(f"Error in IoT water consumption analysis: {str(e)}")
            raise

    async def _prepare_time_series(self, request: IoTConsumptionAnalysisRequest) -> pd.DataFrame:
        """Prepare and clean time series data from request"""
        try:
            # Simulate IoT data (replace with real data ingestion in production)
            np.random.seed(42)
            periods = 365 if not request.periods else request.periods
            date_rng = pd.date_range(end=datetime.utcnow(), periods=periods, freq='D')
            base = np.random.normal(loc=1000, scale=200, size=periods)
            seasonal = 100 * np.sin(np.linspace(0, 2 * np.pi, periods))
            trend = np.linspace(0, 200, periods)
            noise = np.random.normal(0, 50, periods)
            consumption = base + seasonal + trend + noise
            df = pd.DataFrame({'date': date_rng, 'consumption': consumption})
            df.set_index('date', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error preparing time series: {str(e)}")
            return pd.DataFrame()

    async def detect_anomalies(self, ts_data: pd.DataFrame) -> List[AnomalyDetection]:
        """Detect anomalies in water consumption using Isolation Forest"""
        try:
            if ts_data.empty:
                return []
            X = ts_data['consumption'].values.reshape(-1, 1)
            X_scaled = self.scaler.fit_transform(X)
            preds = self.anomaly_model.fit_predict(X_scaled)
            anomalies = np.where(preds == -1)[0]
            results = []
            for idx in anomalies:
                results.append(AnomalyDetection(
                    timestamp=ts_data.index[idx],
                    value=ts_data.iloc[idx]['consumption'],
                    anomaly_score=float(X_scaled[idx][0])
                ))
            return results
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            return []

    async def forecast_consumption(self, ts_data: pd.DataFrame) -> List[ForecastResult]:
        """Forecast future water consumption using ARIMA and Random Forest"""
        try:
            if ts_data.empty:
                return []
            # STL decomposition for trend/seasonality
            stl = STL(ts_data['consumption'], period=30)
            res = stl.fit()
            trend = res.trend
            seasonal = res.seasonal
            resid = res.resid
            # ARIMA for short-term forecast
            arima = ARIMA(ts_data['consumption'], order=(1,1,1))
            arima_fit = arima.fit()
            arima_forecast = arima_fit.forecast(steps=14)
            # Random Forest for longer-term forecast
            X = np.arange(len(ts_data)).reshape(-1, 1)
            y = ts_data['consumption'].values
            self.forecast_model.fit(X, y)
            X_future = np.arange(len(ts_data), len(ts_data)+30).reshape(-1, 1)
            rf_forecast = self.forecast_model.predict(X_future)
            # Combine forecasts
            forecast_results = []
            for i, value in enumerate(arima_forecast):
                forecast_results.append(ForecastResult(
                    timestamp=ts_data.index[-1] + timedelta(days=i+1),
                    predicted_value=float(value),
                    model="ARIMA"
                ))
            for i, value in enumerate(rf_forecast):
                forecast_results.append(ForecastResult(
                    timestamp=ts_data.index[-1] + timedelta(days=15+i),
                    predicted_value=float(value),
                    model="RandomForest"
                ))
            return forecast_results
        except Exception as e:
            self.logger.error(f"Error forecasting consumption: {str(e)}")
            return []

    async def calculate_efficiency(self, ts_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate efficiency metrics for water consumption"""
        try:
            if ts_data.empty:
                return {}
            avg_consumption = ts_data['consumption'].mean()
            std_consumption = ts_data['consumption'].std()
            max_consumption = ts_data['consumption'].max()
            min_consumption = ts_data['consumption'].min()
            # Efficiency score (lower std/avg is better)
            efficiency_score = max(0.0, 1.0 - (std_consumption / avg_consumption))
            return {
                'average_consumption': avg_consumption,
                'std_consumption': std_consumption,
                'max_consumption': max_consumption,
                'min_consumption': min_consumption,
                'efficiency_score': efficiency_score
            }
        except Exception as e:
            self.logger.error(f"Error calculating efficiency: {str(e)}")
            return {}

    async def generate_recommendations(self, ts_data: pd.DataFrame, anomalies: List[AnomalyDetection], efficiency: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        try:
            recommendations = []
            if len(anomalies) > 5:
                recommendations.append("Investigate frequent anomalies in water usage patterns.")
            if efficiency.get('efficiency_score', 1.0) < 0.7:
                recommendations.append("Implement leak detection and repair protocols.")
                recommendations.append("Optimize industrial process schedules for water savings.")
            if efficiency.get('average_consumption', 0) > 1200:
                recommendations.append("Consider upgrading to high-efficiency equipment.")
            recommendations.append("Deploy real-time monitoring for continuous optimization.")
            recommendations.append("Educate staff on water conservation best practices.")
            return recommendations[:5]
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return ["Review water usage data for optimization opportunities."]

    async def calculate_cost_savings(self, ts_data: pd.DataFrame, efficiency: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost savings from optimization"""
        try:
            if ts_data.empty or not efficiency:
                return {}
            baseline = 1300  # Baseline average consumption (liters/day)
            avg = efficiency.get('average_consumption', baseline)
            price_per_liter = 0.002  # Example price
            potential_savings = max(0, baseline - avg) * price_per_liter * 365
            return {
                'annual_cost_savings_usd': potential_savings,
                'baseline_consumption': baseline,
                'actual_consumption': avg
            }
        except Exception as e:
            self.logger.error(f"Error calculating cost savings: {str(e)}")
            return {}

    async def _generate_summary(self, ts_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for the time series"""
        try:
            if ts_data.empty:
                return {}
            return {
                'start_date': str(ts_data.index[0]),
                'end_date': str(ts_data.index[-1]),
                'total_days': len(ts_data),
                'total_consumption': float(ts_data['consumption'].sum())
            }
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return {} 