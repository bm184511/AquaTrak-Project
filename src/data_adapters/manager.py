# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
Data Adapter Manager for AquaTrak
Manages external data source connections and data ingestion
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
import redis
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..config.settings import get_settings
from ..models.system import DataSource

logger = logging.getLogger(__name__)
settings = get_settings()

class DataAdapterManager:
    """Manages data adapters for external data sources"""
    
    def __init__(self):
        self.adapters: Dict[str, Any] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.redis_client: Optional[redis.Redis] = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the data adapter manager"""
        if self.is_initialized:
            return
            
        logger.info("Initializing Data Adapter Manager...")
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'AquaTrak/1.0.0'
            }
        )
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
        
        # Initialize data adapters
        await self._initialize_adapters()
        
        self.is_initialized = True
        logger.info("Data Adapter Manager initialized successfully")
    
    async def _initialize_adapters(self):
        """Initialize individual data adapters"""
        # Weather data adapter
        if settings.weather_api_key:
            self.adapters['weather'] = WeatherDataAdapter(
                api_key=settings.weather_api_key,
                session=self.session,
                redis_client=self.redis_client
            )
        
        # Satellite data adapter
        if settings.satellite_api_key:
            self.adapters['satellite'] = SatelliteDataAdapter(
                api_key=settings.satellite_api_key,
                session=self.session,
                redis_client=self.redis_client
            )
        
        # NOAA data adapter
        self.adapters['noaa'] = NOAADataAdapter(
            session=self.session,
            redis_client=self.redis_client
        )
        
        # Copernicus data adapter
        self.adapters['copernicus'] = CopernicusDataAdapter(
            session=self.session,
            redis_client=self.redis_client
        )
        
        logger.info(f"Initialized {len(self.adapters)} data adapters")
    
    async def get_data(self, source: str, **kwargs) -> Dict[str, Any]:
        """Get data from specified source"""
        if not self.is_initialized:
            await self.initialize()
        
        if source not in self.adapters:
            raise ValueError(f"Data source '{source}' not available")
        
        try:
            return await self.adapters[source].get_data(**kwargs)
        except Exception as e:
            logger.error(f"Error getting data from {source}: {e}")
            raise
    
    async def update_data_sources(self):
        """Update data source status in database"""
        if not self.is_initialized:
            await self.initialize()
        
        db = next(get_db())
        try:
            for source_name, adapter in self.adapters.items():
                # Check if source exists in database
                data_source = db.query(DataSource).filter(
                    DataSource.name == source_name
                ).first()
                
                if not data_source:
                    data_source = DataSource(
                        name=source_name,
                        type=adapter.source_type,
                        url=adapter.base_url,
                        status='active'
                    )
                    db.add(data_source)
                else:
                    data_source.last_updated = datetime.utcnow()
                    data_source.status = 'active'
                
                db.commit()
                logger.info(f"Updated data source: {source_name}")
                
        except Exception as e:
            logger.error(f"Error updating data sources: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Data Adapter Manager...")
        
        if self.session:
            await self.session.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.is_initialized = False
        logger.info("Data Adapter Manager cleanup completed")

class BaseDataAdapter:
    """Base class for data adapters"""
    
    def __init__(self, session: aiohttp.ClientSession, redis_client: redis.Redis):
        self.session = session
        self.redis_client = redis_client
        self.source_type = "unknown"
        self.base_url = ""
    
    async def get_data(self, **kwargs) -> Dict[str, Any]:
        """Get data from source - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache"""
        if not self.redis_client:
            return None
        
        try:
            cached = await self.redis_client.get(key)
            if cached:
                import json
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    async def _cache_set(self, key: str, data: Dict[str, Any], ttl: int = 3600):
        """Set data in cache"""
        if not self.redis_client:
            return
        
        try:
            import json
            await self.redis_client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Cache set error: {e}")

class WeatherDataAdapter(BaseDataAdapter):
    """Weather data adapter"""
    
    def __init__(self, api_key: str, session: aiohttp.ClientSession, redis_client: redis.Redis):
        super().__init__(session, redis_client)
        self.api_key = api_key
        self.source_type = "weather"
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_data(self, lat: float, lon: float, **kwargs) -> Dict[str, Any]:
        """Get weather data for location"""
        cache_key = f"weather:{lat}:{lon}"
        
        # Check cache first
        cached = await self._cache_get(cache_key)
        if cached:
            return cached
        
        # Fetch from API
        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                await self._cache_set(cache_key, data, ttl=1800)  # 30 minutes
                return data
            else:
                raise Exception(f"Weather API error: {response.status}")

class SatelliteDataAdapter(BaseDataAdapter):
    """Satellite data adapter"""
    
    def __init__(self, api_key: str, session: aiohttp.ClientSession, redis_client: redis.Redis):
        super().__init__(session, redis_client)
        self.api_key = api_key
        self.source_type = "satellite"
        self.base_url = "https://api.satellite.com"  # Example URL
    
    async def get_data(self, **kwargs) -> Dict[str, Any]:
        """Get satellite data"""
        # Implementation would depend on specific satellite API
        return {"status": "not_implemented"}

class NOAADataAdapter(BaseDataAdapter):
    """NOAA data adapter"""
    
    def __init__(self, session: aiohttp.ClientSession, redis_client: redis.Redis):
        super().__init__(session, redis_client)
        self.source_type = "noaa"
        self.base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    
    async def get_data(self, **kwargs) -> Dict[str, Any]:
        """Get NOAA data"""
        # Implementation for NOAA API
        return {"status": "not_implemented"}

class CopernicusDataAdapter(BaseDataAdapter):
    """Copernicus data adapter"""
    
    def __init__(self, session: aiohttp.ClientSession, redis_client: redis.Redis):
        super().__init__(session, redis_client)
        self.source_type = "copernicus"
        self.base_url = "https://scihub.copernicus.eu/dhus"
    
    async def get_data(self, **kwargs) -> Dict[str, Any]:
        """Get Copernicus data"""
        # Implementation for Copernicus API
        return {"status": "not_implemented"} 