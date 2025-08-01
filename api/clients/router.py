"""
Clients router for serverless deployment
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.supabase_db import get_supabase_db
from api.auth.router import verify_token

router = APIRouter()

# Pydantic models
class ClientCreate(BaseModel):
    name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    whatsapp_number: Optional[str] = None
    evolution_instance: Optional[str] = None
    gemini_api_key: Optional[str] = None
    agent_name: Optional[str] = "Assistente"
    agent_persona: Optional[str] = None
    welcome_message: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None

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

@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    token_data: dict = Depends(verify_token)
):
    """Get all clients for the authenticated user"""
    db = get_supabase_db()
    
    clients = await db.get_clients_by_owner(token_data['user_id'])
    
    # Apply pagination
    paginated_clients = clients[skip:skip + limit]
    
    return [
        ClientResponse(
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
        for client in paginated_clients
    ]

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    token_data: dict = Depends(verify_token)
):
    """Get a specific client by ID"""
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

@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    token_data: dict = Depends(verify_token)
):
    """Create a new client"""
    db = get_supabase_db()
    
    # Check if domain is already taken
    if client_data.domain:
        existing_client = await db.get_client_by_domain(client_data.domain)
        if existing_client:
            raise HTTPException(status_code=400, detail="Domain already taken")
    
    # Create client data
    new_client_data = {
        "owner_id": token_data['user_id'],
        "name": client_data.name,
        "description": client_data.description,
        "domain": client_data.domain,
        "status": "trial",
        "whatsapp_number": client_data.whatsapp_number,
        "evolution_instance": client_data.evolution_instance,
        "gemini_api_key": client_data.gemini_api_key,
        "agent_name": client_data.agent_name or "Assistente",
        "agent_persona": client_data.agent_persona,
        "welcome_message": client_data.welcome_message,
        "contact_email": client_data.contact_email,
        "contact_phone": client_data.contact_phone,
        "business_hours": client_data.business_hours,
        "session_timeout": 3600,
        "max_history": 50,
        "context_window_size": 20,
        "ai_temperature": 70
    }
    
    client = await db.create_client(new_client_data)
    if not client:
        raise HTTPException(status_code=500, detail="Failed to create client")
    
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

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    token_data: dict = Depends(verify_token)
):
    """Update an existing client"""
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

@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    token_data: dict = Depends(verify_token)
):
    """Delete a client"""
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