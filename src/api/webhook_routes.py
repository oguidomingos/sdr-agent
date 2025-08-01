from fastapi import APIRouter, HTTPException, Header, Request, Response, Depends
from typing import Dict, Any, Optional
import json
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.types.schemas import WebhookData, Message, WhatsAppMessage, MessageDirection
from src.core.message import MessageHandler
from src.core.session import SessionManager
from src.core.gemini import GeminiClient
from src.core.whatsapp import WhatsAppSender
from src.core.batch_processor import BatchProcessor, MessageBatch
from src.core.db import get_db, Client, AgentConfig
from src.config.settings import settings

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

# Caches para componentes por cliente
client_components_cache = {}

class MultiTenantComponents:
    """
    Componentes isolados por cliente
    """
    def __init__(self, client: Client, agent_config: AgentConfig):
        self.client = client
        self.agent_config = agent_config
        
        # Inicializa componentes com configurações do cliente
        self.message_handler = MessageHandler()
        self.session_manager = SessionManager()
        
        # Gemini com configurações específicas do cliente
        self.gemini_client = GeminiClient(
            api_key=client.gemini_api_key,
            model=client.gemini_model
        )
        
        # WhatsApp com configurações específicas do cliente
        self.whatsapp_sender = WhatsAppSender(
            evolution_url=client.evolution_api_url,
            evolution_key=client.evolution_api_key,
            instance=client.evolution_instance
        )
        
        # Batch processor com configurações do agente
        self.batch_processor = BatchProcessor(
            batch_window_seconds=agent_config.batch_window_seconds
        ) if agent_config.batch_enabled else None
        
        # Registra callback do batch processor
        if self.batch_processor:
            self.batch_processor.add_processing_callback(self._process_message_batch)
    
    async def _process_message_batch(self, user_id: str, batch: MessageBatch) -> None:
        """
        Processa um lote de mensagens agrupadas na janela de tempo
        """
        try:
            print(f"🔄 [{self.client.name}] Processando lote para {user_id} com {len(batch.messages)} mensagens")
            
            # Recupera a sessão existente
            current_session = await self.session_manager.get_session(user_id, self.client.id)
            
            # Pega a mensagem mais recente para obter metadados
            latest_message = batch.get_latest_message()
            if not latest_message:
                return
            
            # Combina todas as mensagens do usuário em uma única string
            combined_content = batch.get_combined_content()
            print(f"📝 [{self.client.name}] Conteúdo combinado: {combined_content[:200]}...")
            
            # Cria uma mensagem única com todo o conteúdo
            combined_message = Message(
                user_id=user_id,
                user_name=latest_message.user_name,
                message_direction=MessageDirection.INBOUND,
                content=combined_content,
                metadata=batch.metadata
            )
            
            # Atualiza a sessão com a mensagem combinada
            session = await self.session_manager.update_session(
                user_id=user_id,
                client_id=self.client.id,
                message=combined_message,
                metadata={
                    "name": latest_message.user_name,
                    "instance": batch.metadata.get("instance", self.client.evolution_instance),
                    "batch_size": len(batch.messages)
                }
            )
            
            # Processa a mensagem combinada with Gemini usando prompt personalizado
            print(f"🤖 [{self.client.name}] Enviando mensagem combinada para o Gemini...")
            
            # Processa com Gemini usando configurações do cliente
            response = await self.gemini_client.process_session(
                session=session,
                user_message=combined_content,
                parameters={
                    "temperature": self.agent_config.temperature / 100.0,  # Convert to 0-1 scale
                    "max_tokens": self.agent_config.max_tokens,
                    "system_prompt": self.agent_config.system_prompt or "Você é um assistente comercial especializado.",
                    "welcome_prompt": self.agent_config.welcome_prompt or self.client.welcome_message or "Olá! Como posso ajudá-lo hoje?"
                }
            )
            
            if not response:
                print(f"❌ [{self.client.name}] Erro: Resposta do Gemini é None")
                return
            
            # Atualiza a sessão com a resposta
            bot_message = Message(
                user_id=user_id,
                user_name=self.client.agent_name,
                message_direction=MessageDirection.OUTBOUND,
                content=response.content,
                metadata={"from_me": True, "batch_response": True}
            )
            await self.session_manager.update_session(
                user_id=user_id,
                client_id=self.client.id,
                message=bot_message
            )
            
            # Envia resposta do Gemini
            print(f"📤 [{self.client.name}] Enviando resposta do lote...")
            message_parts = self.whatsapp_sender._split_message(response.content)
            print(f"📝 [{self.client.name}] Resposta dividida em {len(message_parts)} partes")
            
            for i, part in enumerate(message_parts):
                print(f"📤 [{self.client.name}] Enviando parte {i+1}/{len(message_parts)}")
                whatsapp_message = WhatsAppMessage(
                    number=user_id,
                    message=part,
                    metadata={"instance": self.client.evolution_instance}
                )
                
                typing_duration = (
                    5 if len(part) < 50 else
                    7 if len(part) < 200 else
                    10
                )
                
                await self.whatsapp_sender.send_message(
                    message=whatsapp_message,
                    typing_duration=typing_duration,
                    cooldown=2
                )
            
            print(f"✅ [{self.client.name}] Lote processado com sucesso para {user_id}")
            
        except Exception as e:
            print(f"❌ [{self.client.name}] Erro ao processar lote para {user_id}: {e}")

