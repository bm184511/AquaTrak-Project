"""
Authentication API Endpoints
AquaTrak - AI-GIS Water Risk Monitoring Platform

PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2024 AquaTrak. All rights reserved.
This module is part of the AquaTrak proprietary software suite.
Unauthorized copying, distribution, or use is strictly prohibited.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.settings import get_settings
from config.database import get_db
from models.system import User, Organization
from common_utils.exceptions import AuthenticationError

# Initialize components
router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    organization_id: Optional[str]
    country: str
    language: str
    is_active: bool
    created_at: str
    updated_at: str

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != token_type:
            raise AuthenticationError("Invalid token type")
        return payload
    except JWTError:
        raise AuthenticationError("Invalid token")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token")
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# API Endpoints
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": str(user.organization_id) if user.organization_id else None,
            "country": user.country,
            "language": user.language,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
    )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token endpoint"""
    try:
        payload = verify_token(request.refresh_token, "refresh")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid refresh token")
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": user_id})
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """User logout endpoint"""
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return a success response
    return {"message": "Successfully logged out"}

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        country=current_user.country,
        language=current_user.language,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat(),
    )

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    # Update user fields
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.username is not None:
        current_user.username = request.username
    if request.language is not None:
        current_user.language = request.language
    if request.country is not None:
        current_user.country = request.country
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        country=current_user.country,
        language=current_user.language,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat(),
    )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    current_user.password_hash = get_password_hash(new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"} 