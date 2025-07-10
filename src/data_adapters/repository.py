"""
Repository pattern for database operations in AquaTrak
"""

from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date, timedelta
import uuid

from ..models.base import BaseModel
from ..models.system import User, Organization, AnalysisResult, Alert, DataSource, FileUpload, Report, AuditLog
from ..models.modules import *

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[T]):
        self.model = model
    
    def create(self, db: Session, **kwargs) -> T:
        """Create a new record"""
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, id: uuid.UUID) -> Optional[T]:
        """Get record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: uuid.UUID, **kwargs) -> Optional[T]:
        """Update record by ID"""
        db_obj = self.get_by_id(db, id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: uuid.UUID) -> bool:
        """Delete record by ID"""
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """Count total records"""
        return db.query(self.model).count()
    
    def exists(self, db: Session, id: uuid.UUID) -> bool:
        """Check if record exists"""
        return db.query(self.model).filter(self.model.id == id).first() is not None

class UserRepository(BaseRepository[User]):
    """User repository with specific user operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_country(self, db: Session, country_code: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by country"""
        return db.query(User).filter(User.country_code == country_code).offset(skip).limit(limit).all()
    
    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_users_by_role(self, db: Session, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        return db.query(User).filter(User.roles.contains([role])).offset(skip).limit(limit).all()

class OrganizationRepository(BaseRepository[Organization]):
    """Organization repository"""
    
    def __init__(self):
        super().__init__(Organization)
    
    def get_by_country(self, db: Session, country_code: str) -> List[Organization]:
        """Get organizations by country"""
        return db.query(Organization).filter(Organization.country_code == country_code).all()
    
    def get_active_organizations(self, db: Session) -> List[Organization]:
        """Get active organizations"""
        return db.query(Organization).filter(Organization.is_active == True).all()

class AnalysisResultRepository(BaseRepository[AnalysisResult]):
    """Analysis result repository"""
    
    def __init__(self):
        super().__init__(AnalysisResult)
    
    def get_by_user(self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """Get analysis results by user"""
        return db.query(AnalysisResult).filter(AnalysisResult.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_module(self, db: Session, module_name: str, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """Get analysis results by module"""
        return db.query(AnalysisResult).filter(AnalysisResult.module_name == module_name).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """Get analysis results by status"""
        return db.query(AnalysisResult).filter(AnalysisResult.status == status).offset(skip).limit(limit).all()
    
    def get_user_module_results(self, db: Session, user_id: uuid.UUID, module_name: str) -> List[AnalysisResult]:
        """Get user's analysis results for specific module"""
        return db.query(AnalysisResult).filter(
            and_(AnalysisResult.user_id == user_id, AnalysisResult.module_name == module_name)
        ).all()
    
    def get_recent_results(self, db: Session, days: int = 7) -> List[AnalysisResult]:
        """Get recent analysis results"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return db.query(AnalysisResult).filter(AnalysisResult.created_at >= cutoff_date).all()

class AlertRepository(BaseRepository[Alert]):
    """Alert repository"""
    
    def __init__(self):
        super().__init__(Alert)
    
    def get_by_user(self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Get alerts by user"""
        return db.query(Alert).filter(Alert.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_unread_alerts(self, db: Session, user_id: uuid.UUID) -> List[Alert]:
        """Get unread alerts for user"""
        return db.query(Alert).filter(
            and_(Alert.user_id == user_id, Alert.is_read == False)
        ).all()
    
    def get_by_severity(self, db: Session, severity: str, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Get alerts by severity"""
        return db.query(Alert).filter(Alert.severity == severity).offset(skip).limit(limit).all()
    
    def mark_as_read(self, db: Session, alert_id: uuid.UUID) -> bool:
        """Mark alert as read"""
        alert = self.get_by_id(db, alert_id)
        if alert:
            alert.is_read = True
            db.commit()
            return True
        return False

# Module-specific repositories
class InsarRepository(BaseRepository[InsarSubsidenceData]):
    """InSAR subsidence data repository"""
    
    def __init__(self):
        super().__init__(InsarSubsidenceData)
    
    def get_by_region(self, db: Session, region_id: str, skip: int = 0, limit: int = 100) -> List[InsarSubsidenceData]:
        """Get data by region"""
        return db.query(InsarSubsidenceData).filter(
            InsarSubsidenceData.region_id == region_id
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, db: Session, start_date: date, end_date: date) -> List[InsarSubsidenceData]:
        """Get data by date range"""
        return db.query(InsarSubsidenceData).filter(
            and_(
                InsarSubsidenceData.acquisition_date >= start_date,
                InsarSubsidenceData.acquisition_date <= end_date
            )
        ).all()

class FloodRepository(BaseRepository[FloodModelingData]):
    """Flood modeling data repository"""
    
    def __init__(self):
        super().__init__(FloodModelingData)
    
    def get_by_region(self, db: Session, region_id: str) -> List[FloodModelingData]:
        """Get data by region"""
        return db.query(FloodModelingData).filter(FloodModelingData.region_id == region_id).all()

class GroundwaterRepository(BaseRepository[GroundwaterData]):
    """Groundwater data repository"""
    
    def __init__(self):
        super().__init__(GroundwaterData)
    
    def get_by_well(self, db: Session, well_id: str, skip: int = 0, limit: int = 100) -> List[GroundwaterData]:
        """Get data by well"""
        return db.query(GroundwaterData).filter(
            GroundwaterData.well_id == well_id
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, db: Session, start_date: date, end_date: date) -> List[GroundwaterData]:
        """Get data by date range"""
        return db.query(GroundwaterData).filter(
            and_(
                GroundwaterData.sampling_date >= start_date,
                GroundwaterData.sampling_date <= end_date
            )
        ).all()

class IotRepository(BaseRepository[IotSensorData]):
    """IoT sensor data repository"""
    
    def __init__(self):
        super().__init__(IotSensorData)
    
    def get_by_sensor(self, db: Session, sensor_id: str, skip: int = 0, limit: int = 100) -> List[IotSensorData]:
        """Get data by sensor"""
        return db.query(IotSensorData).filter(
            IotSensorData.sensor_id == sensor_id
        ).offset(skip).limit(limit).all()
    
    def get_by_timestamp_range(self, db: Session, start_time: datetime, end_time: datetime) -> List[IotSensorData]:
        """Get data by timestamp range"""
        return db.query(IotSensorData).filter(
            and_(
                IotSensorData.timestamp >= start_time,
                IotSensorData.timestamp <= end_time
            )
        ).all()

class DroughtRepository(BaseRepository[DroughtData]):
    """Drought data repository"""
    
    def __init__(self):
        super().__init__(DroughtData)
    
    def get_by_region(self, db: Session, region_id: str) -> List[DroughtData]:
        """Get data by region"""
        return db.query(DroughtData).filter(DroughtData.region_id == region_id).all()

class WaterNetworkRepository(BaseRepository[WaterNetworkData]):
    """Water network data repository"""
    
    def __init__(self):
        super().__init__(WaterNetworkData)
    
    def get_by_node(self, db: Session, node_id: str, skip: int = 0, limit: int = 100) -> List[WaterNetworkData]:
        """Get data by node"""
        return db.query(WaterNetworkData).filter(
            WaterNetworkData.node_id == node_id
        ).offset(skip).limit(limit).all()

class DrinkingWaterRepository(BaseRepository[DrinkingWaterData]):
    """Drinking water data repository"""
    
    def __init__(self):
        super().__init__(DrinkingWaterData)
    
    def get_by_sample(self, db: Session, sample_id: str) -> Optional[DrinkingWaterData]:
        """Get data by sample ID"""
        return db.query(DrinkingWaterData).filter(DrinkingWaterData.sample_id == sample_id).first()

class TransboundaryRepository(BaseRepository[TransboundaryBasinData]):
    """Transboundary basin data repository"""
    
    def __init__(self):
        super().__init__(TransboundaryBasinData)
    
    def get_by_country(self, db: Session, country_code: str) -> List[TransboundaryBasinData]:
        """Get basins by country"""
        return db.query(TransboundaryBasinData).filter(
            TransboundaryBasinData.countries.contains([country_code])
        ).all()

class DustStormRepository(BaseRepository[DustStormData]):
    """Dust storm data repository"""
    
    def __init__(self):
        super().__init__(DustStormData)
    
    def get_by_region(self, db: Session, region_id: str) -> List[DustStormData]:
        """Get data by region"""
        return db.query(DustStormData).filter(DustStormData.region_id == region_id).all()

class DatacenterRepository(BaseRepository[DatacenterWaterData]):
    """Data center water data repository"""
    
    def __init__(self):
        super().__init__(DatacenterWaterData)
    
    def get_by_datacenter(self, db: Session, datacenter_id: str, skip: int = 0, limit: int = 100) -> List[DatacenterWaterData]:
        """Get data by datacenter"""
        return db.query(DatacenterWaterData).filter(
            DatacenterWaterData.datacenter_id == datacenter_id
        ).offset(skip).limit(limit).all()

class AgriculturalReservoirRepository(BaseRepository[AgriculturalReservoirData]):
    """Agricultural reservoir data repository"""
    
    def __init__(self):
        super().__init__(AgriculturalReservoirData)
    
    def get_by_reservoir(self, db: Session, reservoir_id: str, skip: int = 0, limit: int = 100) -> List[AgriculturalReservoirData]:
        """Get data by reservoir"""
        return db.query(AgriculturalReservoirData).filter(
            AgriculturalReservoirData.reservoir_id == reservoir_id
        ).offset(skip).limit(limit).all()

class UrbanGreenSpaceRepository(BaseRepository[UrbanGreenSpaceData]):
    """Urban green space data repository"""
    
    def __init__(self):
        super().__init__(UrbanGreenSpaceData)
    
    def get_by_area_range(self, db: Session, min_area: float, max_area: float) -> List[UrbanGreenSpaceData]:
        """Get data by area range"""
        return db.query(UrbanGreenSpaceData).filter(
            and_(
                UrbanGreenSpaceData.area_hectares >= min_area,
                UrbanGreenSpaceData.area_hectares <= max_area
            )
        ).all()

class EnvironmentalHealthRepository(BaseRepository[EnvironmentalHealthData]):
    """Environmental health data repository"""
    
    def __init__(self):
        super().__init__(EnvironmentalHealthData)
    
    def get_by_region(self, db: Session, region_id: str) -> List[EnvironmentalHealthData]:
        """Get data by region"""
        return db.query(EnvironmentalHealthData).filter(EnvironmentalHealthData.region_id == region_id).all()

# Repository factory
class RepositoryFactory:
    """Factory for creating repository instances"""
    
    @staticmethod
    def get_user_repository() -> UserRepository:
        return UserRepository()
    
    @staticmethod
    def get_organization_repository() -> OrganizationRepository:
        return OrganizationRepository()
    
    @staticmethod
    def get_analysis_result_repository() -> AnalysisResultRepository:
        return AnalysisResultRepository()
    
    @staticmethod
    def get_alert_repository() -> AlertRepository:
        return AlertRepository()
    
    @staticmethod
    def get_insar_repository() -> InsarRepository:
        return InsarRepository()
    
    @staticmethod
    def get_flood_repository() -> FloodRepository:
        return FloodRepository()
    
    @staticmethod
    def get_groundwater_repository() -> GroundwaterRepository:
        return GroundwaterRepository()
    
    @staticmethod
    def get_iot_repository() -> IotRepository:
        return IotRepository()
    
    @staticmethod
    def get_drought_repository() -> DroughtRepository:
        return DroughtRepository()
    
    @staticmethod
    def get_water_network_repository() -> WaterNetworkRepository:
        return WaterNetworkRepository()
    
    @staticmethod
    def get_drinking_water_repository() -> DrinkingWaterRepository:
        return DrinkingWaterRepository()
    
    @staticmethod
    def get_transboundary_repository() -> TransboundaryRepository:
        return TransboundaryRepository()
    
    @staticmethod
    def get_dust_storm_repository() -> DustStormRepository:
        return DustStormRepository()
    
    @staticmethod
    def get_datacenter_repository() -> DatacenterRepository:
        return DatacenterRepository()
    
    @staticmethod
    def get_agricultural_reservoir_repository() -> AgriculturalReservoirRepository:
        return AgriculturalReservoirRepository()
    
    @staticmethod
    def get_urban_green_space_repository() -> UrbanGreenSpaceRepository:
        return UrbanGreenSpaceRepository()
    
    @staticmethod
    def get_environmental_health_repository() -> EnvironmentalHealthRepository:
        return EnvironmentalHealthRepository() 