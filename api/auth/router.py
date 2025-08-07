"""
Authentication router for serverless deployment
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
import os

from src.core.supabase_db import get_supabase_db

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    email: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    status: str
    plan: str
    created_at: str

# JWT configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "your-jwt-secret-here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))

def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """User login endpoint"""
    db = get_supabase_db()
    
    # Get user by email
    user = await db.get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(user_data.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check user status
    if user['status'] != 'active':
        raise HTTPException(status_code=401, detail="Account is not active")
    
    # Update last login
    await db.update_user(user['id'], {'last_login': datetime.now(timezone.utc).isoformat()})
    
    # Create access token
    access_token = create_access_token(user['id'], user['email'])
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user_id=user['id'],
        email=user['email']
    )

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """User registration endpoint"""
    db = get_supabase_db()
    
    # Check if user already exists
    existing_user = await db.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user data
    new_user_data = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "status": "active",
        "plan": "free"
    }
    
    # Create user
    user = await db.create_user(new_user_data)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        first_name=user.get('first_name'),
        last_name=user.get('last_name'),
        status=user['status'],
        plan=user['plan'],
        created_at=user['created_at']
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user information"""
    db = get_supabase_db()
    
    user = await db.get_user_by_id(token_data['user_id'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        first_name=user.get('first_name'),
        last_name=user.get('last_name'),
        status=user['status'],
        plan=user['plan'],
        created_at=user['created_at']
    )

@router.post("/refresh")
async def refresh_token(token_data: dict = Depends(verify_token)):
    """Refresh access token"""
    db = get_supabase_db()
    
    # Verify user still exists and is active
    user = await db.get_user_by_id(token_data['user_id'])
    if not user or user['status'] != 'active':
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Create new token
    access_token = create_access_token(user['id'], user['email'])
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user_id=user['id'],
        email=user['email']
    )