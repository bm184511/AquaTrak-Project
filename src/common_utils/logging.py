# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
Logging configuration for AquaTrak
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ..config.settings import get_settings

settings = get_settings()

def setup_logging(
    log_level: str = None,
    log_file: str = None,
    log_format: str = None
) -> None:
    """
    Setup logging configuration for AquaTrak
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_format: Log message format
    """
    
    # Use settings if not provided
    log_level = log_level or settings.LOG_LEVEL
    log_file = log_file or settings.LOG_FILE
    log_format = log_format or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """Get logger with specified name"""
    return logging.getLogger(name)

def log_function_call(func_name: str, args: dict = None, kwargs: dict = None):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed with error: {str(e)}")
                raise
        return wrapper
    return decorator

def log_performance(func_name: str):
    """Decorator to log function performance"""
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                logger.info(f"{func_name} executed in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.error(f"{func_name} failed after {execution_time:.4f} seconds: {str(e)}")
                raise
        return wrapper
    return decorator

def log_security_event(event_type: str, user_id: str = None, details: dict = None):
    """Log security-related events"""
    logger = logging.getLogger("security")
    event = {
        "type": event_type,
        "user_id": user_id,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)),
        "details": details or {}
    }
    logger.warning(f"Security event: {event}")

def log_data_access(
    user_id: str,
    data_type: str,
    action: str,
    resource_id: str = None,
    success: bool = True
):
    """Log data access events"""
    logger = logging.getLogger("data_access")
    event = {
        "user_id": user_id,
        "data_type": data_type,
        "action": action,
        "resource_id": resource_id,
        "success": success,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"Data access: {event}")

def log_api_request(
    method: str,
    path: str,
    user_id: str = None,
    status_code: int = None,
    response_time: float = None
):
    """Log API request details"""
    logger = logging.getLogger("api")
    event = {
        "method": method,
        "path": path,
        "user_id": user_id,
        "status_code": status_code,
        "response_time": response_time,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    logger.info(f"API request: {event}")

def log_error(error: Exception, context: dict = None):
    """Log error with context"""
    logger = logging.getLogger("errors")
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    logger.error(f"Error occurred: {error_info}", exc_info=True)

def log_module_execution(module_name: str, status: str, details: dict = None):
    """Log module execution status"""
    logger = logging.getLogger("modules")
    event = {
        "module": module_name,
        "status": status,
        "details": details or {},
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    logger.info(f"Module execution: {event}")

def log_external_api_call(
    api_name: str,
    endpoint: str,
    method: str,
    status_code: int = None,
    response_time: float = None,
    success: bool = True
):
    """Log external API calls"""
    logger = logging.getLogger("external_api")
    event = {
        "api_name": api_name,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "response_time": response_time,
        "success": success,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"External API call: {event}")

def log_database_operation(
    operation: str,
    table: str,
    user_id: str = None,
    success: bool = True,
    execution_time: float = None
):
    """Log database operations"""
    logger = logging.getLogger("database")
    event = {
        "operation": operation,
        "table": table,
        "user_id": user_id,
        "success": success,
        "execution_time": execution_time,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"Database operation: {event}")

def log_file_operation(
    operation: str,
    file_path: str,
    user_id: str = None,
    success: bool = True,
    file_size: int = None
):
    """Log file operations"""
    logger = logging.getLogger("files")
    event = {
        "operation": operation,
        "file_path": file_path,
        "user_id": user_id,
        "success": success,
        "file_size": file_size,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"File operation: {event}")

def log_user_activity(
    user_id: str,
    activity: str,
    details: dict = None,
    ip_address: str = None
):
    """Log user activities"""
    logger = logging.getLogger("user_activity")
    event = {
        "user_id": user_id,
        "activity": activity,
        "details": details or {},
        "ip_address": ip_address,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    logger.info(f"User activity: {event}")

def log_system_health(
    component: str,
    status: str,
    metrics: dict = None
):
    """Log system health information"""
    logger = logging.getLogger("system_health")
    event = {
        "component": component,
        "status": status,
        "metrics": metrics or {},
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    logger.info(f"System health: {event}")

def log_audit_trail(
    user_id: str,
    action: str,
    resource: str,
    resource_id: str = None,
    changes: dict = None
):
    """Log audit trail events"""
    logger = logging.getLogger("audit")
    event = {
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "changes": changes or {},
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
    }
    logger.info(f"Audit trail: {event}") 