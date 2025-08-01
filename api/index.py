from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add the parent directory to Python path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import settings
from src.core.db import init_db, seed_default_data

# Create FastAPI application for Vercel
app = FastAPI(
    title="SDR Agent Multi-Client SaaS",
    description="Multi-tenant SDR Agent with WhatsApp integration, AI processing, and conversation management",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routers
from src.api.routes import router as legacy_webhook_router
from src.api.clients import router as clients_router
from src.api.playbooks import router as playbooks_router
from src.api.messages import router as messages_router
from src.api.auth_routes import router as auth_router, client_router
from src.api.webhook_routes import router as webhook_router

# Include authentication routes
app.include_router(auth_router)
app.include_router(client_router)

# Include new multi-tenant webhook routes
app.include_router(webhook_router)

# Include legacy webhook routes (for backward compatibility)
app.include_router(legacy_webhook_router, prefix="/legacy")

# Include playbook API routes
app.include_router(playbooks_router)

# Include messages API routes
app.include_router(messages_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the multi-client system"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
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

# Handler for Vercel
handler = app