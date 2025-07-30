from fastapi import APIRouter, HTTPException, Header, Request, Response
from typing import Dict, Any, Optional
import json
from pydantic import ValidationError

from src.types.schemas import WebhookData, Message, WhatsAppMessage, GeminiRequest
from src.core.message import MessageHandler
from src.core.session import SessionManager
from src.core.gemini import GeminiClient
from src.core.whatsapp import WhatsAppSender
from src.config.settings import settings

# Inicializa o router
router = APIRouter()

# Inicializa os componentes principais
message_handler = MessageHandler()
session_manager = SessionManager()
gemini_client = GeminiClient()
whatsapp_sender = WhatsAppSender()


# Middleware será movido para o main.py


@router.post("/webhook/whatsapp")
async def handle_webhook(
    request: Request,
    x_hub_signature: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Endpoint principal para receber webhooks da Evolution API
    """
    try:
        print(f"🚀 Iniciando processamento do webhook...")
        # Extrai os dados do webhook
        webhook_data = await request.json()
        print(f"📦 Dados do webhook: {webhook_data}")
        
        # Extrai o número do remetente
        # Extrai dados da mensagem
        sender_number = webhook_data["data"]["key"]["remoteJid"]
        user_message = webhook_data["data"]["message"].get("conversation", "")
        push_name = webhook_data["data"]["pushName"]
        print(f"Número do remetente: {sender_number}")
        print(f"Nome do usuário: {push_name}")
        print(f"Mensagem recebida: {user_message}")

        # Recupera a sessão existente
        current_session = await session_manager.get_session(sender_number)
        print(f"📋 Sessão atual: {current_session}")
        
        # Cria mensagem do usuário
        message = Message(
            user_id=sender_number,
            user_name=push_name,
            message_direction=MessageDirection.INBOUND,
            content=user_message,
            metadata={
                "from_me": False,
                "instance": webhook_data.get("instance", "default")
            }
        )
        print(f"💬 Mensagem criada: {message}")
        
        # Atualiza a sessão com a nova mensagem
        session = await session_manager.update_session(
            user_id=sender_number,
            message=message,
            metadata={
                "name": push_name,
                "instance": webhook_data.get("instance", "default")
            }
        )
        print(f"📝 Sessão atualizada: {session}")

        # Se for primeira mensagem, envia saudação
        print(f"🔍 Verificando se é primeira mensagem: current_session = {current_session}")
        if not current_session:
            print(f"👋 É primeira mensagem! Enviando saudação...")
            await message_handler.send_greeting(
                user_id=sender_number,
                name=push_name,
                instance=webhook_data.get("instance", "default")
            )
            return {"status": "greeting_sent"}
        else:
            print(f"🔄 Não é primeira mensagem, continuando processamento...")

        # Processa a mensagem com o Gemini
        print(f"🔄 Processando mensagem com Gemini...")
        response = await gemini_client.process_session(
            session=session,
            user_message=user_message
        )

        print(f"📝 Resposta do Gemini: {response}")
        
        if not response:
            print(f"❌ Erro: Resposta do Gemini é None")
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar resposta"
            )

        # Atualiza a sessão com a resposta
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

        # Se for primeira mensagem do usuário, envia saudação
        session_messages = await session_manager.get_session_messages(sender_number)
        print(f"📊 Mensagens na sessão: {len(session_messages)}")
        
        if len(session_messages) <= 2:  # Considera primeira mensagem + resposta
            print(f"👋 Enviando saudação...")
            await message_handler.send_greeting(sender_number, push_name)
        else:
            # Envia resposta do Gemini em partes se necessário
            print(f"📤 Enviando resposta do Gemini...")
            message_parts = whatsapp_sender._split_message(response.content)
            print(f"📝 Partes da mensagem: {len(message_parts)}")
            
            for i, part in enumerate(message_parts):
                print(f"📤 Enviando parte {i+1}/{len(message_parts)}: {part[:50]}...")
                whatsapp_message = WhatsAppMessage(
                    number=sender_number,
                    message=part,
                    metadata={"instance": webhook_data.get("instance", "default")}
                )
                typing_duration = (
                    5 if len(part) < 50 else
                    7 if len(part) < 200 else
                    10
                )
                result = await whatsapp_sender.send_message(
                    message=whatsapp_message,
                    typing_duration=typing_duration,
                    cooldown=2  # 2 segundos entre partes
                )
                print(f"✅ Resultado do envio: {result}")
        
        return {
            "status": "success",
            "message": response.content
        }
        
    except Exception as e:
        print(f"\n=== Error Processing Request ===")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e)}")
        print("=== End Error ===\n")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


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