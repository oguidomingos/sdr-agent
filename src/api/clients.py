from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from src.core.db import get_db, Client, ClientStatus, Playbook, PlaybookStatus, Message, MessageStatus
from src.config.settings import settings
from src.types.schemas import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new client"""
    try:
        # Check if domain already exists
        existing_client = await db.execute(
            select(Client).where(Client.domain == client_data.domain)
        )
        if existing_client.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Domain already exists"
            )
        
        # Create new client
        client = Client(
            id=str(uuid.uuid4()),
            name=client_data.name,
            description=client_data.description,
            domain=client_data.domain,
            status=ClientStatus.TRIAL if settings.REQUIRE_CLIENT_APPROVAL else ClientStatus.ACTIVE,
            
            # API Configuration
            evolution_api_url=client_data.evolution_api_url,
            evolution_api_key=client_data.evolution_api_key,
            evolution_instance=client_data.evolution_instance,
            gemini_api_key=client_data.gemini_api_key,
            gemini_model=client_data.gemini_model or settings.GEMINI_MODEL,
            
            # Session Configuration
            session_timeout=client_data.session_timeout or settings.SESSION_TIMEOUT,
            max_history=client_data.max_history or settings.MAX_HISTORY_MESSAGES,
            context_window_size=client_data.context_window_size or settings.CONTEXT_WINDOW_SIZE,
            
            # Persona and Branding
            agent_name=client_data.agent_name or "SDR Assistant",
            agent_persona=client_data.agent_persona,
            welcome_message=client_data.welcome_message or "Olá! Como posso ajudá-lo?",
            logo_url=client_data.logo_url,
            
            # Business Information
            contact_email=client_data.contact_email,
            contact_phone=client_data.contact_phone,
            business_hours=client_data.business_hours or {},
            timezone=client_data.timezone or "UTC",
            
            # Settings
            ai_temperature=client_data.ai_temperature or 70,
            rate_limit_enabled=client_data.rate_limit_enabled if client_data.rate_limit_enabled is not None else True,
            rate_limit_calls=client_data.rate_limit_calls or settings.RATE_LIMIT_CALLS,
            rate_limit_period=client_data.rate_limit_period or settings.RATE_LIMIT_PERIOD
        )
        
        db.add(client)
        await db.commit()
        await db.refresh(client)
        
        # Create default playbook for the client
        if client_data.create_default_playbook:
            default_playbook = Playbook(
                id=str(uuid.uuid4()),
                client_id=client.id,
                name="Default Medical SPIN Playbook",
                description="Default playbook using SPIN methodology",
                status=PlaybookStatus.ACTIVE,
                is_default=True,
                steps=[
                    {"stage": "welcome", "message": client.welcome_message, "next": "situation"},
                    {"stage": "situation", "prompt": "Descubra a situação atual", "next": "problem"},
                    {"stage": "problem", "prompt": "Identifique os problemas", "next": "implication"},
                    {"stage": "implication", "prompt": "Explore as implicações", "next": "need_payoff"},
                    {"stage": "need_payoff", "prompt": "Apresente os benefícios", "next": "close"}
                ],
                situation_prompts=[
                    "Há quanto tempo sente esses sintomas?",
                    "Como isso está afetando seu dia a dia?"
                ],
                problem_prompts=[
                    "Quais são os principais desconfortos?",
                    "O que mais te preocupa sobre essa situação?"
                ],
                implication_prompts=[
                    "Como isso pode evoluir se não for tratado?",
                    "Que impacto isso pode ter na sua qualidade de vida?"
                ],
                need_payoff_prompts=[
                    "Como seria sua vida sem esses sintomas?",
                    "Qual a importância de resolver isso agora?"
                ]
            )
            db.add(default_playbook)
            await db.commit()
        
        return ClientResponse.from_orm(client)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ClientListResponse)
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ClientStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all clients with pagination and filtering"""
    try:
        query = select(Client)
        
        # Apply filters
        if status:
            query = query.where(Client.status == status)
        
        if search:
            query = query.where(
                Client.name.ilike(f"%{search}%") |
                Client.domain.ilike(f"%{search}%") |
                Client.description.ilike(f"%{search}%")
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Client.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        clients = result.scalars().all()
        
        return ClientListResponse(
            clients=[ClientResponse.from_orm(client) for client in clients],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific client by ID"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return ClientResponse.from_orm(client)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing client"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Check if domain conflicts with another client
        if client_data.domain and client_data.domain != client.domain:
            existing_client = await db.execute(
                select(Client).where(
                    Client.domain == client_data.domain,
                    Client.id != client_id
                )
            )
            if existing_client.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Domain already exists"
                )
        
        # Update client fields
        update_data = client_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        client.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(client)
        
        return ClientResponse.from_orm(client)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a client (soft delete by setting status to inactive)"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Soft delete by setting status to inactive
        client.status = ClientStatus.INACTIVE
        client.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "Client deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/stats")
async def get_client_stats(
    client_id: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get client statistics"""
    try:
        # Verify client exists
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Calculate date range
        from_date = datetime.utcnow() - timedelta(days=days)
        
        # Get message statistics
        total_messages = await db.execute(
            select(func.count(Message.id)).where(
                Message.client_id == client_id,
                Message.timestamp >= from_date
            )
        )
        
        qualified_leads = await db.execute(
            select(func.count(Message.id)).where(
                Message.client_id == client_id,
                Message.status == MessageStatus.QUALIFIED,
                Message.timestamp >= from_date
            )
        )
        
        scheduled_appointments = await db.execute(
            select(func.count(Message.id)).where(
                Message.client_id == client_id,
                Message.status == MessageStatus.SCHEDULED,
                Message.timestamp >= from_date
            )
        )
        
        unique_users = await db.execute(
            select(func.count(func.distinct(Message.user_id))).where(
                Message.client_id == client_id,
                Message.timestamp >= from_date
            )
        )
        
        return {
            "client_id": client_id,
            "period_days": days,
            "total_messages": total_messages.scalar(),
            "unique_users": unique_users.scalar(),
            "qualified_leads": qualified_leads.scalar(),
            "scheduled_appointments": scheduled_appointments.scalar(),
            "conversion_rate": (
                qualified_leads.scalar() / unique_users.scalar() * 100
                if unique_users.scalar() > 0 else 0
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/activate")
async def activate_client(
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Activate a client"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client.status = ClientStatus.ACTIVE
        client.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "Client activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/suspend")
async def suspend_client(
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Suspend a client"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client.status = ClientStatus.SUSPENDED
        client.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "Client suspended successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))