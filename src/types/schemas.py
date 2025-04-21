from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WebhookData(BaseModel):
    """
    Modelo para dados recebidos do webhook da Evolution API
    """
    instance: str
    type: str
    data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "instance": "teste",
                "type": "Message_Upsert",
                "data": {
                    "key": {
                        "remoteJid": "5511999999999@s.whatsapp.net",
                        "fromMe": False,
                    },
                    "pushName": "João Silva",
                    "message": {
                        "conversation": "Olá, gostaria de mais informações"
                    }
                }
            }
        }


class Message(BaseModel):
    """
    Modelo para mensagens processadas
    """
    user_id: str = Field(..., description="ID do usuário (número do WhatsApp)")
    user_name: str = Field(..., description="Nome do usuário")
    content: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class SessionContext(BaseModel):
    """
    Modelo para contexto da sessão
    """
    user_id: str
    messages: List[Message] = Field(default_factory=list)
    last_interaction: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "5511999999999",
                "messages": [
                    {
                        "user_id": "5511999999999",
                        "user_name": "João Silva",
                        "content": "Olá, gostaria de mais informações",
                        "timestamp": "2024-04-18T11:53:40",
                        "metadata": {}
                    }
                ],
                "last_interaction": "2024-04-18T11:53:40",
                "metadata": {
                    "stage": "initial_contact",
                    "interests": ["marketing_digital"]
                }
            }
        }


class GeminiRequest(BaseModel):
    """
    Modelo para requisições à API do Gemini
    """
    prompt: str
    context: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default=None)


class GeminiResponse(BaseModel):
    """
    Modelo para respostas da API do Gemini
    """
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class WhatsAppMessage(BaseModel):
    """
    Modelo para mensagens enviadas via WhatsApp
    """
    number: str = Field(..., description="Número do destinatário")
    message: str = Field(..., description="Conteúdo da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "number": "5511999999999",
                "message": "Olá! Como posso ajudar?",
                "metadata": {
                    "message_type": "text",
                    "priority": "normal"
                }
            }
        }