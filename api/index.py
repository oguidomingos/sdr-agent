"""
Main API entry point for Vercel serverless deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import CORS configuration
from src.core.cors_config import get_cors_config

# Import routers
from api.auth.router import router as auth_router
from api.clients.router import router as clients_router
from api.messages.router import router as messages_router
from api.webhook.router import router as webhook_router

# Create FastAPI app
app = FastAPI(
    title="SDR Agent Multi-Client SaaS",
    description="Multi-tenant SDR Agent with WhatsApp integration, AI processing, and conversation management",
    version="2.0.0"
)

# Configure CORS with proper settings
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
    max_age=cors_config["max_age"]
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(clients_router, prefix="/clients", tags=["clients"])
app.include_router(messages_router, prefix="/messages", tags=["messages"])
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the multi-client system"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "multi_client": True
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SDR Agent Multi-Client SaaS API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "webhook": "/webhook/whatsapp"
    }