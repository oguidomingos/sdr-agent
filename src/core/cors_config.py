"""
CORS configuration for FastAPI applications
"""
import os
from typing import List

def get_cors_origins() -> List[str]:
    """Get allowed CORS origins from environment"""
    cors_origins_env = os.environ.get("CORS_ORIGINS", "")
    
    if cors_origins_env:
        origins = [origin.strip() for origin in cors_origins_env.split(",")]
    else:
        # Default origins for development and production
        origins = [
            "https://sdr-agent-frontend.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]
    
    return origins

def get_cors_config() -> dict:
    """Get complete CORS configuration"""
    return {
        "allow_origins": get_cors_origins(),
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
        "max_age": 86400  # 24 hours
    }