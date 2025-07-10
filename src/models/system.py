"""
Core system SQLAlchemy models for AquaTrak
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, Float, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB, ARRAY, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel

class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    roles = Column(ARRAY(String), default=['user'])
    is_active = Column(Boolean, default=True)
    country_code = Column(String(2), index=True)
    language = Column(String(5), default='en')
    organization = Column(String(255))
    phone = Column(String(20))
    
    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    file_uploads = relationship("FileUpload", back_populates="user")
    reports = relationship("Report", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    user_organizations = relationship("UserOrganization", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Organization(BaseModel):
    """Organization model"""
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # government, private, academic, etc.
    country_code = Column(String(2), index=True)
    address = Column(Text)
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    subscription_plan = Column(String(50), default='basic')
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_organizations = relationship("UserOrganization", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(name='{self.name}', type='{self.type}')>"

class UserOrganization(BaseModel):
    """User-Organization relationship model"""
    __tablename__ = "user_organizations"
    
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(PostgresUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default='member')  # admin, member, viewer
    
    # Relationships
    user = relationship("User", back_populates="user_organizations")
    organization = relationship("Organization", back_populates="user_organizations")
    
    def __repr__(self):
        return f"<UserOrganization(user_id='{self.user_id}', organization_id='{self.organization_id}')>"

class AnalysisResult(BaseModel):
    """Analysis result model"""
    __tablename__ = "analysis_results"
    
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    module_name = Column(String(100), nullable=False, index=True)
    analysis_type = Column(String(100), nullable=False)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    status = Column(String(20), default='pending', index=True)
    completed_at = Column(DateTime(timezone=True))
    processing_time = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="analysis_results")
    
    def __repr__(self):
        return f"<AnalysisResult(module='{self.module_name}', status='{self.status}')>"

class Alert(BaseModel):
    """Alert model"""
    __tablename__ = "alerts"
    
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    module_name = Column(String(100), nullable=False)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    location = Column(Text)  # GeoJSON string
    metadata = Column(JSONB)
    is_read = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(type='{self.alert_type}', severity='{self.severity}')>"

class DataSource(BaseModel):
    """Data source model"""
    __tablename__ = "data_sources"
    
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    url = Column(String(500))
    api_key = Column(String(255))
    status = Column(String(20), default='active')
    last_updated = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<DataSource(name='{self.name}', type='{self.type}')>"

class FileUpload(BaseModel):
    """File upload model"""
    __tablename__ = "file_uploads"
    
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    upload_status = Column(String(20), default='uploading', index=True)
    
    # Relationships
    user = relationship("User", back_populates="file_uploads")
    
    def __repr__(self):
        return f"<FileUpload(filename='{self.filename}', status='{self.upload_status}')>"

class Report(BaseModel):
    """Report model"""
    __tablename__ = "reports"
    
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    report_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(JSONB)
    file_path = Column(String(500))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(title='{self.title}', type='{self.report_type}')>"

class AuditLog(BaseModel):
    """Audit log model"""
    __tablename__ = "audit_log"
    
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    resource_id = Column(PostgresUUID(as_uuid=True))
    details = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', user_id='{self.user_id}')>"

# Indexes
Index('idx_users_username', User.username)
Index('idx_users_email', User.email)
Index('idx_users_country_code', User.country_code)
Index('idx_organizations_country_code', Organization.country_code)
Index('idx_user_organizations_user_id', UserOrganization.user_id)
Index('idx_user_organizations_org_id', UserOrganization.organization_id)
Index('idx_analysis_results_user_module', AnalysisResult.user_id, AnalysisResult.module_name)
Index('idx_alerts_user_severity', Alert.user_id, Alert.severity)
Index('idx_file_uploads_user_status', FileUpload.user_id, FileUpload.upload_status)
Index('idx_audit_log_user_created', AuditLog.user_id, AuditLog.created_at) 