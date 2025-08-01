from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: str = "UTC"
    language: str = "pt-BR"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

class UserResponse(UserBase):
    id: str
    status: UserStatus
    plan: UserPlan
    max_clients: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

# Client Creation Schema (Enhanced)
class ClientCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: str = Field(..., min_length=1, max_length=255)
    
    # WhatsApp number (required for Evolution API instance)
    whatsapp_number: str = Field(..., min_length=10, max_length=20, description="Número do WhatsApp que será conectado (formato: +5511999999999)")
    
    # Evolution API credentials
    evolution_api_url: str = Field(..., min_length=1)
    evolution_api_key: str = Field(..., min_length=1)
    
    # Gemini API credentials
    gemini_api_key: str = Field(..., min_length=1)
    gemini_model: str = "gemini-2.0-flash"
    
    # Agent configuration
    agent_name: str = "Assistente"
    agent_prompt: Optional[str] = None
    agent_persona: Optional[str] = None
    welcome_message: Optional[str] = None
    
    # Business info
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[dict] = None
    
    # AI Settings
    ai_temperature: int = Field(70, ge=0, le=100)
    batch_enabled: bool = True
    batch_window_seconds: int = Field(180, ge=60, le=600)  # 1-10 minutos

class ClientResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str]
    domain: str
    status: str
    
    # WhatsApp info
    whatsapp_number: Optional[str]
    
    # Evolution API info (sem expor tokens)
    evolution_api_url: Optional[str]
    evolution_instance: Optional[str]
    evolution_instance_id: Optional[str]
    has_evolution_token: bool = False  # Apenas indica se tem token
    
    # Agent info
    agent_name: str
    agent_persona: Optional[str]
    welcome_message: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Agent Config Schemas
class AgentConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    system_prompt: Optional[str] = None
    welcome_prompt: Optional[str] = None
    fallback_prompt: Optional[str] = None
    
    # AI Parameters
    temperature: int = Field(70, ge=0, le=100)
    max_tokens: int = Field(1000, ge=100, le=4000)
    top_p: int = Field(95, ge=0, le=100)
    
    # Batch config
    batch_enabled: bool = True
    batch_window_seconds: int = Field(180, ge=60, le=600)

class AgentConfigCreate(AgentConfigBase):
    pass

class AgentConfigUpdate(BaseModel):
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    welcome_prompt: Optional[str] = None
    fallback_prompt: Optional[str] = None
    temperature: Optional[int] = Field(None, ge=0, le=100)
    max_tokens: Optional[int] = Field(None, ge=100, le=4000)
    top_p: Optional[int] = Field(None, ge=0, le=100)
    batch_enabled: Optional[bool] = None
    batch_window_seconds: Optional[int] = Field(None, ge=60, le=600)
    is_active: Optional[bool] = None

class AgentConfigResponse(AgentConfigBase):
    id: str
    client_id: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Evolution API Integration Schemas
class EvolutionInstanceCreate(BaseModel):
    instanceName: str
    token: Optional[str] = None
    qrcode: bool = True
    webhook: Optional[str] = None
    webhook_by_events: bool = False
    events: Optional[List[str]] = None

class EvolutionInstanceResponse(BaseModel):
    instance: dict
    hash: Optional[str] = None
    webhook: Optional[str] = None
    events: Optional[List[str]] = None