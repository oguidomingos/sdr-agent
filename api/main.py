"""
Main API handler for Vercel serverless deployment with real Supabase integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Try to import routers safely
try:
    from api.auth.router import router as auth_router
    AUTH_ROUTER_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import auth router: {e}")
    AUTH_ROUTER_AVAILABLE = False

try:
    from api.clients.router import router as clients_router
    CLIENTS_ROUTER_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import clients router: {e}")
    CLIENTS_ROUTER_AVAILABLE = False

try:
    from api.messages.router import router as messages_router
    MESSAGES_ROUTER_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import messages router: {e}")
    MESSAGES_ROUTER_AVAILABLE = False

try:
    from api.webhook.router import router as webhook_router
    WEBHOOK_ROUTER_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import webhook router: {e}")
    WEBHOOK_ROUTER_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="SDR Agent Multi-Client SaaS",
    description="Multi-tenant SDR Agent with WhatsApp integration, AI processing, and conversation management",
    version="2.0.0"
)

# Configure CORS
cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400
)

# Include routers safely
if AUTH_ROUTER_AVAILABLE:
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])

if CLIENTS_ROUTER_AVAILABLE:
    app.include_router(clients_router, prefix="/clients", tags=["clients"])

if MESSAGES_ROUTER_AVAILABLE:
    app.include_router(messages_router, prefix="/messages", tags=["messages"])

if WEBHOOK_ROUTER_AVAILABLE:
    app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with environment validation"""
    # Check required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "JWT_SECRET"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise HTTPException(
            status_code=500, 
            detail=f"Missing environment variables: {', '.join(missing_vars)}"
        )
    
    # Test Supabase connection
    try:
        from src.core.supabase_db import get_supabase_db
        db = get_supabase_db()
        # Simple connection test
        result = db.client.table('users').select('id').limit(1).execute()
        supabase_status = "connected"
    except Exception as e:
        supabase_status = f"error: {str(e)}"
        print(f"Supabase connection error: {e}")  # Log for debugging
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "cors": "enabled",
        "vercel": os.environ.get("VERCEL", "0") == "1",
        "supabase": supabase_status,
        "environment_vars": {
            "SUPABASE_URL": "✅" if os.environ.get("SUPABASE_URL") else "❌",
            "SUPABASE_SERVICE_ROLE_KEY": "✅" if os.environ.get("SUPABASE_SERVICE_ROLE_KEY") else "❌",
            "JWT_SECRET": "✅" if os.environ.get("JWT_SECRET") else "❌"
        }
    }

# CORS test endpoint
@app.get("/cors-test")
async def cors_test():
    """Test CORS configuration"""
    return {
        "message": "CORS is working!",
        "origins": cors_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "headers": "*"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SDR Agent API - Full Version with Supabase",
        "version": "2.0.0",
        "cors": "enabled",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/*",
            "clients": "/clients/*",
            "messages": "/messages/*",
            "webhook": "/webhook/*"
        }
    }

# Main handler for Vercel
def handler(request):
    """Main handler for all requests"""
    return app(request)