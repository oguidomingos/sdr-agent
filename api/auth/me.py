"""
Get current user endpoint for Vercel serverless deployment
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import os

from src.core.supabase_db import get_supabase_db

app = FastAPI()
security = HTTPBearer()

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

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/", response_model=UserResponse)
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