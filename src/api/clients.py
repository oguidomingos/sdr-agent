from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import httpx

from src.core.db import get_db, Client, Playbook
from src.types.schemas import (
    ClientResponse,
    ClientListResponse,
    ClientCreate,
    ClientUpdate,
    PlaybookCreate
)

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("", response_model=ClientListResponse)
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all clients with pagination"""
    # Get total count
    count_stmt = select(func.count(Client.id))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # Get clients
    stmt = select(Client).offset(skip).limit(limit).order_by(Client.created_at.desc())
    result = await db.execute(stmt)
    clients = result.scalars().all()
    
    return ClientListResponse(
        clients=[ClientResponse.model_validate(client) for client in clients],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific client by ID"""
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check webhook status if not already set
    if not hasattr(client, 'has_webhook_configured'):
        client.has_webhook_configured = False
        
    return ClientResponse.model_validate(client)

@router.post("", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new client
    
    Parameters:
    - register_webhook: If True, automatically registers webhook for Evolution instance
      after client creation (default: False)
    """
    import uuid
    from src.core.db import ClientStatus, PlaybookStatus
    
    # Create client
    client = Client(
        id=str(uuid.uuid4()),
        name=client_data.name,
        description=client_data.description,
        domain=client_data.domain,
        status=ClientStatus.TRIAL,
        evolution_api_url=client_data.evolution_api_url,
        evolution_api_key=client_data.evolution_api_key,
        evolution_instance=client_data.evolution_instance,
        gemini_api_key=client_data.gemini_api_key,
        gemini_model=client_data.gemini_model or "gemini-2.0-flash",
        session_timeout=client_data.session_timeout or 3600,
        max_history=client_data.max_history or 50,
        context_window_size=client_data.context_window_size or 20,
        agent_name=client_data.agent_name or "SDR Assistant",
        agent_persona=client_data.agent_persona,
        welcome_message=client_data.welcome_message,
        logo_url=client_data.logo_url,
        contact_email=client_data.contact_email,
        contact_phone=client_data.contact_phone,
        business_hours=client_data.business_hours,
        timezone=client_data.timezone or "UTC",
        ai_temperature=client_data.ai_temperature or 70,
        rate_limit_enabled=client_data.rate_limit_enabled or True,
        rate_limit_calls=client_data.rate_limit_calls or 100,
        rate_limit_period=client_data.rate_limit_period or 3600
    )
    
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    # Create default playbook if requested
    if client_data.create_default_playbook:
        default_playbook = Playbook(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name="Default SDR Playbook",
            description="Default playbook for lead qualification using SPIN methodology",
            status=PlaybookStatus.ACTIVE,
            is_default=True,
            steps=[
                {"stage": "welcome", "message": "Olá! Como posso ajudá-lo?", "next": "situation"},
                {"stage": "situation", "prompt": "Descubra a situação atual do lead", "next": "problem"},
                {"stage": "problem", "prompt": "Identifique os problemas específicos", "next": "implication"},
                {"stage": "implication", "prompt": "Explore as implicações dos problemas", "next": "need_payoff"},
                {"stage": "need_payoff", "prompt": "Apresente os benefícios da solução", "next": "close"}
            ],
            situation_prompts=[
                "Qual é a situação atual da sua empresa?",
                "Como você está lidando com esse desafio atualmente?",
                "Há quanto tempo vocês enfrentam essa questão?"
            ],
            problem_prompts=[
                "Quais são os principais problemas que isso causa?",
                "Como isso afeta sua operação diária?",
                "Qual é o impacto no seu negócio?"
            ],
            implication_prompts=[
                "O que pode acontecer se isso não for resolvido?", 
                "Como isso pode afetar seus resultados futuros?",
                "Quais são os riscos de manter a situação atual?"
            ],
            need_payoff_prompts=[
                "Como seria se vocês resolvessem esse problema?",
                "Qual seria o valor de uma solução efetiva?",
                "O que significaria ter isso funcionando perfeitamente?"
            ]
        )
        db.add(default_playbook)
        await db.commit()
    
    # Check webhook status if not already set
    if not hasattr(client, 'has_webhook_configured'):
        client.has_webhook_configured = False
        
    return ClientResponse.model_validate(client)

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing client
    
    Parameters:
    - register_webhook: If True, automatically registers webhook for Evolution instance
      after client update (optional)
    """
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update fields
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(client, field):
            setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)

    # Register webhook if requested
    if client_data.register_webhook and client.evolution_instance:
        try:
            await configure_client_webhook(client.id, db)
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Error registering webhook: {str(e)}")

    # Check webhook status if not already set
    if not hasattr(client, 'has_webhook_configured'):
        client.has_webhook_configured = False
        
    return ClientResponse.model_validate(client)

@router.delete("/{client_id}")
async def delete_client(client_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a client"""
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    await db.delete(client)
    await db.commit()
    
    return {"message": "Client deleted successfully"}

@router.post("/{client_id}/webhook")
async def configure_client_webhook(
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Configure webhook for a client's Evolution instance"""
    from src.core.evolution_integration import evolution_service
    from src.config.settings import settings
    
    # Get client from database
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if not client.evolution_instance:
        raise HTTPException(
            status_code=400,
            detail="Client does not have an Evolution instance configured"
        )
    
    try:
        # Get Evolution client
        evolution_client = evolution_service.get_client(
            client.evolution_api_url,
            client.evolution_api_key
        )
        
        # Configure webhook
        webhook_url = f"{settings.WEBHOOK_BASE_URL}/webhook/whatsapp/{client_id}"
        result = await evolution_client.configure_webhook(
            instance_name=client.evolution_instance,
            webhook_url=webhook_url,
            events=["MESSAGE_UPSERT", "CONNECTION_UPDATE"]
        )
        
        # Update client webhook status
        client.has_webhook_configured = True
        await db.commit()
        await db.refresh(client)
        
        return {
            "status": "success",
            "webhook_url": webhook_url,
            "instance": client.evolution_instance,
            "result": result
        }
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error configuring webhook with Evolution API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )