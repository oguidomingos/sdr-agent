"""
Login endpoint for Vercel serverless deployment
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import jwt
import bcrypt
from datetime import datetime, timedelta
import os

from src.core.supabase_db import get_supabase_db

app = FastAPI()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    email: str

# JWT configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "your-jwt-secret-here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))

def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@app.post("/", response_model=TokenResponse)
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
    await db.update_user(user['id'], {'last_login': datetime.utcnow().isoformat()})
    
    # Create access token
    access_token = create_access_token(user['id'], user['email'])
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user_id=user['id'],
        email=user['email']
    )