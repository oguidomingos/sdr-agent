"""
Main API entry point for Vercel serverless deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sdr-agent-frontend.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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