import uvicorn
import os
from dotenv import load_dotenv
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from src.config.settings import settings
from src.core.db import init_db, seed_default_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - runs on startup and shutdown
    """
    # Startup
    print("🚀 Starting SDR Agent Multi-Client SaaS...")
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        await init_db()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")
        print("🔄 Application will continue...")
    
    # Seed default data if enabled (separate from table creation)
    if settings.SEED_DATABASE:
        try:
            print("🌱 Seeding default data...")
            await seed_default_data()
        except Exception as e:
            print(f"⚠️  Database seeding error: {e}")
            print("🔄 Application will continue without default data...")
    
    print("✅ Application startup complete!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SDR Agent...")


# Create FastAPI application with multi-client support
app = FastAPI(
    title="SDR Agent Multi-Client SaaS",
    description="Multi-tenant SDR Agent with WhatsApp integration, AI processing, and conversation management",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routers
from src.api.routes import router as webhook_router
from src.api.clients import router as clients_router

# Include webhook routes
app.include_router(webhook_router)

# Include new multi-client API routes
app.include_router(clients_router)

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

# Webhook endpoint is handled by src/api/routes.py


def main():
    """
    Main function to start the FastAPI server
    """
    # Load environment variables
    load_dotenv()
    
    # Configure uvicorn
    config = {
        "app": "main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.DEBUG,
        "workers": 1 if settings.DEBUG else min(os.cpu_count(), 4),
        "log_level": "debug" if settings.DEBUG else "info",
        "access_log": settings.DEBUG
    }
    
    # Start the server
    print(f"🚀 Starting SDR Agent Multi-Client SaaS on {config['host']}:{config['port']}")
    print(f"📚 API Documentation: http://{config['host']}:{config['port']}/docs")
    print(f"🔧 Environment: {settings.ENVIRONMENT}")
    
    uvicorn.run(**config)


if __name__ == "__main__":
    main()