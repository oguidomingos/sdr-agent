"""
Simplified API handler for Vercel with real Supabase integration
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import sys
import jwt
import bcrypt
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import Supabase client directly
try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client not available")
    create_client = None
    Client = None

# Create FastAPI app
app = FastAPI(
    title="SDR Agent - Fixed Authentication",
    description="SDR Agent with real Supabase authentication",
    version="2.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Must be False when origins = "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400
)

# Security
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

# Global Supabase client
_supabase_client = None

def get_supabase_client():
    """Get Supabase client instance"""
    global _supabase_client
    
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise HTTPException(
                status_code=500, 
                detail="Missing Supabase configuration"
            )
        
        if not create_client:
            raise HTTPException(
                status_code=500, 
                detail="Supabase client not available"
            )
        
        try:
            _supabase_client = create_client(url, key)
            # Test connection
            result = _supabase_client.table('users').select('id').limit(1).execute()
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Database connection failed: {str(e)}"
            )
    
    return _supabase_client

# JWT configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "fallback-secret-key")
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with environment validation"""
    # Check required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "JWT_SECRET"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        return {
            "status": "unhealthy",
            "error": f"Missing environment variables: {', '.join(missing_vars)}",
            "environment_vars": {var: "❌" for var in missing_vars}
        }
    
    # Test Supabase connection
    try:
        client = get_supabase_client()
        result = client.table('users').select('id').limit(1).execute()
        supabase_status = "connected"
    except Exception as e:
        supabase_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if supabase_status == "connected" else "unhealthy",
        "version": "2.1.0",
        "cors": "enabled",
        "vercel": os.environ.get("VERCEL", "0") == "1",
        "supabase": supabase_status,
        "environment_vars": {
            "SUPABASE_URL": "✅" if os.environ.get("SUPABASE_URL") else "❌",
            "SUPABASE_SERVICE_ROLE_KEY": "✅" if os.environ.get("SUPABASE_SERVICE_ROLE_KEY") else "❌",
            "JWT_SECRET": "✅" if os.environ.get("JWT_SECRET") else "❌"
        }
    }

# Authentication endpoints
@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """User login endpoint"""
    try:
        client = get_supabase_client()
        
        # Get user by email
        result = client.table('users').select('*').eq('email', user_data.email).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = result.data[0]
        
        # Verify password
        if not verify_password(user_data.password, user['hashed_password']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check user status
        if user['status'] != 'active':
            raise HTTPException(status_code=401, detail="Account is not active")
        
        # Update last login
        client.table('users').update({
            'last_login': datetime.utcnow().isoformat()
        }).eq('id', user['id']).execute()
        
        # Create access token
        access_token = create_access_token(user['id'], user['email'])
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_HOURS * 3600,
            user_id=user['id'],
            email=user['email']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """User registration endpoint"""
    try:
        client = get_supabase_client()
        
        # Check if user already exists
        result = client.table('users').select('*').eq('email', user_data.email).execute()
        
        if result.data:
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
        result = client.table('users').insert(new_user_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        user = result.data[0]
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            first_name=user.get('first_name'),
            last_name=user.get('last_name'),
            status=user['status'],
            plan=user['plan'],
            created_at=user['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user information - REAL DATA FROM SUPABASE"""
    try:
        client = get_supabase_client()
        
        # Get user from database using token user_id
        result = client.table('users').select('*').eq('id', token_data['user_id']).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = result.data[0]
        
        # Return REAL user data from database
        return UserResponse(
            id=user['id'],
            email=user['email'],  # This should be the REAL email
            first_name=user.get('first_name'),  # This should be the REAL first name
            last_name=user.get('last_name'),  # This should be the REAL last name
            status=user['status'],
            plan=user['plan'],
            created_at=user['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user data: {str(e)}")

# Clients endpoint
@app.get("/clients/")
async def get_clients(token_data: dict = Depends(verify_token)):
    """Get clients for authenticated user"""
    try:
        client = get_supabase_client()
        
        # Get clients owned by user
        result = client.table('clients').select('*').eq('owner_id', token_data['user_id']).execute()
        
        clients = result.data or []
        
        return {
            "items": clients,
            "total": len(clients),
            "skip": 0,
            "limit": 100
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get clients: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SDR Agent API - Fixed Authentication",
        "version": "2.1.0",
        "status": "Fixed authentication with real Supabase data",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/*",
            "clients": "/clients/"
        }
    }

# Main handler for Vercel
def handler(request):
    """Main handler for all requests"""
    return app(request)