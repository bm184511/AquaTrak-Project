"""
Base SQLAlchemy models for AquaTrak
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, Float, Integer, JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB, ARRAY
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class TimestampMixin:
    """Mixin for timestamp fields"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    """Mixin for UUID primary key"""
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model with common fields"""
    __abstract__ = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert model to JSON-serializable dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from dictionary"""
        return cls(**data) 