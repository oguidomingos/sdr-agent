from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from src.core.db import get_db, User, Client, AgentConfig, UserStatus
from src.core.auth import auth_service, get_current_active_user, create_user_token
from src.core.evolution_integration import evolution_service
from src.types.auth_schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    ClientCreateRequest, ClientResponse, 
    AgentConfigCreate, AgentConfigResponse, AgentConfigUpdate
)
from src.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
client_router = APIRouter(prefix="/clients", tags=["Clients"], dependencies=[Depends(get_current_active_user)])

# ================== AUTH ROUTES ==================

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import logging

from src.core.db import get_db, User, Client, AgentConfig, UserStatus
from src.core.auth import auth_service, get_current_active_user, create_user_token
from src.core.evolution_integration import evolution_service
from src.types.auth_schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    ClientCreateRequest, ClientResponse,
    AgentConfigCreate, AgentConfigResponse, AgentConfigUpdate
)
from src.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
client_router = APIRouter(prefix="/clients", tags=["Clients"], dependencies=[Depends(get_current_active_user)])

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== AUTH ROUTES ==================

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra um novo usuário no sistema
    """
    logger.info(f"Tentativa de registro do usuário: {user_data.email}")
    try:
        user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            timezone=user_data.timezone,
            language=user_data.language
        )
        
        logger.info(f"Usuário registrado com sucesso: {user.email}")
        return UserResponse.model_validate(user)
        
    except HTTPException as http_exception:
        logger.error(f"Erro HTTP ao registrar usuário: {http_exception.detail}")
        raise
    except Exception as e:
        logger.exception(f"Erro ao registrar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Autentica usuário e retorna token JWT
    """
    logger.info(f"Tentativa de login do usuário: {user_credentials.email}")
    user = await auth_service.authenticate_user(
        db, user_credentials.email, user_credentials.password
    )
    
    if not user:
        logger.warning(f"Falha no login: usuário não encontrado ou senha incorreta para {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != UserStatus.ACTIVE:
        logger.warning(f"Falha no login: conta inativa para {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Atualiza último login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    token_data = create_user_token(user)
    logger.info(f"Usuário logado com sucesso: {user.email}")
    return Token(**token_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna informações do usuário atual
    """
    return UserResponse.model_validate(current_user)

# ================== CLIENT ROUTES ==================

@client_router.get("/")
async def list_user_clients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os clientes do usuário atual
    """
    # Get total count
    from sqlalchemy import func
    count_stmt = select(func.count(Client.id)).where(Client.owner_id == current_user.id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # Get clients with pagination
    result = await db.execute(
        select(Client)
        .where(Client.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Client.created_at.desc())
    )
    clients = result.scalars().all()
    
    # Adiciona flag de token Evolution
    client_responses = []
    for client in clients:
        client_data = ClientResponse.model_validate(client)
        client_data.has_evolution_token = bool(client.evolution_instance_token)
        client_responses.append(client_data)
    
    return {
        "clients": client_responses,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@client_router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria um novo cliente com integração automática Evolution API
    """
    # Verifica limite de clientes do usuário
    existing_clients = await db.execute(
        select(Client).where(Client.owner_id == current_user.id)
    )
    client_count = len(existing_clients.scalars().all())
    
    if client_count >= current_user.max_clients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum number of clients reached ({current_user.max_clients})"
        )
    
    try:
        # Cria instância Evolution API
        print(f"🚀 Criando instância Evolution para cliente: {client_data.name}")
        
        evolution_result = await evolution_service.setup_client_instance(
            client_id="temp",  # Será atualizado após criar o client
            client_name=client_data.name,
            whatsapp_number=client_data.whatsapp_number,
            evolution_url=client_data.evolution_api_url,
            evolution_key=client_data.evolution_api_key
        )
        
        # Cria cliente no banco
        client = Client(
            owner_id=current_user.id,
            name=client_data.name,
            description=client_data.description,
            domain=client_data.domain,
            
            # WhatsApp
            whatsapp_number=client_data.whatsapp_number,
            
            # Evolution API
            evolution_api_url=client_data.evolution_api_url,
            evolution_api_key=client_data.evolution_api_key,
            evolution_instance=evolution_result["instance_name"],
            evolution_instance_id=evolution_result["instance_id"],
            evolution_instance_token=evolution_result["instance_token"],
            
            # AI
            gemini_api_key=client_data.gemini_api_key,
            gemini_model=client_data.gemini_model,
            
            # Agent
            agent_name=client_data.agent_name,
            agent_prompt=client_data.agent_prompt,
            agent_persona=client_data.agent_persona,
            welcome_message=client_data.welcome_message,
            
            # Webhook
            webhook_secret=evolution_result["webhook_secret"],
            webhook_url=evolution_result["webhook_url"],
            
            # Business
            contact_email=client_data.contact_email,
            contact_phone=client_data.contact_phone,
            business_hours=client_data.business_hours,
            
            # AI Settings
            ai_temperature=client_data.ai_temperature
        )
        
        db.add(client)
        await db.commit()
        await db.refresh(client)
        
        # Atualiza webhook URL com client_id real
        if evolution_result.get("webhook_url"):
            webhook_url = evolution_result["webhook_url"].replace("/temp", f"/{client.id}")
            client.webhook_url = webhook_url
            await db.commit()
            
            # Também atualiza o webhook na Evolution API com a URL correta
            try:
                await evolution_service.update_webhook_url(
                    instance_name=client.evolution_instance,
                    webhook_url=webhook_url,
                    evolution_url=client.evolution_api_url,
                    evolution_key=client.evolution_api_key
                )
                print(f"✅ Webhook URL atualizada na Evolution API: {webhook_url}")
            except Exception as webhook_error:
                print(f"⚠️  Falha ao atualizar webhook na Evolution API: {webhook_error}")
                print(f"📝 Cliente criado com sucesso, mas webhook deve ser reconfigurado manualmente")
        
        # Marca se webhook foi configurado com sucesso
        webhook_configured = evolution_result.get("webhook_configured", False)
        if webhook_configured:
            print(f"✅ Webhook configurado com sucesso para cliente '{client.name}'")
        else:
            print(f"⚠️  Cliente '{client.name}' criado sem webhook - configurar manualmente se necessário")
        
        # Cria configuração padrão do agente
        default_config = AgentConfig(
            client_id=client.id,
            name="Configuração Padrão",
            system_prompt=client_data.agent_prompt or "Você é um assistente comercial especializado.",
            welcome_prompt=client_data.welcome_message or f"Olá! Sou o {client_data.agent_name}. Como posso ajudar?",
            temperature=client_data.ai_temperature,
            batch_enabled=client_data.batch_enabled,
            batch_window_seconds=client_data.batch_window_seconds,
            is_active=True
        )
        
        db.add(default_config)
        await db.commit()
        
        print(f"✅ Cliente '{client.name}' criado com sucesso!")
        print(f"📱 WhatsApp Instance: {client.evolution_instance}")
        print(f"🔗 Webhook URL: {client.webhook_url}")
        
        response = ClientResponse.model_validate(client)
        response.has_evolution_token = True
        
        return response
        
    except Exception as e:
        print(f"❌ Erro ao criar cliente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating client: {str(e)}"
        )

@client_router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna detalhes de um cliente específico
    """
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    response = ClientResponse.model_validate(client)
    response.has_evolution_token = bool(client.evolution_instance_token)
    
    return response

@client_router.get("/{client_id}/qr-code")
async def get_client_qr_code(
    client_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém QR Code para conectar WhatsApp do cliente
    """
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if not client.evolution_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client does not have Evolution instance configured"
        )
    
    try:
        qr_data = await evolution_service.get_client_qr_code(
            instance_name=client.evolution_instance,
            evolution_url=client.evolution_api_url,
            evolution_key=client.evolution_api_key
        )
        
        return {
            "client_id": client_id,
            "client_name": client.name,
            "whatsapp_number": client.whatsapp_number,
            "instance_name": client.evolution_instance,
            "qr_code": qr_data.get("base64"),
            "qr_code_url": qr_data.get("qrcode"),
            "status": qr_data.get("status"),
            "connection_state": qr_data.get("instance", {}).get("state")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting QR code: {str(e)}"
        )

@client_router.post("/{client_id}/connect-pairing")
async def connect_with_pairing_code(
    client_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Conecta WhatsApp usando código de pareamento
    """
    pairing_code = request.get("pairing_code")
    if not pairing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pairing code is required"
        )
    
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if not client.evolution_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client does not have Evolution instance configured"
        )
    
    try:
        connection_result = await evolution_service.connect_with_pairing_code(
            instance_name=client.evolution_instance,
            pairing_code=pairing_code,
            evolution_url=client.evolution_api_url,
            evolution_key=client.evolution_api_key
        )
        
        return {
            "client_id": client_id,
            "instance_name": client.evolution_instance,
            "whatsapp_number": client.whatsapp_number,
            "connection_result": connection_result,
            "status": "connecting"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting with pairing code: {str(e)}"
        )

@client_router.get("/{client_id}/status")
async def get_client_whatsapp_status(
    client_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica status da conexão WhatsApp do cliente
    """
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if not client.evolution_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client does not have Evolution instance configured"
        )
    
    try:
        status_data = await evolution_service.check_instance_status(
            instance_name=client.evolution_instance,
            evolution_url=client.evolution_api_url,
            evolution_key=client.evolution_api_key
        )
        
        return {
            "client_id": client_id,
            "client_name": client.name,
            "whatsapp_number": client.whatsapp_number,
            "instance_name": client.evolution_instance,
            "status": status_data,
            "is_connected": status_data.get("state") == "open"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking status: {str(e)}"
        )

@client_router.post("/{client_id}/reset-sessions")
async def reset_client_sessions(
    client_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reseta todas as sessões/mensagens de um cliente
    """
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    try:
        # Deleta todas as mensagens do cliente
        from src.core.db import Message
        delete_query = select(Message).where(Message.client_id == client_id)
        messages_result = await db.execute(delete_query)
        messages = messages_result.scalars().all()
        
        for message in messages:
            await db.delete(message)
        
        await db.commit()
        
        print(f"🗑️  Resetadas {len(messages)} mensagens do cliente {client.name}")
        
        return {
            "status": "sessions_reset", 
            "client_id": client_id,
            "messages_deleted": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting sessions: {str(e)}"
        )

@client_router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deleta um cliente e sua instância Evolution
    """
    result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    try:
        # Deleta instância Evolution se existir
        if client.evolution_instance:
            await evolution_service.delete_client_instance(
                instance_name=client.evolution_instance,
                evolution_url=client.evolution_api_url,
                evolution_key=client.evolution_api_key
            )
        
        # Deleta cliente do banco (cascade delete nas relacionadas)
        await db.delete(client)
        await db.commit()
        
        return {"status": "deleted", "client_id": client_id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting client: {str(e)}"
        )

# ================== AGENT CONFIG ROUTES ==================

@client_router.get("/{client_id}/agent-configs", response_model=List[AgentConfigResponse])
async def list_agent_configs(
    client_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista configurações do agente de um cliente
    """
    # Verifica se cliente pertence ao usuário
    client_result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Lista configurações
    result = await db.execute(
        select(AgentConfig).where(AgentConfig.client_id == client_id)
    )
    configs = result.scalars().all()
    
    return [AgentConfigResponse.model_validate(config) for config in configs]

@client_router.post("/{client_id}/agent-configs", response_model=AgentConfigResponse)
async def create_agent_config(
    client_id: str,
    config_data: AgentConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria nova configuração de agente
    """
    # Verifica se cliente pertence ao usuário
    client_result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Cria configuração
    config = AgentConfig(
        client_id=client_id,
        **config_data.model_dump()
    )
    
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    return AgentConfigResponse.model_validate(config)

@client_router.put("/{client_id}/agent-configs/{config_id}", response_model=AgentConfigResponse)
async def update_agent_config(
    client_id: str,
    config_id: str,
    config_data: AgentConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza configuração de agente
    """
    # Verifica se cliente pertence ao usuário
    client_result = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.owner_id == current_user.id
        )
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Busca configuração
    config_result = await db.execute(
        select(AgentConfig).where(
            AgentConfig.id == config_id,
            AgentConfig.client_id == client_id
        )
    )
    config = config_result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent config not found"
        )
    
    # Atualiza campos
    update_data = config_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    await db.commit()
    await db.refresh(config)
    
    return AgentConfigResponse.model_validate(config)