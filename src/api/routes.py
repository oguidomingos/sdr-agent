from fastapi import APIRouter, HTTPException, Header, Request, Response
from typing import Dict, Any, Optional
import json
from pydantic import ValidationError

from src.types.schemas import WebhookData, Message, WhatsAppMessage, GeminiRequest, MessageDirection
from src.core.message import MessageHandler
from src.core.session import SessionManager
from src.core.gemini import GeminiClient
from src.core.whatsapp import WhatsAppSender
from src.core.batch_processor import BatchProcessor, MessageBatch
from src.config.settings import settings

# Inicializa o router
router = APIRouter()

# Inicializa os componentes principais
message_handler = MessageHandler()
session_manager = SessionManager()
gemini_client = GeminiClient()
whatsapp_sender = WhatsAppSender()
batch_processor = BatchProcessor(batch_window_seconds=180)  # 3 minutos


# Função callback para processar lotes de mensagens
async def process_message_batch(user_id: str, batch: MessageBatch) -> None:
    """
    Processa um lote de mensagens agrupadas na janela de tempo
    """
    try:
        print(f"🔄 Processando lote para {user_id} com {len(batch.messages)} mensagens")
        
        # Recupera a sessão existente
        current_session = await session_manager.get_session(user_id)
        
        # Pega a mensagem mais recente para obter metadados
        latest_message = batch.get_latest_message()
        if not latest_message:
            return
        
        # Combina todas as mensagens do usuário em uma única string
        combined_content = batch.get_combined_content()
        print(f"📝 Conteúdo combinado: {combined_content[:200]}...")
        
        # Cria uma mensagem única com todo o conteúdo
        combined_message = Message(
            user_id=user_id,
            user_name=latest_message.user_name,
            message_direction=MessageDirection.INBOUND,
            content=combined_content,
            metadata=batch.metadata
        )
        
        # Atualiza a sessão com a mensagem combinada
        session = await session_manager.update_session(
            user_id=user_id,
            message=combined_message,
            metadata={
                "name": latest_message.user_name,
                "instance": batch.metadata.get("instance", "default"),
                "batch_size": len(batch.messages)
            }
        )
        
        # Processa a mensagem combinada com o Gemini
        print(f"🤖 Enviando mensagem combinada para o Gemini...")
        response = await gemini_client.process_session(
            session=session,
            user_message=combined_content
        )
        
        if not response:
            print(f"❌ Erro: Resposta do Gemini é None")
            return
        
        # Atualiza a sessão com a resposta
        bot_message = Message(
            user_id=user_id,
            user_name="ROI Gem",
            message_direction=MessageDirection.OUTBOUND,
            content=response.content,
            metadata={"from_me": True, "batch_response": True}
        )
        await session_manager.update_session(
            user_id=user_id,
            message=bot_message
        )
        
        # Envia resposta do Gemini
        print(f"📤 Enviando resposta do lote...")
        message_parts = whatsapp_sender._split_message(response.content)
        print(f"📝 Resposta dividida em {len(message_parts)} partes")
        
        for i, part in enumerate(message_parts):
            print(f"📤 Enviando parte {i+1}/{len(message_parts)}")
            whatsapp_message = WhatsAppMessage(
                number=user_id,
                message=part,
                metadata={"instance": batch.metadata.get("instance", "default")}
            )
            
            typing_duration = (
                5 if len(part) < 50 else
                7 if len(part) < 200 else
                10
            )
            
            await whatsapp_sender.send_message(
                message=whatsapp_message,
                typing_duration=typing_duration,
                cooldown=2
            )
        
        print(f"✅ Lote processado com sucesso para {user_id}")
        
    except Exception as e:
        print(f"❌ Erro ao processar lote para {user_id}: {e}")


# Registra o callback no batch processor
batch_processor.add_processing_callback(process_message_batch)


# Middleware será movido para o main.py


