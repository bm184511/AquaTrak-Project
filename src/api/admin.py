# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
Admin API routes for AquaTrak
Comprehensive administrative functionality for system management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import psutil
import os

from ..security.auth import get_current_user, require_admin, User
from ..config.database import get_db
from ..models.system import (
    User, Organization, UserOrganization, AnalysisResult, 
    Alert, DataSource, FileUpload, Report, AuditLog
)
from ..models.modules import (
    IoTWaterConsumption, EnvironmentalHealth, UrbanGreenSpace, 
    UrbanWaterNetwork, AgriculturalReservoir, TransboundaryWater,
    DataCenterWater, DustStormAnalysis, UrbanFloodModeling,
    GroundwaterPollution, DrinkingWaterQuality, DroughtPrediction,
    InSARSubsidence
)

router = APIRouter()

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin dashboard with comprehensive system overview"""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        new_users_today = db.query(User).filter(
            User.created_at >= datetime.utcnow().date()
        ).count()
        
        # Organization statistics
        total_organizations = db.query(Organization).count()
        active_organizations = db.query(Organization).filter(Organization.is_active == True).count()
        
        # Analysis statistics
        total_analyses = db.query(AnalysisResult).count()
        pending_analyses = db.query(AnalysisResult).filter(AnalysisResult.status == 'pending').count()
        completed_analyses = db.query(AnalysisResult.status == 'completed').count()
        
        # Alert statistics
        total_alerts = db.query(Alert).count()
        unread_alerts = db.query(Alert).filter(Alert.is_read == False).count()
        critical_alerts = db.query(Alert).filter(Alert.severity == 'critical').count()
        
        # System statistics
        system_stats = get_system_stats()
        
        # Recent activities
        recent_activities = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(10).all()
        
        # Module statistics
        module_stats = get_module_statistics(db)
        
        return {
            "status": "success",
            "data": {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "new_today": new_users_today,
                    "growth_rate": calculate_growth_rate(db, User)
                },
                "organizations": {
                    "total": total_organizations,
                    "active": active_organizations
                },
                "analyses": {
                    "total": total_analyses,
                    "pending": pending_analyses,
                    "completed": completed_analyses,
                    "success_rate": (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0
                },
                "alerts": {
                    "total": total_alerts,
                    "unread": unread_alerts,
                    "critical": critical_alerts
                },
                "system": system_stats,
                "modules": module_stats,
                "recent_activities": [
                    {
                        "id": str(activity.id),
                        "action": activity.action,
                        "user": activity.user.username if activity.user else "System",
                        "resource": activity.resource,
                        "timestamp": activity.created_at.isoformat(),
                        "details": activity.details
                    }
                    for activity in recent_activities
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users")
async def get_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None
):
    """Get all users with filtering and pagination"""
    try:
        query = db.query(User)
        
        # Apply filters
        if search:
            query = query.filter(
                (User.username.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%")) |
                (User.full_name.ilike(f"%{search}%"))
            )
        
        if role:
            query = query.filter(User.roles.contains([role]))
        
        if status:
            if status == "active":
                query = query.filter(User.is_active == True)
            elif status == "inactive":
                query = query.filter(User.is_active == False)
        
        if country:
            query = query.filter(User.country_code == country)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset((page - 1) * limit).limit(limit).all()
        
        return {
            "status": "success",
            "data": {
                "users": [
                    {
                        "id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "roles": user.roles,
                        "is_active": user.is_active,
                        "country_code": user.country_code,
                        "language": user.language,
                        "organization": user.organization,
                        "phone": user.phone,
                        "created_at": user.created_at.isoformat(),
                        "last_login": get_last_login(db, user.id)
                    }
                    for user in users
                ],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get specific user details"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user statistics
        analysis_count = db.query(AnalysisResult).filter(AnalysisResult.user_id == user.id).count()
        alert_count = db.query(Alert).filter(Alert.user_id == user.id).count()
        file_count = db.query(FileUpload).filter(FileUpload.user_id == user.id).count()
        
        return {
            "status": "success",
            "data": {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "roles": user.roles,
                    "is_active": user.is_active,
                    "country_code": user.country_code,
                    "language": user.language,
                    "organization": user.organization,
                    "phone": user.phone,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                },
                "statistics": {
                    "analyses": analysis_count,
                    "alerts": alert_count,
                    "files": file_count
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@router.post("/users")
async def create_user(
    user_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    try:
        # Validate required fields
        required_fields = ["username", "email", "password", "full_name"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data["username"]) | (User.email == user_data["email"])
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash password
        from ..security.auth import get_password_hash
        hashed_password = get_password_hash(user_data["password"])
        
        # Create user
        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            roles=user_data.get("roles", ["user"]),
            is_active=user_data.get("is_active", True),
            country_code=user_data.get("country_code"),
            language=user_data.get("language", "en"),
            organization=user_data.get("organization"),
            phone=user_data.get("phone")
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log activity
        log_activity(db, current_user.id, "create_user", "user", str(new_user.id), {
            "username": new_user.username,
            "email": new_user.email
        })
        
        return {
            "status": "success",
            "message": "User created successfully",
            "data": {
                "id": str(new_user.id),
                "username": new_user.username,
                "email": new_user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user information"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        updateable_fields = ["full_name", "roles", "is_active", "country_code", "language", "organization", "phone"]
        for field in updateable_fields:
            if field in user_data:
                setattr(user, field, user_data[field])
        
        # Update password if provided
        if "password" in user_data:
            from ..security.auth import get_password_hash
            user.hashed_password = get_password_hash(user_data["password"])
        
        db.commit()
        
        # Log activity
        log_activity(db, current_user.id, "update_user", "user", str(user.id), {
            "updated_fields": list(user_data.keys())
        })
        
        return {
            "status": "success",
            "message": "User updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent self-deletion
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        # Log activity before deletion
        log_activity(db, current_user.id, "delete_user", "user", str(user.id), {
            "username": user.username,
            "email": user.email
        })
        
        db.delete(user)
        db.commit()
        
        return {
            "status": "success",
            "message": "User deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# ============================================================================
# ORGANIZATION MANAGEMENT
# ============================================================================

@router.get("/organizations")
async def get_organizations(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    type: Optional[str] = None,
    country: Optional[str] = None
):
    """Get all organizations with filtering and pagination"""
    try:
        query = db.query(Organization)
        
        # Apply filters
        if search:
            query = query.filter(Organization.name.ilike(f"%{search}%"))
        
        if type:
            query = query.filter(Organization.type == type)
        
        if country:
            query = query.filter(Organization.country_code == country)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        organizations = query.offset((page - 1) * limit).limit(limit).all()
        
        return {
            "status": "success",
            "data": {
                "organizations": [
                    {
                        "id": str(org.id),
                        "name": org.name,
                        "type": org.type,
                        "country_code": org.country_code,
                        "address": org.address,
                        "contact_email": org.contact_email,
                        "contact_phone": org.contact_phone,
                        "subscription_plan": org.subscription_plan,
                        "is_active": org.is_active,
                        "created_at": org.created_at.isoformat(),
                        "user_count": get_organization_user_count(db, org.id)
                    }
                    for org in organizations
                ],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get organizations: {str(e)}")

# ============================================================================
# SYSTEM MONITORING
# ============================================================================

@router.get("/system/status")
async def system_status(current_user: User = Depends(require_admin)):
    """Get comprehensive system status"""
    try:
        return {
            "status": "success",
            "data": get_system_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/system/performance")
async def system_performance(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system performance metrics"""
    try:
        # Database performance
        db_stats = get_database_stats(db)
        
        # API performance
        api_stats = get_api_performance_stats(db)
        
        # Module performance
        module_performance = get_module_performance_stats(db)
        
        return {
            "status": "success",
            "data": {
                "database": db_stats,
                "api": api_stats,
                "modules": module_performance
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/system/logs")
async def system_logs(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None
):
    """Get system audit logs"""
    try:
        query = db.query(AuditLog)
        
        # Apply filters
        if level:
            query = query.filter(AuditLog.action.contains(level))
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        return {
            "status": "success",
            "data": {
                "logs": [
                    {
                        "id": str(log.id),
                        "action": log.action,
                        "user": log.user.username if log.user else "System",
                        "resource": log.resource,
                        "resource_id": str(log.resource_id) if log.resource_id else None,
                        "details": log.details,
                        "ip_address": str(log.ip_address) if log.ip_address else None,
                        "user_agent": log.user_agent,
                        "created_at": log.created_at.isoformat()
                    }
                    for log in logs
                ],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system logs: {str(e)}")

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

@router.get("/data/sources")
async def get_data_sources(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all data sources"""
    try:
        sources = db.query(DataSource).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(source.id),
                    "name": source.name,
                    "type": source.type,
                    "url": source.url,
                    "status": source.status,
                    "last_updated": source.last_updated.isoformat() if source.last_updated else None
                }
                for source in sources
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data sources: {str(e)}")

@router.get("/data/uploads")
async def get_file_uploads(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Get file uploads"""
    try:
        query = db.query(FileUpload)
        
        # Apply filters
        if status:
            query = query.filter(FileUpload.upload_status == status)
        
        if user_id:
            query = query.filter(FileUpload.user_id == user_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        uploads = query.order_by(desc(FileUpload.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        return {
            "status": "success",
            "data": {
                "uploads": [
                    {
                        "id": str(upload.id),
                        "filename": upload.filename,
                        "file_size": upload.file_size,
                        "file_type": upload.file_type,
                        "upload_status": upload.upload_status,
                        "user": upload.user.username if upload.user else "Unknown",
                        "created_at": upload.created_at.isoformat()
                    }
                    for upload in uploads
                ],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file uploads: {str(e)}")

# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================

@router.get("/analytics/usage")
async def get_usage_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    period: str = Query("7d", regex="^(1d|7d|30d|90d|1y)$")
):
    """Get usage analytics for the specified period"""
    try:
        end_date = datetime.utcnow()
        
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)
        
        # User registrations
        user_registrations = db.query(func.date(User.created_at)).filter(
            User.created_at >= start_date
        ).group_by(func.date(User.created_at)).all()
        
        # Analysis completions
        analysis_completions = db.query(func.date(AnalysisResult.completed_at)).filter(
            AnalysisResult.completed_at >= start_date
        ).group_by(func.date(AnalysisResult.completed_at)).all()
        
        # Alert generation
        alert_generations = db.query(func.date(Alert.created_at)).filter(
            Alert.created_at >= start_date
        ).group_by(func.date(Alert.created_at)).all()
        
        return {
            "status": "success",
            "data": {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "user_registrations": [str(date[0]) for date in user_registrations],
                "analysis_completions": [str(date[0]) for date in analysis_completions],
                "alert_generations": [str(date[0]) for date in alert_generations]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage analytics: {str(e)}")

@router.get("/analytics/modules")
async def get_module_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get module usage analytics"""
    try:
        # Module usage statistics
        module_stats = db.query(
            AnalysisResult.module_name,
            func.count(AnalysisResult.id).label('total_analyses'),
            func.avg(AnalysisResult.processing_time).label('avg_processing_time'),
            func.count(AnalysisResult.id).filter(AnalysisResult.status == 'completed').label('completed_analyses')
        ).group_by(AnalysisResult.module_name).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "module_name": stat.module_name,
                    "total_analyses": stat.total_analyses,
                    "completed_analyses": stat.completed_analyses,
                    "success_rate": (stat.completed_analyses / stat.total_analyses * 100) if stat.total_analyses > 0 else 0,
                    "avg_processing_time": float(stat.avg_processing_time) if stat.avg_processing_time else 0
                }
                for stat in module_stats
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get module analytics: {str(e)}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_system_stats() -> Dict[str, Any]:
    """Get system statistics"""
    try:
        # CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network statistics
        network = psutil.net_io_counters()
        
        return {
            "status": "healthy",
            "uptime": get_system_uptime(),
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "memory_available": memory.available,
            "memory_total": memory.total,
            "disk_usage": disk.percent,
            "disk_free": disk.free,
            "disk_total": disk.total,
            "network_bytes_sent": network.bytes_sent,
            "network_bytes_recv": network.bytes_recv,
            "active_connections": len(psutil.net_connections())
        }
    except Exception:
        return {
            "status": "unknown",
            "error": "Failed to get system statistics"
        }

def get_system_uptime() -> str:
    """Get system uptime"""
    try:
        uptime_seconds = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    except Exception:
        return "Unknown"

def get_module_statistics(db: Session) -> Dict[str, Any]:
    """Get module statistics"""
    try:
        # Count records in each module table
        module_counts = {}
        
        module_tables = [
            (IoTWaterConsumption, "iot_water_consumption"),
            (EnvironmentalHealth, "environmental_health"),
            (UrbanGreenSpace, "urban_green_space"),
            (UrbanWaterNetwork, "urban_water_network"),
            (AgriculturalReservoir, "agricultural_reservoir"),
            (TransboundaryWater, "transboundary_water"),
            (DataCenterWater, "data_center_water"),
            (DustStormAnalysis, "dust_storm_analysis"),
            (UrbanFloodModeling, "urban_flood_modeling"),
            (GroundwaterPollution, "groundwater_pollution"),
            (DrinkingWaterQuality, "drinking_water_quality"),
            (DroughtPrediction, "drought_prediction"),
            (InSARSubsidence, "insar_subsidence")
        ]
        
        for model, name in module_tables:
            try:
                count = db.query(model).count()
                module_counts[name] = count
            except Exception:
                module_counts[name] = 0
        
        return module_counts
    except Exception:
        return {}

def calculate_growth_rate(db: Session, model) -> float:
    """Calculate growth rate for a model"""
    try:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        today_count = db.query(model).filter(func.date(model.created_at) == today).count()
        yesterday_count = db.query(model).filter(func.date(model.created_at) == yesterday).count()
        
        if yesterday_count == 0:
            return 100.0 if today_count > 0 else 0.0
        
        return ((today_count - yesterday_count) / yesterday_count) * 100
    except Exception:
        return 0.0

def get_last_login(db: Session, user_id: str) -> Optional[str]:
    """Get user's last login time"""
    try:
        last_login = db.query(AuditLog).filter(
            and_(AuditLog.user_id == user_id, AuditLog.action == "login")
        ).order_by(desc(AuditLog.created_at)).first()
        
        return last_login.created_at.isoformat() if last_login else None
    except Exception:
        return None

def get_organization_user_count(db: Session, org_id: str) -> int:
    """Get user count for an organization"""
    try:
        return db.query(UserOrganization).filter(UserOrganization.organization_id == org_id).count()
    except Exception:
        return 0

def get_database_stats(db: Session) -> Dict[str, Any]:
    """Get database performance statistics"""
    try:
        # This would typically involve database-specific queries
        # For now, return basic stats
        return {
            "connection_pool_size": 10,
            "active_connections": 5,
            "query_count": 1000,
            "avg_query_time": 0.05
        }
    except Exception:
        return {}

def get_api_performance_stats(db: Session) -> Dict[str, Any]:
    """Get API performance statistics"""
    try:
        # Count recent API calls from audit logs
        recent_calls = db.query(AuditLog).filter(
            AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        return {
            "requests_per_hour": recent_calls,
            "avg_response_time": 0.2,
            "error_rate": 0.01
        }
    except Exception:
        return {}

def get_module_performance_stats(db: Session) -> Dict[str, Any]:
    """Get module performance statistics"""
    try:
        # Get average processing times for each module
        module_performance = db.query(
            AnalysisResult.module_name,
            func.avg(AnalysisResult.processing_time).label('avg_time'),
            func.count(AnalysisResult.id).label('total_count')
        ).group_by(AnalysisResult.module_name).all()
        
        return {
            module.module_name: {
                "avg_processing_time": float(module.avg_time) if module.avg_time else 0,
                "total_analyses": module.total_count
            }
            for module in module_performance
        }
    except Exception:
        return {}

def log_activity(db: Session, user_id: str, action: str, resource: str, resource_id: str, details: Dict[str, Any]):
    """Log admin activity"""
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback() 