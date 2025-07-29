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
from src.api.routes import app as legacy_routes
from src.api.clients import router as clients_router

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

# Webhook endpoint for WhatsApp messages
@app.post("/webhook/whatsapp")
async def webhook_whatsapp(request: Request) -> Dict[str, Any]:
    """Webhook endpoint for WhatsApp messages from Evolution API"""
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        print(f"=== Webhook Received ===")
        print(f"Instance: {webhook_data.get('instance', 'unknown')}")
        
        # Basic validation - check if it's a message
        if "data" not in webhook_data:
            return {"status": "ignored", "reason": "no_data"}
            
        data = webhook_data["data"]
        
        # Check if it's an incoming message
        if "key" not in data or "message" not in data:
            return {"status": "ignored", "reason": "not_message"}
            
        # Check if it's from user (not from us)
        if data["key"].get("fromMe", False):
            return {"status": "ignored", "reason": "from_me"}
            
        # Extract message content
        message_content = data["message"].get("conversation", "")
        if not message_content:
            # Try extended text message
            if "extendedTextMessage" in data["message"]:
                message_content = data["message"]["extendedTextMessage"].get("text", "")
        
        if not message_content:
            return {"status": "ignored", "reason": "no_content"}
            
        # Extract sender info
        sender_number = data["key"]["remoteJid"]
        sender_name = data.get("pushName", "User")
        instance_name = webhook_data.get("instance", "")
        
        print(f"Message from {sender_name} ({sender_number}): {message_content}")
        print(f"Instance: {instance_name}")
        
        # Find client by instance name
        from src.core.db import AsyncSessionLocal, Client, init_db
        from sqlalchemy import select
        
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Client).where(Client.evolution_instance == instance_name)
                )
                client = result.scalar_one_or_none()
                
                if not client:
                    print(f"⚠️  No client found for instance: {instance_name}")
                    return {"status": "error", "reason": "no_client_found", "instance": instance_name}
        except Exception as db_error:
            print(f"⚠️  Database error: {db_error}")
            return {"status": "error", "reason": "database_error", "error": str(db_error)}
        
        print(f"✅ Found client: {client.name} (ID: {client.id})")
        
        # TODO: Process message with AI and send response
        # For now, just acknowledge receipt with client info
        return {
            "status": "received",
            "client_id": client.id,
            "client_name": client.name,
            "instance": instance_name,
            "sender": sender_number,
            "message": message_content,
            "next_step": "process_with_ai"
        }
        
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


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