"""
Individual client endpoint for Vercel serverless deployment
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt
import os

from src.core.supabase_db import get_supabase_db

app = FastAPI()
security = HTTPBearer()

class ClientResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str]
    domain: Optional[str]
    status: str
    whatsapp_number: Optional[str]
    evolution_instance: Optional[str]
    agent_name: str
    agent_persona: Optional[str]
    welcome_message: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    business_hours: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    whatsapp_number: Optional[str] = None
    evolution_instance: Optional[str] = None
    gemini_api_key: Optional[str] = None
    agent_name: Optional[str] = None
    agent_persona: Optional[str] = None
    welcome_message: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

# JWT configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "your-jwt-secret-here")
JWT_ALGORITHM = "HS256"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_client_id_from_path(request: Request) -> str:
    """Extract client ID from URL path"""
    path_parts = request.url.path.strip('/').split('/')
    # Path should be like /api/clients/[id] or /clients/[id]
    if len(path_parts) >= 2:
        return path_parts[-1]  # Last part should be the ID
    raise HTTPException(status_code=400, detail="Invalid client ID in path")

@app.get("/", response_model=ClientResponse)
async def get_client(
    request: Request,
    token_data: dict = Depends(verify_token)
):
    """Get a specific client by ID"""
    client_id = get_client_id_from_path(request)
    db = get_supabase_db()
    
    client = await db.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check ownership
    if client['owner_id'] != token_data['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ClientResponse(
        id=client['id'],
        owner_id=client['owner_id'],
        name=client['name'],
        description=client.get('description'),
        domain=client.get('domain'),
        status=client['status'],
        whatsapp_number=client.get('whatsapp_number'),
        evolution_instance=client.get('evolution_instance'),
        agent_name=client.get('agent_name', 'Assistente'),
        agent_persona=client.get('agent_persona'),
        welcome_message=client.get('welcome_message'),
        contact_email=client.get('contact_email'),
        contact_phone=client.get('contact_phone'),
        business_hours=client.get('business_hours'),
        created_at=client['created_at'],
        updated_at=client['updated_at']
    )

@app.put("/", response_model=ClientResponse)
async def update_client(
    request: Request,
    client_data: ClientUpdate,
    token_data: dict = Depends(verify_token)
):
    """Update an existing client"""
    client_id = get_client_id_from_path(request)
    db = get_supabase_db()
    
    # Check if client exists and user owns it
    existing_client = await db.get_client_by_id(client_id)
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if existing_client['owner_id'] != token_data['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check domain uniqueness if being updated
    if client_data.domain and client_data.domain != existing_client.get('domain'):
        domain_client = await db.get_client_by_domain(client_data.domain)
        if domain_client:
            raise HTTPException(status_code=400, detail="Domain already taken")
    
    # Prepare update data
    update_data = {}
    for field, value in client_data.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    # Update client
    updated_client = await db.update_client(client_id, update_data)
    if not updated_client:
        raise HTTPException(status_code=500, detail="Failed to update client")
    
    return ClientResponse(
        id=updated_client['id'],
        owner_id=updated_client['owner_id'],
        name=updated_client['name'],
        description=updated_client.get('description'),
        domain=updated_client.get('domain'),
        status=updated_client['status'],
        whatsapp_number=updated_client.get('whatsapp_number'),
        evolution_instance=updated_client.get('evolution_instance'),
        agent_name=updated_client.get('agent_name', 'Assistente'),
        agent_persona=updated_client.get('agent_persona'),
        welcome_message=updated_client.get('welcome_message'),
        contact_email=updated_client.get('contact_email'),
        contact_phone=updated_client.get('contact_phone'),
        business_hours=updated_client.get('business_hours'),
        created_at=updated_client['created_at'],
        updated_at=updated_client['updated_at']
    )

@app.delete("/")
async def delete_client(
    request: Request,
    token_data: dict = Depends(verify_token)
):
    """Delete a client"""
    client_id = get_client_id_from_path(request)
    db = get_supabase_db()
    
    # Check if client exists and user owns it
    existing_client = await db.get_client_by_id(client_id)
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if existing_client['owner_id'] != token_data['user_id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete client
    success = await db.delete_client(client_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete client")
    
    return {"message": "Client deleted successfully"}