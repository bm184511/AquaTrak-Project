# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
AquaTrak Main Application Entry Point
AI-GIS Platform for Predictive Water Risk and Urban Resilience
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config.settings import get_settings
from config.database import init_db, check_db_connection, get_db_info
from security.auth import setup_security
from api.routes import setup_routes
from common_utils.logging import setup_logging
from data_adapters.manager import DataAdapterManager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting AquaTrak Application...")
    
    # Initialize database
    try:
        logger.info("📊 Initializing database...")
        if not check_db_connection():
            logger.error("❌ Database connection failed")
            raise Exception("Database connection failed")
        
        init_db()
        logger.info("✅ Database initialized successfully")
        
        # Get database info
        db_info = get_db_info()
        logger.info(f"📊 Database info: {db_info}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
    
    # Initialize data adapters
    try:
        app.state.data_adapters = DataAdapterManager()
        await app.state.data_adapters.initialize()
        logger.info("✅ Data adapters initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize data adapters: {e}")
        raise
    
    # Initialize security
    try:
        setup_security(app)
        logger.info("✅ Security setup completed")
    except Exception as e:
        logger.error(f"❌ Failed to setup security: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AquaTrak Application...")
    if hasattr(app.state, 'data_adapters'):
        await app.state.data_adapters.cleanup()

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="AquaTrak API",
        description="AI-GIS Platform for Predictive Water Risk and Urban Resilience",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint"""
        try:
            # Check database health
            db_healthy = check_db_connection()
            db_info = get_db_info() if db_healthy else None
            
            return {
                "status": "healthy" if db_healthy else "unhealthy",
                "service": "AquaTrak API",
                "version": "1.0.0",
                "database": {
                    "status": "connected" if db_healthy else "disconnected",
                    "info": db_info
                },
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "AquaTrak API",
                "version": "1.0.0",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    # Database info endpoint
    @app.get("/db/info")
    async def database_info() -> Dict[str, Any]:
        """Get database information"""
        try:
            return get_db_info()
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Setup routes
    setup_routes(app)
    
    # Serve static files in development
    if settings.DEBUG:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app

def main():
    """Main application entry point"""
    try:
        app = create_app()
        
        # Run the application
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if not settings.DEBUG else "debug",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 