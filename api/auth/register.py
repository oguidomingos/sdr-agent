"""
Register endpoint for Vercel serverless deployment
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import bcrypt

from src.core.supabase_db import get_supabase_db

app = FastAPI()

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    status: str
    plan: str
    created_at: str

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@app.post("/", response_model=UserResponse)
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