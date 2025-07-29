from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import enum


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


# Client Management Schemas
class ClientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SUSPENDED = "suspended"
    TRIAL = "trial"


class PlaybookStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ClientCreate(BaseModel):
    """Schema for creating a new client"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: str = Field(..., min_length=1, max_length=255)
    
    # API Configuration
    evolution_api_url: Optional[str] = None
    evolution_api_key: Optional[str] = None
    evolution_instance: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    
    # Session Configuration
    session_timeout: Optional[int] = Field(None, gt=0)
    max_history: Optional[int] = Field(None, gt=0)
    context_window_size: Optional[int] = Field(None, gt=0)
    
    # Persona and Branding
    agent_name: Optional[str] = None
    agent_persona: Optional[str] = None
    welcome_message: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Business Information
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    
    # Settings
    ai_temperature: Optional[int] = Field(None, ge=0, le=100)
    rate_limit_enabled: Optional[bool] = None
    rate_limit_calls: Optional[int] = Field(None, gt=0)
    rate_limit_period: Optional[int] = Field(None, gt=0)
    
    # Additional options
    create_default_playbook: bool = True

    @validator('domain')
    def validate_domain(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Domain cannot be empty')
        return v.lower().strip()


class ClientUpdate(BaseModel):
    """Schema for updating an existing client"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[ClientStatus] = None
    
    # API Configuration
    evolution_api_url: Optional[str] = None
    evolution_api_key: Optional[str] = None
    evolution_instance: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    
    # Session Configuration
    session_timeout: Optional[int] = Field(None, gt=0)
    max_history: Optional[int] = Field(None, gt=0)
    context_window_size: Optional[int] = Field(None, gt=0)
    
    # Persona and Branding
    agent_name: Optional[str] = None
    agent_persona: Optional[str] = None
    welcome_message: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Business Information
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    
    # Settings
    ai_temperature: Optional[int] = Field(None, ge=0, le=100)
    rate_limit_enabled: Optional[bool] = None
    rate_limit_calls: Optional[int] = Field(None, gt=0)
    rate_limit_period: Optional[int] = Field(None, gt=0)

    @validator('domain')
    def validate_domain(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Domain cannot be empty')
        return v.lower().strip() if v else v


class ClientResponse(BaseModel):
    """Schema for client responses"""
    id: str
    name: str
    description: Optional[str]
    domain: str
    status: ClientStatus
    
    # API Configuration (exclude sensitive keys)
    evolution_api_url: Optional[str]
    evolution_instance: Optional[str]
    gemini_model: Optional[str]
    
    # Session Configuration
    session_timeout: int
    max_history: int
    context_window_size: int
    
    # Persona and Branding
    agent_name: str
    agent_persona: Optional[str]
    welcome_message: Optional[str]
    logo_url: Optional[str]
    
    # Business Information
    contact_email: Optional[str]
    contact_phone: Optional[str]
    business_hours: Optional[Dict[str, Any]]
    timezone: str
    
    # Settings
    ai_temperature: int
    rate_limit_enabled: bool
    rate_limit_calls: int
    rate_limit_period: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClientListResponse(BaseModel):
    """Schema for paginated client list responses"""
    clients: List[ClientResponse]
    total: int
    skip: int
    limit: int


# Playbook Management Schemas
class PlaybookCreate(BaseModel):
    """Schema for creating a new playbook"""
    client_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_default: bool = False
    
    # Conversation Flow
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    conditions: Optional[Dict[str, Any]] = None
    fallback_messages: Optional[List[str]] = None
    
    # SPIN Selling Configuration
    situation_prompts: Optional[List[str]] = None
    problem_prompts: Optional[List[str]] = None
    implication_prompts: Optional[List[str]] = None
    need_payoff_prompts: Optional[List[str]] = None


class PlaybookUpdate(BaseModel):
    """Schema for updating an existing playbook"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[PlaybookStatus] = None
    is_default: Optional[bool] = None
    
    # Conversation Flow
    steps: Optional[List[Dict[str, Any]]] = None
    conditions: Optional[Dict[str, Any]] = None
    fallback_messages: Optional[List[str]] = None
    
    # SPIN Selling Configuration
    situation_prompts: Optional[List[str]] = None
    problem_prompts: Optional[List[str]] = None
    implication_prompts: Optional[List[str]] = None
    need_payoff_prompts: Optional[List[str]] = None


class PlaybookResponse(BaseModel):
    """Schema for playbook responses"""
    id: str
    client_id: str
    name: str
    description: Optional[str]
    status: PlaybookStatus
    is_default: bool
    version: int
    
    # Conversation Flow
    steps: List[Dict[str, Any]]
    conditions: Optional[Dict[str, Any]]
    fallback_messages: Optional[List[str]]
    
    # SPIN Selling Configuration
    situation_prompts: Optional[List[str]]
    problem_prompts: Optional[List[str]]
    implication_prompts: Optional[List[str]]
    need_payoff_prompts: Optional[List[str]]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PlaybookListResponse(BaseModel):
    """Schema for paginated playbook list responses"""
    playbooks: List[PlaybookResponse]
    total: int
    skip: int
    limit: int


# Message and Conversation Schemas
class ConversationResponse(BaseModel):
    """Schema for conversation responses"""
    user_id: str
    user_name: Optional[str]
    client_id: str
    messages: List[Message]
    last_interaction: datetime
    message_count: int
    status: Optional[str]
    lead_score: int = 0
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list responses"""
    conversations: List[ConversationResponse]
    total: int
    skip: int
    limit: int


class MessageHistory(BaseModel):
    """Schema for message history responses"""
    id: str
    client_id: str
    user_id: str
    user_name: Optional[str]
    direction: str  # 'inbound' or 'outbound'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]
    status: Optional[str]
    conversation_stage: Optional[str]
    lead_score: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageHistoryResponse(BaseModel):
    """Schema for paginated message history responses"""
    messages: List[MessageHistory]
    total: int
    skip: int
    limit: int