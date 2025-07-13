"""
Configuration Package
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from .settings import get_settings
from .database import get_db, get_db_context, init_db, check_db_connection
from .countries import ALL_COUNTRIES, get_country_info, SUPPORTED_COUNTRY_CODES

__all__ = [
    'get_settings',
    'get_db',
    'get_db_context',
    'init_db',
    'check_db_connection',
    'ALL_COUNTRIES',
    'get_country_info',
    'SUPPORTED_COUNTRY_CODES'
] 