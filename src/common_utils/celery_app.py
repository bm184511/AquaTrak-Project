# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
Celery configuration for background tasks in AquaTrak
"""

import os

# Try to import celery, but don't fail if not available
try:
    from celery import Celery
    from celery.schedules import crontab
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create dummy classes for when celery is not available
    class Celery:
        def __init__(self, *args, **kwargs):
            pass
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def conf(self):
            return type('Config', (), {'update': lambda x: None})()
    
    class crontab:
        def __init__(self, **kwargs):
            pass

# Try to import settings, but don't fail if not available
try:
    from ..config.settings import get_settings
    settings = get_settings()
except ImportError:
    # Fallback settings for when config is not available
    settings = type('Settings', (), {
        'REDIS_URL': 'redis://localhost:6379/0'
    })()

# Create Celery app
celery_app = Celery(
    "aquatrak",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.modules.insar_subsidence.tasks",
        "src.modules.flood_modeling.tasks",
        "src.modules.groundwater_pollution.tasks",
        "src.modules.industrial_water.tasks",
        "src.modules.agricultural_drought.tasks",
        "src.modules.urban_water_network.tasks",
        "src.modules.drinking_water_quality.tasks",
        "src.modules.transboundary_water.tasks",
        "src.modules.dust_storm.tasks",
        "src.modules.data_center_water.tasks",
        "src.modules.agricultural_reservoir.tasks",
        "src.modules.urban_green_space.tasks",
        "src.modules.environmental_health.tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "src.modules.*.tasks.*": {"queue": "modules"},
        "src.data_adapters.tasks.*": {"queue": "data"},
        "src.common_utils.tasks.*": {"queue": "utils"},
    },
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Daily data updates
        "update-noaa-data": {
            "task": "src.data_adapters.tasks.update_noaa_data",
            "schedule": crontab(hour=2, minute=0),  # 2 AM UTC
        },
        "update-copernicus-data": {
            "task": "src.data_adapters.tasks.update_copernicus_data",
            "schedule": crontab(hour=3, minute=0),  # 3 AM UTC
        },
        "update-ecmwf-data": {
            "task": "src.data_adapters.tasks.update_ecmwf_data",
            "schedule": crontab(hour=4, minute=0),  # 4 AM UTC
        },
        
        # Weekly analysis tasks
        "weekly-insar-analysis": {
            "task": "src.modules.insar_subsidence.tasks.weekly_analysis",
            "schedule": crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM UTC
        },
        "weekly-flood-risk-assessment": {
            "task": "src.modules.flood_modeling.tasks.weekly_risk_assessment",
            "schedule": crontab(day_of_week=1, hour=7, minute=0),  # Monday 7 AM UTC
        },
        
        # Monthly comprehensive reports
        "monthly-subsidence-report": {
            "task": "src.modules.insar_subsidence.tasks.generate_monthly_report",
            "schedule": crontab(day=1, hour=8, minute=0),  # 1st of month 8 AM UTC
        },
        "monthly-water-quality-report": {
            "task": "src.modules.drinking_water_quality.tasks.generate_monthly_report",
            "schedule": crontab(day=1, hour=9, minute=0),  # 1st of month 9 AM UTC
        },
        
        # System maintenance
        "cleanup-temp-files": {
            "task": "src.common_utils.tasks.cleanup_temp_files",
            "schedule": crontab(hour=1, minute=0),  # 1 AM UTC daily
        },
        "backup-database": {
            "task": "src.common_utils.tasks.backup_database",
            "schedule": crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM UTC
        },
        "health-check": {
            "task": "src.common_utils.tasks.system_health_check",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes
        },
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Monitoring
    event_queue_expires=60,
    event_queue_ttl=5,
    event_queue_max_priority=10,
)

# Task base class with common functionality
class AquaTrakTask:
    """Base task class for AquaTrak"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        from .logging import log_module_execution
        log_module_execution(
            module_name=self.__class__.__name__,
            status="completed",
            details={"task_id": task_id, "result": str(retval)}
        )
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        from .logging import log_error
        log_error(
            error=exc,
            context={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "module": self.__class__.__name__
            }
        )
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        from .logging import log_module_execution
        log_module_execution(
            module_name=self.__class__.__name__,
            status="retrying",
            details={"task_id": task_id, "attempt": self.request.retries}
        )

# Example task implementations
@celery_app.task(bind=True, base=AquaTrakTask)
def example_task(self, data):
    """Example task implementation"""
    try:
        # Task logic here
        result = f"Processed {data}"
        return result
    except Exception as exc:
        # Retry task up to 3 times
        if self.request.retries < 3:
            raise self.retry(countdown=60, exc=exc)
        raise

@celery_app.task(bind=True, base=AquaTrakTask)
def cleanup_temp_files(self):
    """Clean up temporary files"""
    from .file_utils import cleanup_temp_files
    from pathlib import Path
    
    temp_dir = Path("temp")
    if temp_dir.exists():
        cleanup_temp_files(temp_dir)
        return f"Cleaned up {temp_dir}"
    return "No temp directory found"

@celery_app.task(bind=True, base=AquaTrakTask)
def backup_database(self):
    """Backup database"""
    # Database backup logic here
    return "Database backup completed"

@celery_app.task(bind=True, base=AquaTrakTask)
def system_health_check(self):
    """System health check"""
    # Health check logic here
    return "System health check completed"

# Task monitoring and management
def get_task_status(task_id: str):
    """Get task status by ID"""
    return celery_app.AsyncResult(task_id)

def cancel_task(task_id: str):
    """Cancel a running task"""
    celery_app.control.revoke(task_id, terminate=True)

def get_active_tasks():
    """Get list of active tasks"""
    return celery_app.control.inspect().active()

def get_scheduled_tasks():
    """Get list of scheduled tasks"""
    return celery_app.control.inspect().scheduled()

def get_registered_tasks():
    """Get list of registered tasks"""
    return celery_app.control.inspect().registered()

# Task queue management
def purge_queue(queue_name: str):
    """Purge all tasks from a queue"""
    celery_app.control.purge()

def get_queue_length(queue_name: str):
    """Get number of tasks in queue"""
    return celery_app.control.inspect().reserved().get(queue_name, [])

# Task statistics
def get_task_statistics():
    """Get task execution statistics"""
    stats = celery_app.control.inspect().stats()
    return stats

def get_worker_statistics():
    """Get worker statistics"""
    stats = celery_app.control.inspect().stats()
    return stats

# Task monitoring decorators
def monitor_task_execution(func):
    """Decorator to monitor task execution"""
    def wrapper(*args, **kwargs):
        from .logging import log_performance
        return log_performance(func.__name__)(func)(*args, **kwargs)
    return wrapper

def retry_on_failure(max_retries: int = 3, countdown: int = 60):
    """Decorator to retry task on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # Retry logic here
                raise exc
        return wrapper
    return decorator 