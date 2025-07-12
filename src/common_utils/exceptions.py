"""
Common Exceptions
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

class AquaTrakException(Exception):
    """Base exception for AquaTrak application"""
    pass

class DataImportError(AquaTrakException):
    """Exception raised during data import operations"""
    pass

class DatabaseError(AquaTrakException):
    """Exception raised during database operations"""
    pass

class ValidationError(AquaTrakException):
    """Exception raised during data validation"""
    pass

class AuthenticationError(AquaTrakException):
    """Exception raised during authentication"""
    pass

class AuthorizationError(AquaTrakException):
    """Exception raised during authorization"""
    pass

class ConfigurationError(AquaTrakException):
    """Exception raised during configuration"""
    pass

class ProcessingError(AquaTrakException):
    """Exception raised during data processing"""
    pass

class FileError(AquaTrakException):
    """Exception raised during file operations"""
    pass 