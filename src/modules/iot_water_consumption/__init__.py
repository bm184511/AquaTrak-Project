"""
IoT Industrial Water Consumption Module
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from .models import *
from .processor import *
from .api import *

__version__ = "1.0.0"
__author__ = "AquaTrak Development Team"
__all__ = ["IoTWaterProcessor", "WaterConsumptionModel", "IoTDeviceData"] 