@router.post("/webhook/whatsapp")
async def handle_webhook(
    request: Request,
    x_hub_signature: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Endpoint principal para receber webhooks da Evolution API
    Agora com sistema de batch processing para agrupar mensagens
    """
    try:
        print(f"🚀 Iniciando processamento do webhook...")
        # Extrai os dados do webhook
        webhook_data = await request.json()
        print(f"📦 Dados recebidos: {webhook_data.get('type', 'unknown')}")
        
        # Extrai dados da mensagem
        sender_number = webhook_data["data"]["key"]["remoteJid"]
        user_message = webhook_data["data"]["message"].get("conversation", "")
        push_name = webhook_data["data"]["pushName"]
        instance = webhook_data.get("instance", "default")
        
        print(f"📱 {push_name} ({sender_number}): {user_message}")

        # Recupera a sessão existente
        current_session = await session_manager.get_session(sender_number)
        
        # Cria mensagem do usuário
        message = Message(
            user_id=sender_number,
            user_name=push_name,
            message_direction=MessageDirection.INBOUND,
            content=user_message,
            metadata={
                "from_me": False,
                "instance": instance
            }
        )
        
        # Se for primeira mensagem, envia saudação e processa imediatamente
        if not current_session:
            print(f"👋 Primeira mensagem de {push_name}! Enviando saudação...")
            
            # Atualiza a sessão
            await session_manager.update_session(
                user_id=sender_number,
                message=message,
                metadata={
                    "name": push_name,
                    "instance": instance
                }
            )
            
            # Envia saudação
            await message_handler.send_greeting(
                user_id=sender_number,
                name=push_name,
                instance=instance
            )
            
            return {"status": "greeting_sent"}
        
        # Para mensagens subsequentes, adiciona ao batch processor
        print(f"📦 Adicionando mensagem ao lote de processamento...")
        was_batched = await batch_processor.add_message(message)
        
        if was_batched:
            # Também atualiza a sessão imediatamente para manter histórico
            await session_manager.update_session(
                user_id=sender_number,
                message=message,
                metadata={
                    "name": push_name,
                    "instance": instance
                }
            )
            
            # Verifica status do lote
            batch_status = await batch_processor.get_batch_status(sender_number)
            print(f"📊 Status do lote: {batch_status}")
            
            return {
                "status": "message_batched",
                "batch_info": {
                    "message_count": batch_status.get("message_count", 0) if batch_status else 0,
                    "window_seconds": 180
                }
            }
        else:
            # Fallback: se não foi possível fazer batch, processa imediatamente
            print(f"⚠️ Mensagem não foi adicionada ao lote, processando imediatamente...")
            return await _process_single_message(sender_number, push_name, user_message, instance)
        
    except Exception as e:
        print(f"\n=== Error Processing Request ===")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e)}")
        print("=== End Error ===\n")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


async def _process_single_message(sender_number: str, push_name: str, user_message: str, instance: str) -> Dict[str, Any]:
    """
    Processa uma única mensagem (fallback para quando batch não funciona)
    """
    # Recupera sessão
    session = await session_manager.get_session(sender_number)
    
    # Processa com Gemini
    response = await gemini_client.process_session(
        session=session,
        user_message=user_message
    )
    
    if not response:
        raise HTTPException(status_code=500, detail="Erro ao gerar resposta")
    
    # Atualiza sessão com resposta
    bot_message = Message(
        user_id=sender_number,
        user_name="ROI Gem",
        message_direction=MessageDirection.OUTBOUND,
        content=response.content,
        metadata={"from_me": True}
    )
    await session_manager.update_session(
        user_id=sender_number,
        message=bot_message
    )
    
    # Envia resposta
    message_parts = whatsapp_sender._split_message(response.content)
    for part in message_parts:
        whatsapp_message = WhatsAppMessage(
            number=sender_number,
            message=part,
            metadata={"instance": instance}
        )
        await whatsapp_sender.send_message(message=whatsapp_message)
    
    return {"status": "success", "message": response.content}


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Endpoint para verificação de saúde da API
    """
    return {"status": "healthy"}


@router.get("/sessions/{user_id}")
async def get_session_data(user_id: str) -> Dict[str, Any]:
    """
    Endpoint para consultar dados de uma sessão
    """
    session = await session_manager.get_session(user_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )
    
    return {
        "user_id": session.user_id,
        "message_count": len(session.messages),
        "last_interaction": session.last_interaction.isoformat(),
        "metadata": session.metadata
    }


@router.delete("/sessions/{user_id}")
async def delete_session(user_id: str) -> Dict[str, str]:
    """
    Endpoint para deletar uma sessão
    """
    success = await session_manager.delete_session(user_id)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Erro ao deletar sessão"
        )
    
    return {"status": "deleted"}


@router.get("/batch/{user_id}")
async def get_batch_status(user_id: str) -> Dict[str, Any]:
    """
    Endpoint para consultar status de um lote ativo
    """
    batch_status = await batch_processor.get_batch_status(user_id)
    
    if not batch_status:
        raise HTTPException(
            status_code=404,
            detail="Lote não encontrado ou não ativo"
        )
    
    return batch_status


@router.post("/batch/{user_id}/process")
async def force_process_batch(user_id: str) -> Dict[str, Any]:
    """
    Endpoint para forçar o processamento imediato de um lote
    """
    was_processed = await batch_processor.force_process_batch(user_id)
    
    if not was_processed:
        raise HTTPException(
            status_code=404,
            detail="Lote não encontrado ou não ativo"
        )
    
    return {"status": "batch_processed", "user_id": user_id}