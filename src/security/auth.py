# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
Authentication and Authorization Module for AquaTrak
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    roles: list = []

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    roles: list = []
    is_active: bool = True
    country_code: Optional[str] = None
    language: str = "en"

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # In practice, this would fetch from database
        # For now, return a mock user
        user = get_user_by_username(username)
        if user is None:
            raise credentials_exception
        
        return user
        
    except JWTError:
        raise credentials_exception

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username (mock implementation)"""
    # In practice, this would query the database
    # For now, return a mock user
    if username == "admin":
        return User(
            id="1",
            username="admin",
            email="admin@aquatrak.com",
            full_name="Administrator",
            roles=["admin"],
            is_active=True,
            country_code="IR",
            language="en"
        )
    return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if not user:
        return None
    
    # In practice, verify against hashed password in database
    if username == "admin" and password == "admin123":  # Mock authentication
        return user
    
    return None

def setup_security(app):
    """Setup security middleware and dependencies"""
    # Add security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

def check_permission(user: User, required_role: str) -> bool:
    """Check if user has required role"""
    return required_role in user.roles

def require_role(role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if not check_permission(current_user, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role"""
    return require_role("admin")(current_user)

def require_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require basic user role"""
    return require_role("user")(current_user)

def get_user_country(user: User) -> str:
    """Get user's country code"""
    return user.country_code or settings.DEFAULT_COUNTRY

def get_user_language(user: User) -> str:
    """Get user's preferred language"""
    return user.language or settings.DEFAULT_LANGUAGE

def is_country_allowed(country_code: str) -> bool:
    """Check if country is allowed access"""
    return country_code in settings.SUPPORTED_COUNTRIES

def is_language_supported(language_code: str) -> bool:
    """Check if language is supported"""
    return language_code in settings.SUPPORTED_LANGUAGES

def validate_country_access(user: User) -> bool:
    """Validate user's country access"""
    country = get_user_country(user)
    if not is_country_allowed(country):
        logger.warning(f"Access denied for country: {country}")
        return False
    return True

def validate_language_access(user: User) -> bool:
    """Validate user's language access"""
    language = get_user_language(user)
    if not is_language_supported(language):
        logger.warning(f"Language not supported: {language}")
        return False
    return True

def create_user_session(user: User) -> Dict[str, Any]:
    """Create user session data"""
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": user.roles,
        "country_code": user.country_code,
        "language": user.language,
        "session_start": datetime.utcnow().isoformat()
    }

def log_user_activity(user: User, action: str, details: Dict[str, Any] = None):
    """Log user activity for audit"""
    activity = {
        "user_id": user.id,
        "username": user.username,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": "unknown",  # Would get from request
        "user_agent": "unknown",  # Would get from request
        "details": details or {}
    }
    logger.info(f"User activity: {activity}")

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    # In practice, use proper encryption
    import base64
    return base64.b64encode(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    # In practice, use proper decryption
    import base64
    return base64.b64decode(encrypted_data.encode()).decode() 