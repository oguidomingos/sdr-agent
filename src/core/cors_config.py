"""
CORS configuration for FastAPI applications
"""
import os
import re
from typing import List

def is_vercel_environment() -> bool:
    """Check if running in Vercel environment"""
    return os.environ.get("VERCEL") == "1"

def get_vercel_deployment_url() -> str:
    """Get current Vercel deployment URL"""
    return os.environ.get("VERCEL_URL", "")

def get_vercel_origins() -> List[str]:
    """Get all possible Vercel origins for this project"""
    origins = []
    
    # Current deployment URL
    vercel_url = get_vercel_deployment_url()
    if vercel_url:
        origins.append(f"https://{vercel_url}")
    
    # Project-specific patterns
    project_name = "sdr-agent"
    team_name = "oguidomingos-projects"
    
    # Common Vercel URL patterns
    vercel_patterns = [
        f"https://{project_name}-*.vercel.app",
        f"https://{project_name}-*-{team_name}.vercel.app",
        "https://*.vercel.app"
    ]
    
    origins.extend(vercel_patterns)
    return origins

def get_cors_origins() -> List[str]:
    """Get allowed CORS origins from environment"""
    cors_origins_env = os.environ.get("CORS_ORIGINS", "")
    
    if cors_origins_env:
        origins = [origin.strip() for origin in cors_origins_env.split(",")]
    else:
        origins = []
        
        # Add Vercel origins if in Vercel environment
        if is_vercel_environment():
            origins.extend(get_vercel_origins())
        
        # Add development origins
        origins.extend([
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ])
        
        # In production, allow all origins as fallback
        if is_vercel_environment():
            origins.append("*")
    
    return origins

def get_cors_config_for_vercel() -> dict:
    """Get CORS configuration optimized for Vercel deployment"""
    origins = get_cors_origins()
    
    # In Vercel production, be more permissive to avoid issues
    if is_vercel_environment():
        return {
            "allow_origins": ["*"],  # Allow all origins in production
            "allow_credentials": False,  # Must be False when allow_origins is "*"
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["*"],  # Allow all headers
            "max_age": 86400
        }
    else:
        # Development configuration
        return {
            "allow_origins": origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": [
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "X-CSRF-Token",
                "X-Api-Version",
                "X-Signature",
                "X-Hub-Signature-256",
                "Cache-Control",
                "Pragma"
            ],
            "max_age": 86400
        }

def get_cors_config() -> dict:
    """Get complete CORS configuration (legacy function)"""
    return get_cors_config_for_vercel()