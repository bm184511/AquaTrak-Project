"""
Country Configuration for AquaTrak
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class CountryCategory(Enum):
    """Country categories for AquaTrak"""
    CORE_WATER_MANAGEMENT = "core_water_management"
    STARTUP_ECOSYSTEM = "startup_ecosystem"
    REGIONAL = "regional"


@dataclass
class CountryInfo:
    """Country information structure"""
    code: str
    name: str
    native_name: str
    flag: str
    languages: List[str]
    primary_language: str
    category: CountryCategory
    water_management_score: float
    startup_ecosystem_score: float
    gdp_per_capita: Optional[float] = None
    population: Optional[int] = None
    region: Optional[str] = None


# Core supported countries with strong water management
CORE_WATER_MANAGEMENT_COUNTRIES = {
    "CA": CountryInfo(
        code="CA",
        name="Canada",
        native_name="Canada",
        flag="🇨🇦",
        languages=["en", "fr"],
        primary_language="en",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.95,
        startup_ecosystem_score=0.85,
        gdp_per_capita=52000.0,
        population=38000000,
        region="North America"
    ),
    "DE": CountryInfo(
        code="DE",
        name="Germany",
        native_name="Deutschland",
        flag="🇩🇪",
        languages=["de", "en"],
        primary_language="de",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.92,
        startup_ecosystem_score=0.88,
        gdp_per_capita=48000.0,
        population=83000000,
        region="Europe"
    ),
    "NL": CountryInfo(
        code="NL",
        name="Netherlands",
        native_name="Nederland",
        flag="🇳🇱",
        languages=["nl", "en"],
        primary_language="nl",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.98,
        startup_ecosystem_score=0.82,
        gdp_per_capita=52000.0,
        population=17000000,
        region="Europe"
    ),
    "FR": CountryInfo(
        code="FR",
        name="France",
        native_name="France",
        flag="🇫🇷",
        languages=["fr", "en"],
        primary_language="fr",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.90,
        startup_ecosystem_score=0.80,
        gdp_per_capita=42000.0,
        population=67000000,
        region="Europe"
    ),
    "SE": CountryInfo(
        code="SE",
        name="Sweden",
        native_name="Sverige",
        flag="🇸🇪",
        languages=["sv", "en"],
        primary_language="sv",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.94,
        startup_ecosystem_score=0.85,
        gdp_per_capita=54000.0,
        population=10000000,
        region="Europe"
    ),
    "FI": CountryInfo(
        code="FI",
        name="Finland",
        native_name="Suomi",
        flag="🇫🇮",
        languages=["fi", "sv", "en"],
        primary_language="fi",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.96,
        startup_ecosystem_score=0.83,
        gdp_per_capita=48000.0,
        population=5500000,
        region="Europe"
    ),
    "DK": CountryInfo(
        code="DK",
        name="Denmark",
        native_name="Danmark",
        flag="🇩🇰",
        languages=["da", "en"],
        primary_language="da",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.93,
        startup_ecosystem_score=0.84,
        gdp_per_capita=58000.0,
        population=5800000,
        region="Europe"
    ),
    "NO": CountryInfo(
        code="NO",
        name="Norway",
        native_name="Norge",
        flag="🇳🇴",
        languages=["no", "en"],
        primary_language="no",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.95,
        startup_ecosystem_score=0.81,
        gdp_per_capita=75000.0,
        population=5400000,
        region="Europe"
    ),
    "CH": CountryInfo(
        code="CH",
        name="Switzerland",
        native_name="Schweiz",
        flag="🇨🇭",
        languages=["de", "fr", "it", "en"],
        primary_language="de",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.97,
        startup_ecosystem_score=0.87,
        gdp_per_capita=82000.0,
        population=8600000,
        region="Europe"
    ),
    "BE": CountryInfo(
        code="BE",
        name="Belgium",
        native_name="België",
        flag="🇧🇪",
        languages=["nl", "fr", "en"],
        primary_language="nl",
        category=CountryCategory.CORE_WATER_MANAGEMENT,
        water_management_score=0.89,
        startup_ecosystem_score=0.79,
        gdp_per_capita=46000.0,
        population=11500000,
        region="Europe"
    )
}

# Startup ecosystem countries
STARTUP_ECOSYSTEM_COUNTRIES = {
    "PT": CountryInfo(
        code="PT",
        name="Portugal",
        native_name="Portugal",
        flag="🇵🇹",
        languages=["pt", "en"],
        primary_language="pt",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.75,
        startup_ecosystem_score=0.70,
        gdp_per_capita=24000.0,
        population=10300000,
        region="Europe"
    ),
    "GB": CountryInfo(
        code="GB",
        name="United Kingdom",
        native_name="United Kingdom",
        flag="🇬🇧",
        languages=["en"],
        primary_language="en",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.85,
        startup_ecosystem_score=0.90,
        gdp_per_capita=42000.0,
        population=67000000,
        region="Europe"
    ),
    "AU": CountryInfo(
        code="AU",
        name="Australia",
        native_name="Australia",
        flag="🇦🇺",
        languages=["en"],
        primary_language="en",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.80,
        startup_ecosystem_score=0.78,
        gdp_per_capita=55000.0,
        population=25000000,
        region="Oceania"
    ),
    "NZ": CountryInfo(
        code="NZ",
        name="New Zealand",
        native_name="Aotearoa",
        flag="🇳🇿",
        languages=["en", "mi"],
        primary_language="en",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.82,
        startup_ecosystem_score=0.72,
        gdp_per_capita=42000.0,
        population=5000000,
        region="Oceania"
    ),
    "SG": CountryInfo(
        code="SG",
        name="Singapore",
        native_name="Singapore",
        flag="🇸🇬",
        languages=["en", "zh", "ms", "ta"],
        primary_language="en",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.88,
        startup_ecosystem_score=0.92,
        gdp_per_capita=65000.0,
        population=5700000,
        region="Asia"
    ),
    "US": CountryInfo(
        code="US",
        name="United States",
        native_name="United States",
        flag="🇺🇸",
        languages=["en", "es"],
        primary_language="en",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.78,
        startup_ecosystem_score=0.95,
        gdp_per_capita=63000.0,
        population=330000000,
        region="North America"
    ),
    "CL": CountryInfo(
        code="CL",
        name="Chile",
        native_name="Chile",
        flag="🇨🇱",
        languages=["es", "en"],
        primary_language="es",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.70,
        startup_ecosystem_score=0.65,
        gdp_per_capita=15000.0,
        population=19000000,
        region="South America"
    ),
    "KR": CountryInfo(
        code="KR",
        name="South Korea",
        native_name="대한민국",
        flag="🇰🇷",
        languages=["ko", "en"],
        primary_language="ko",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.75,
        startup_ecosystem_score=0.85,
        gdp_per_capita=32000.0,
        population=51000000,
        region="Asia"
    ),
    "IE": CountryInfo(
        code="IE",
        name="Ireland",
        native_name="Éire",
        flag="🇮🇪",
        languages=["en", "ga"],
        primary_language="en",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.80,
        startup_ecosystem_score=0.88,
        gdp_per_capita=85000.0,
        population=4900000,
        region="Europe"
    ),
    "ES": CountryInfo(
        code="ES",
        name="Spain",
        native_name="España",
        flag="🇪🇸",
        languages=["es", "ca", "eu", "gl", "en"],
        primary_language="es",
        category=CountryCategory.STARTUP_ECOSYSTEM,
        water_management_score=0.72,
        startup_ecosystem_score=0.68,
        gdp_per_capita=30000.0,
        population=47000000,
        region="Europe"
    )
}

# Regional countries (existing support)
REGIONAL_COUNTRIES = {
    "IR": CountryInfo(
        code="IR",
        name="Iran",
        native_name="ایران",
        flag="🇮🇷",
        languages=["fa", "en"],
        primary_language="fa",
        category=CountryCategory.REGIONAL,
        water_management_score=0.60,
        startup_ecosystem_score=0.45,
        gdp_per_capita=5000.0,
        population=84000000,
        region="Middle East"
    ),
    "TR": CountryInfo(
        code="TR",
        name="Turkey",
        native_name="Türkiye",
        flag="🇹🇷",
        languages=["tr", "en"],
        primary_language="tr",
        category=CountryCategory.REGIONAL,
        water_management_score=0.65,
        startup_ecosystem_score=0.55,
        gdp_per_capita=9500.0,
        population=84000000,
        region="Middle East"
    ),
    # Add more regional countries as needed
}

# Combine all countries
ALL_COUNTRIES = {**CORE_WATER_MANAGEMENT_COUNTRIES, **STARTUP_ECOSYSTEM_COUNTRIES, **REGIONAL_COUNTRIES}

# Supported country codes
SUPPORTED_COUNTRY_CODES = list(ALL_COUNTRIES.keys())

# Supported languages from all countries
SUPPORTED_LANGUAGES = []
for country in ALL_COUNTRIES.values():
    SUPPORTED_LANGUAGES.extend(country.languages)
SUPPORTED_LANGUAGES = list(set(SUPPORTED_LANGUAGES))  # Remove duplicates


def get_country_info(country_code: str) -> Optional[CountryInfo]:
    """Get country information by country code"""
    return ALL_COUNTRIES.get(country_code.upper())


def get_countries_by_category(category: CountryCategory) -> List[CountryInfo]:
    """Get all countries in a specific category"""
    return [country for country in ALL_COUNTRIES.values() if country.category == category]


def get_countries_by_region(region: str) -> List[CountryInfo]:
    """Get all countries in a specific region"""
    return [country for country in ALL_COUNTRIES.values() if country.region == region]


def get_countries_by_language(language_code: str) -> List[CountryInfo]:
    """Get all countries that support a specific language"""
    return [country for country in ALL_COUNTRIES.values() if language_code in country.languages]


def is_country_supported(country_code: str) -> bool:
    """Check if a country is supported"""
    return country_code.upper() in SUPPORTED_COUNTRY_CODES


def get_primary_language(country_code: str) -> Optional[str]:
    """Get the primary language for a country"""
    country = get_country_info(country_code)
    return country.primary_language if country else None


def get_supported_languages(country_code: str) -> List[str]:
    """Get all supported languages for a country"""
    country = get_country_info(country_code)
    return country.languages if country else []


def get_water_management_leaders() -> List[CountryInfo]:
    """Get countries with the highest water management scores"""
    sorted_countries = sorted(ALL_COUNTRIES.values(), key=lambda x: x.water_management_score, reverse=True)
    return sorted_countries[:10]


def get_startup_ecosystem_leaders() -> List[CountryInfo]:
    """Get countries with the highest startup ecosystem scores"""
    sorted_countries = sorted(ALL_COUNTRIES.values(), key=lambda x: x.startup_ecosystem_score, reverse=True)
    return sorted_countries[:10]


def get_country_statistics() -> Dict[str, any]:
    """Get statistics about supported countries"""
    total_countries = len(ALL_COUNTRIES)
    core_countries = len(CORE_WATER_MANAGEMENT_COUNTRIES)
    startup_countries = len(STARTUP_ECOSYSTEM_COUNTRIES)
    regional_countries = len(REGIONAL_COUNTRIES)
    
    total_population = sum(country.population or 0 for country in ALL_COUNTRIES.values())
    avg_gdp = sum(country.gdp_per_capita or 0 for country in ALL_COUNTRIES.values()) / total_countries
    
    return {
        "total_countries": total_countries,
        "core_water_management_countries": core_countries,
        "startup_ecosystem_countries": startup_countries,
        "regional_countries": regional_countries,
        "total_population": total_population,
        "average_gdp_per_capita": avg_gdp,
        "supported_languages": len(SUPPORTED_LANGUAGES),
        "regions": list(set(country.region for country in ALL_COUNTRIES.values() if country.region))
    } 