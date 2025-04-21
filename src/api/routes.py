from fastapi import FastAPI, HTTPException, Header, Request, Response
from typing import Dict, Any, Optional
import json
from pydantic import ValidationError

from src.types.schemas import WebhookData, Message, WhatsAppMessage, GeminiRequest
from src.core.message import MessageHandler
from src.core.session import SessionManager
from src.core.gemini import GeminiClient
from src.core.whatsapp import WhatsAppSender
from src.config.settings import settings

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="SDR Agent API",
    description="API para processamento de mensagens do WhatsApp usando IA",
    version="1.0.0"
)

# Inicializa os componentes principais
message_handler = MessageHandler()
session_manager = SessionManager()
gemini_client = GeminiClient()
whatsapp_sender = WhatsAppSender()


# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logging de requisições
    """
    print(f"\n=== Incoming Request ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print("Headers:", dict(request.headers))
    
    # Log do corpo da requisição para debugging
    if request.method == "POST":
        body = await request.body()
        try:
            body_str = body.decode()
            print(f"Request body: {body_str}")
            # Recria o stream do body para o FastAPI
            request._body = body
        except Exception as e:
            print(f"Erro ao decodificar request body: {e}")
            
        # Salva o payload em um arquivo
        try:
            with open("last_payload.json", "w") as f:
                f.write(body_str)
        except Exception as e:
            print(f"Erro ao salvar payload em arquivo: {str(e)}")
    
    print("=== End Request ===\n")
    
    response = await call_next(request)
    return response


@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_hub_signature: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Endpoint principal para receber webhooks da Evolution API
    """
    try:
        # Extrai os dados do webhook
        webhook_data = await request.json()
        
        # Extrai o número do remetente
        # Extrai dados da mensagem
        sender_number = webhook_data["data"]["key"]["remoteJid"]
        user_message = webhook_data["data"]["message"].get("conversation", "")
        push_name = webhook_data["data"]["pushName"]
        print(f"Número do remetente: {sender_number}")
        print(f"Nome do usuário: {push_name}")
        print(f"Mensagem recebida: {user_message}")

        # Cria/atualiza a sessão
        message = Message(
            user_id=sender_number,
            user_name=push_name,
            content=user_message,
            metadata={"from_me": False}
        )
        session = await session_manager.update_session(
            user_id=sender_number,
            message=message,
            metadata={"name": push_name}
        )

        # Processa a mensagem com o Gemini
        response = await gemini_client.process_session(
            session=session,
            user_message=user_message
        )

        if not response:
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar resposta"
            )

        # Atualiza a sessão com a resposta
        bot_message = Message(
            user_id=sender_number,
            user_name="ROI Gem",
            content=response.content,
            metadata={"from_me": True}
        )
        await session_manager.update_session(
            user_id=sender_number,
            message=bot_message
        )

        # Envia a resposta para o WhatsApp
        whatsapp_message = WhatsAppMessage(
            number=sender_number,
            message=response.content
        )
        await whatsapp_sender.send_message(whatsapp_message)
        
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


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Endpoint para verificação de saúde da API
    """
    return {"status": "healthy"}


@app.get("/sessions/{user_id}")
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


@app.delete("/sessions/{user_id}")
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