async def get_client_components(client_id: str, db: AsyncSession) -> MultiTenantComponents:
    """
    Obtém ou cria componentes isolados para um cliente
    """
    # Verifica cache
    if client_id in client_components_cache:
        return client_components_cache[client_id]
    
    # Busca cliente e configuração ativa
    client_result = await db.execute(select(Client).where(Client.id == client_id))
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Busca configuração ativa do agente
    config_result = await db.execute(
        select(AgentConfig).where(
            AgentConfig.client_id == client_id,
            AgentConfig.is_active == True
        ).order_by(AgentConfig.created_at.desc())
    )
    agent_config = config_result.scalar_one_or_none()
    
    if not agent_config:
        raise HTTPException(status_code=400, detail="No active agent configuration found")
    
    # Cria e cacheia componentes
    components = MultiTenantComponents(client, agent_config)
    client_components_cache[client_id] = components
    
    return components

@router.post("/test/{client_id}")
async def test_webhook(client_id: str, request: Request):
    """Endpoint de teste para verificar se webhooks chegam"""
    body = await request.body()
    print(f"🧪 TEST WEBHOOK [{client_id}] RECEBIDO!")
    print(f"📦 Body: {body.decode('utf-8')}")
    return {"status": "test_received", "client_id": client_id}

@router.post("/whatsapp/{client_id}")
async def handle_client_webhook(
    client_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_hub_signature: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Endpoint de webhook específico para cada cliente
    Agora com sistema de batch processing e configurações isoladas
    """
    try:
        print(f"🚀 [{client_id}] WEBHOOK RECEBIDO! Iniciando processamento...")
        
        # Log da requisição completa para debug
        body = await request.body()
        print(f"📦 [{client_id}] Raw body: {body.decode('utf-8')[:500]}...")
        
        # Obtém componentes isolados do cliente
        components = await get_client_components(client_id, db)
        
        # Extrai os dados do webhook
        webhook_data = await request.json()
        print(f"📦 [{client_id}] Dados recebidos: {webhook_data.get('type', 'unknown')}")
        print(f"🔍 [{client_id}] Webhook data structure: {list(webhook_data.keys())}")
        
        # Tratamento robusto para diferentes formatos de webhook
        try:
            # Formato padrão da Evolution API
            if "data" in webhook_data and "key" in webhook_data["data"]:
                sender_number = webhook_data["data"]["key"]["remoteJid"]
                user_message = webhook_data["data"]["message"].get("conversation", "")
                push_name = webhook_data["data"].get("pushName", "Unknown")
            # Formato alternativo
            elif "key" in webhook_data:
                sender_number = webhook_data["key"]["remoteJid"]
                user_message = webhook_data["message"].get("conversation", "")
                push_name = webhook_data.get("pushName", "Unknown")
            else:
                print(f"❌ [{client_id}] Formato de webhook não reconhecido: {webhook_data}")
                return {"status": "error", "message": "Webhook format not recognized"}
            
            instance = webhook_data.get("instance", components.client.evolution_instance)
        except KeyError as e:
            print(f"❌ [{client_id}] Erro ao extrair dados do webhook: {e}")
            print(f"📋 [{client_id}] Webhook completo: {webhook_data}")
            return {"status": "error", "message": f"Missing required field: {e}"}
        
        print(f"📱 [{client_id}] {push_name} ({sender_number}): {user_message}")

        # Recupera a sessão existente
        current_session = await components.session_manager.get_session(sender_number, client_id)
        
        # Cria mensagem do usuário
        message = Message(
            user_id=sender_number,
            user_name=push_name,
            message_direction=MessageDirection.INBOUND,
            content=user_message,
            metadata={
                "from_me": False,
                "instance": instance,
                "client_id": client_id
            }
        )
        
        # Se for primeira mensagem, envia saudação e processa imediatamente
        if not current_session:
            print(f"👋 [{client_id}] Primeira mensagem de {push_name}! Enviando saudação...")
            
            # Atualiza a sessão
            await components.session_manager.update_session(
                user_id=sender_number,
                client_id=client_id,
                message=message,
                metadata={
                    "name": push_name,
                    "instance": instance
                }
            )
            
            # Envia saudação personalizada do cliente
            welcome_message = (components.agent_config.welcome_prompt or 
                             components.client.welcome_message or 
                             f"Olá! Sou o {components.client.agent_name}. Como posso ajudar?")
            
            await components.message_handler.send_greeting(
                user_id=sender_number,
                name=push_name,
                instance=instance,
                custom_message=welcome_message
            )
            
            return {"status": "greeting_sent", "client_id": client_id}
        
        # Para mensagens subsequentes, verifica se batch está habilitado
        if components.batch_processor and components.agent_config.batch_enabled:
            print(f"📦 [{client_id}] Adicionando mensagem ao lote de processamento...")
            was_batched = await components.batch_processor.add_message(message)
            
            if was_batched:
                # Também atualiza a sessão imediatamente para manter histórico
                await components.session_manager.update_session(
                    user_id=sender_number,
                    client_id=client_id,
                    message=message,
                    metadata={
                        "name": push_name,
                        "instance": instance
                    }
                )
                
                # Verifica status do lote
                batch_status = await components.batch_processor.get_batch_status(sender_number)
                print(f"📊 [{client_id}] Status do lote: {batch_status}")
                
                return {
                    "status": "message_batched",
                    "client_id": client_id,
                    "batch_info": {
                        "message_count": batch_status.get("message_count", 0) if batch_status else 0,
                        "window_seconds": components.agent_config.batch_window_seconds
                    }
                }
        
        # Fallback: processa mensagem imediatamente (batch desabilitado ou falha)
        print(f"⚠️ [{client_id}] Processando mensagem imediatamente...")
        return await _process_single_message(
            components, sender_number, push_name, user_message, instance, client_id
        )
        
    except Exception as e:
        print(f"\n=== Error Processing Request for Client {client_id} ===")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e)}")
        print("=== End Error ===\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing webhook for client {client_id}: {str(e)}"
        )

async def _process_single_message(
    components: MultiTenantComponents,
    sender_number: str, 
    push_name: str, 
    user_message: str, 
    instance: str,
    client_id: str
) -> Dict[str, Any]:
    """
    Processa uma única mensagem (fallback ou quando batch está desabilitado)
    """
    # Recupera sessão
    session = await components.session_manager.get_session(sender_number, client_id)
    
    # Processa com Gemini usando configurações do cliente
    response = await components.gemini_client.process_session(
        session=session,
        user_message=user_message,
        parameters={
            "temperature": components.agent_config.temperature / 100.0,
            "max_tokens": components.agent_config.max_tokens,
            "system_prompt": components.agent_config.system_prompt or "Você é um assistente comercial especializado.",
            "welcome_prompt": components.agent_config.welcome_prompt or components.client.welcome_message or "Olá! Como posso ajudá-lo hoje?"
        }
    )
    
    if not response:
        raise HTTPException(status_code=500, detail="Erro ao gerar resposta")
    
    # Atualiza sessão com resposta
    bot_message = Message(
        user_id=sender_number,
        user_name=components.client.agent_name,
        message_direction=MessageDirection.OUTBOUND,
        content=response.content,
        metadata={"from_me": True, "client_id": client_id}
    )
    await components.session_manager.update_session(
        user_id=sender_number,
        client_id=client_id,
        message=bot_message
    )
    
    # Envia resposta
    message_parts = components.whatsapp_sender._split_message(response.content)
    for part in message_parts:
        whatsapp_message = WhatsAppMessage(
            number=sender_number,
            message=part,
            metadata={"instance": instance}
        )
        await components.whatsapp_sender.send_message(message=whatsapp_message)
    
    return {
        "status": "success", 
        "message": response.content, 
        "client_id": client_id
    }

# Endpoint para forçar processamento de lote (debug)
@router.post("/batch/{client_id}/{user_id}/process")
async def force_process_client_batch(
    client_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Força o processamento imediato de um lote específico do cliente
    """
    try:
        components = await get_client_components(client_id, db)
        
        if not components.batch_processor:
            raise HTTPException(
                status_code=400,
                detail="Batch processing not enabled for this client"
            )
        
        was_processed = await components.batch_processor.force_process_batch(user_id)
        
        if not was_processed:
            raise HTTPException(
                status_code=404,
                detail="Batch not found or not active"
            )
        
        return {
            "status": "batch_processed", 
            "client_id": client_id,
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing batch: {str(e)}"
        )

# Endpoint para verificar status de lote (debug)
@router.get("/batch/{client_id}/{user_id}")
async def get_client_batch_status(
    client_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica status de um lote ativo do cliente
    """
    try:
        components = await get_client_components(client_id, db)
        
        if not components.batch_processor:
            raise HTTPException(
                status_code=400,
                detail="Batch processing not enabled for this client"
            )
        
        batch_status = await components.batch_processor.get_batch_status(user_id)
        
        if not batch_status:
            raise HTTPException(
                status_code=404,
                detail="Batch not found or not active"
            )
        
        batch_status["client_id"] = client_id
        return batch_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting batch status: {str(e)}"
        )