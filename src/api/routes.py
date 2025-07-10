"""
API Routes Configuration
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from fastapi import FastAPI
from . import auth, admin, data, reports, monitoring

# Import module routers
from ..modules.insar_subsidence.api import router as insar_router
from ..modules.urban_flood_modeling.api import router as flood_router
from ..modules.groundwater_pollution.api import router as pollution_router
from ..modules.iot_water_consumption.api import router as iot_router
from ..modules.drought_prediction.api import router as drought_router
from ..modules.urban_water_network.api import router as network_router
from ..modules.drinking_water_quality.api import router as quality_router
from ..modules.transboundary_water.api import router as transboundary_router
from ..modules.dust_storm_analysis.api import router as dust_storm_router
from ..modules.data_center_water.api import router as data_center_router
from ..modules.agricultural_reservoir.api import router as agricultural_router
from ..modules.urban_green_space.api import router as green_space_router
from ..modules.environmental_health.api import router as health_risk_router

def setup_routes(app: FastAPI):
    """Setup all API routes"""
    
    # Include module routers
    app.include_router(insar_router, prefix="/api/v1")
    app.include_router(flood_router, prefix="/api/v1")
    app.include_router(pollution_router, prefix="/api/v1")
    app.include_router(iot_router, prefix="/api/v1")
    app.include_router(drought_router, prefix="/api/v1")
    app.include_router(network_router, prefix="/api/v1")
    app.include_router(quality_router, prefix="/api/v1")
    app.include_router(transboundary_router, prefix="/api/v1")
    app.include_router(dust_storm_router, prefix="/api/v1")
    app.include_router(data_center_router, prefix="/api/v1")
    app.include_router(agricultural_router, prefix="/api/v1")
    app.include_router(green_space_router, prefix="/api/v1")
    app.include_router(health_risk_router, prefix="/api/v1")

    # Include utility routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administration"])
    app.include_router(data.router, prefix="/api/v1/data", tags=["Data Management"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
    app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["System Monitoring"])

    # Add additional API endpoints
    setup_additional_routes(app)

def setup_additional_routes(app: FastAPI):
    """Setup additional API routes for modules, analysis, alerts, etc."""
    
    from fastapi import APIRouter, Depends, HTTPException
    from sqlalchemy.orm import Session
    from config.database import get_db
    from models.system import User, Module, AnalysisResult, Alert, Dashboard, Organization
    from api.auth import get_current_user
    from typing import List, Optional
    from datetime import datetime
    
    # Create routers for additional endpoints
    modules_router = APIRouter(prefix="/modules", tags=["Modules"])
    analysis_router = APIRouter(prefix="/analysis", tags=["Analysis"])
    alerts_router = APIRouter(prefix="/alerts", tags=["Alerts"])
    dashboards_router = APIRouter(prefix="/dashboards", tags=["Dashboards"])
    organizations_router = APIRouter(prefix="/organizations", tags=["Organizations"])
    
    # Modules endpoints
    @modules_router.get("/")
    async def get_modules(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get all modules"""
        modules = db.query(Module).all()
        return {
            "status": "success",
            "data": [
                {
                    "id": str(m.id),
                    "name": m.name,
                    "description": m.description,
                    "category": m.category,
                    "status": m.status,
                    "version": m.version,
                    "last_updated": m.last_updated.isoformat(),
                    "config": m.config
                }
                for m in modules
            ]
        }
    
    @modules_router.get("/{module_id}")
    async def get_module(
        module_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get module by ID"""
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        return {
            "status": "success",
            "data": {
                "id": str(module.id),
                "name": module.name,
                "description": module.description,
                "category": module.category,
                "status": module.status,
                "version": module.version,
                "last_updated": module.last_updated.isoformat(),
                "config": module.config
            }
        }
    
    @modules_router.get("/{module_id}/status")
    async def get_module_status(
        module_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get module status"""
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        return {
            "status": "success",
            "data": {
                "status": module.status,
                "last_update": module.last_updated.isoformat()
            }
        }
    
    # Analysis endpoints
    @analysis_router.get("/")
    async def get_analysis_results(
        module_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get analysis results"""
        query = db.query(AnalysisResult)
        
        if module_id:
            query = query.filter(AnalysisResult.module_id == module_id)
        if status:
            query = query.filter(AnalysisResult.status == status)
        
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(r.id),
                    "module_id": str(r.module_id),
                    "module_name": r.module_name,
                    "analysis_type": r.analysis_type,
                    "status": r.status,
                    "parameters": r.parameters,
                    "results": r.results,
                    "metadata": r.metadata,
                    "created_at": r.created_at.isoformat(),
                    "updated_at": r.updated_at.isoformat(),
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None
                }
                for r in results
            ],
            "pagination": {
                "page": offset // limit + 1,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        }
    
    @analysis_router.get("/{analysis_id}")
    async def get_analysis_result(
        analysis_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get analysis result by ID"""
        result = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Analysis result not found")
        
        return {
            "status": "success",
            "data": {
                "id": str(result.id),
                "module_id": str(result.module_id),
                "module_name": result.module_name,
                "analysis_type": result.analysis_type,
                "status": result.status,
                "parameters": result.parameters,
                "results": result.results,
                "metadata": result.metadata,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat(),
                "completed_at": result.completed_at.isoformat() if result.completed_at else None
            }
        }
    
    # Alerts endpoints
    @alerts_router.get("/")
    async def get_alerts(
        severity: Optional[str] = None,
        status: Optional[str] = None,
        module_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get alerts"""
        query = db.query(Alert)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        if status:
            query = query.filter(Alert.status == status)
        if module_id:
            query = query.filter(Alert.module_id == module_id)
        
        total = query.count()
        alerts = query.offset(offset).limit(limit).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(a.id),
                    "type": a.type,
                    "severity": a.severity,
                    "title": a.title,
                    "message": a.message,
                    "module_id": str(a.module_id) if a.module_id else None,
                    "analysis_id": str(a.analysis_id) if a.analysis_id else None,
                    "location": a.location,
                    "metadata": a.metadata,
                    "created_at": a.created_at.isoformat(),
                    "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
                    "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                    "status": a.status
                }
                for a in alerts
            ],
            "pagination": {
                "page": offset // limit + 1,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        }
    
    @alerts_router.get("/{alert_id}")
    async def get_alert(
        alert_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get alert by ID"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "status": "success",
            "data": {
                "id": str(alert.id),
                "type": alert.type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "module_id": str(alert.module_id) if alert.module_id else None,
                "analysis_id": str(alert.analysis_id) if alert.analysis_id else None,
                "location": alert.location,
                "metadata": alert.metadata,
                "created_at": alert.created_at.isoformat(),
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "status": alert.status
            }
        }
    
    @alerts_router.post("/{alert_id}/acknowledge")
    async def acknowledge_alert(
        alert_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Acknowledge an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "id": str(alert.id),
                "status": alert.status,
                "acknowledged_at": alert.acknowledged_at.isoformat()
            }
        }
    
    @alerts_router.post("/{alert_id}/resolve")
    async def resolve_alert(
        alert_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Resolve an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "id": str(alert.id),
                "status": alert.status,
                "resolved_at": alert.resolved_at.isoformat()
            }
        }
    
    @alerts_router.post("/{alert_id}/dismiss")
    async def dismiss_alert(
        alert_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Dismiss an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.status = "dismissed"
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "id": str(alert.id),
                "status": alert.status
            }
        }
    
    # Dashboards endpoints
    @dashboards_router.get("/")
    async def get_dashboards(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get user dashboards"""
        dashboards = db.query(Dashboard).filter(
            (Dashboard.user_id == current_user.id) | (Dashboard.is_public == True)
        ).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(d.id),
                    "name": d.name,
                    "description": d.description,
                    "user_id": str(d.user_id),
                    "is_public": d.is_public,
                    "widgets": d.widgets,
                    "layout": d.layout,
                    "created_at": d.created_at.isoformat(),
                    "updated_at": d.updated_at.isoformat()
                }
                for d in dashboards
            ]
        }
    
    # Organizations endpoints
    @organizations_router.get("/current")
    async def get_current_organization(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        """Get current user's organization"""
        if not current_user.organization_id:
            raise HTTPException(status_code=404, detail="User not associated with any organization")
        
        org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return {
            "status": "success",
            "data": {
                "id": str(org.id),
                "name": org.name,
                "description": org.description,
                "country": org.country,
                "industry": org.industry,
                "size": org.size,
                "subscription_plan": org.subscription_plan,
                "settings": org.settings,
                "created_at": org.created_at.isoformat(),
                "updated_at": org.updated_at.isoformat()
            }
        }
    
    # Include all routers
    app.include_router(modules_router, prefix="/api/v1")
    app.include_router(analysis_router, prefix="/api/v1")
    app.include_router(alerts_router, prefix="/api/v1")
    app.include_router(dashboards_router, prefix="/api/v1")
    app.include_router(organizations_router, prefix="/api/v1") 