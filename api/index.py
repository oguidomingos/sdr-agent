from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config.settings import settings
    from src.api.auth_routes import router as auth_router, client_router
    from src.api.clients import router as clients_router
    from src.api.webhook_routes import router as webhook_router
    from src.api.playbooks import router as playbooks_router
    from src.api.messages import router as messages_router
except ImportError as e:
    print(f"Import error: {e}")
    settings = None

app = FastAPI(
    title="SDR Agent API",
    description="Multi-tenant SDR Agent API",
    version="2.0.0"
)

# Configure CORS - Permitir todas as origens para debug
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporariamente permitir todas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers if available
if settings:
    try:
        app.include_router(auth_router)
        app.include_router(client_router)
        app.include_router(webhook_router)
        app.include_router(clients_router)
        app.include_router(playbooks_router)
        app.include_router(messages_router)
    except Exception as e:
        print(f"Router error: {e}")

@app.get("/")
async def root():
    return {
        "message": "SDR Agent API", 
        "version": "2.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

# Handler para Vercel - Simplificado
app_handler = app