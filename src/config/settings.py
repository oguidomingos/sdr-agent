from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Multi-client SaaS configuration using Pydantic BaseSettings.
    Loads environment variables with support for dynamic client configurations.
    """
    
    # Application Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str
    WEBHOOK_SECRET: str
    JWT_SECRET: str
    JWT_EXPIRATION_HOURS: int = 24
    
    # Database Configuration (PostgreSQL)
    POSTGRES_DB: str = "sdr_agent"
    POSTGRES_USER: str = "sdr_user"
    POSTGRES_PASSWORD: str = "sdr_password"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Session Management
    SESSION_TIMEOUT: int = 3600
    CONTEXT_WINDOW_SIZE: int = 20
    MAX_HISTORY_MESSAGES: int = 100
    
    # AI Configuration (Default/Fallback)
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash"
    DEFAULT_AI_TEMPERATURE: float = 0.7
    DEFAULT_AI_MAX_TOKENS: int = 1000
    
    # WhatsApp Integration (Default/Fallback)
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    DEFAULT_EVOLUTION_INSTANCE: str = "default"
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 3600
    RATE_LIMIT_ENABLED: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "/app/logs/sdr-agent.log"
    LOG_ROTATION_SIZE: str = "10MB"
    LOG_RETENTION_DAYS: int = 30
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    CORS_CREDENTIALS: bool = True
    
    # File Upload Settings
    MAX_FILE_SIZE: str = "10MB"
    ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,image/gif,application/pdf,text/plain"
    
    # Webhook Configuration
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_ATTEMPTS: int = 3
    WEBHOOK_RETRY_DELAY: int = 5
    
    # Multi-Tenant Features
    DEFAULT_CLIENT_NAME: str = "Demo Client"
    DEFAULT_CLIENT_DOMAIN: str = "demo.sdr-agent.com"
    ENABLE_CLIENT_SIGNUP: bool = False
    REQUIRE_CLIENT_APPROVAL: bool = True
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = 100
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Monitoring & Analytics
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    ANALYTICS_RETENTION_DAYS: int = 90
    
    # Email Configuration (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_NAME: str = "SDR Agent"
    SMTP_FROM_EMAIL: str = "noreply@sdr-agent.com"
    
    # External Integrations (Optional)
    CALENDAR_PROVIDER: Optional[str] = None
    GOOGLE_CALENDAR_CREDENTIALS_PATH: Optional[str] = None
    CRM_INTEGRATION_ENABLED: bool = False
    CRM_WEBHOOK_URL: Optional[str] = None
    
    # Development/Testing
    MOCK_WHATSAPP_RESPONSES: bool = False
    ENABLE_TEST_ENDPOINTS: bool = False
    SEED_DATABASE: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property 
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Convert file types string to list"""
        return [file_type.strip() for file_type in self.ALLOWED_FILE_TYPES.split(",") if file_type.strip()]

    @property
    def session_config(self) -> Dict[str, Any]:
        """Legacy session configuration for compatibility"""
        return {
            "enabled": True,
            "timeout": self.SESSION_TIMEOUT,
            "max_history": self.MAX_HISTORY_MESSAGES
        }

    @property
    def message_config(self) -> Dict[str, Any]:
        """Message configuration for typing effects and delays"""
        return {
            "typing_effect": {
                "short": 5,   # 5 seconds for short messages
                "medium": 7,  # 7 seconds for medium messages  
                "long": 10    # 10 seconds for long messages
            },
            "cooldown": 2  # interval between messages
        }


class ClientSettings:
    """
    Dynamic client-specific settings that override global defaults.
    This class is used to manage per-client configurations.
    """
    
    def __init__(self, client_data: Dict[str, Any], global_settings: Settings):
        self.global_settings = global_settings
        self.client_data = client_data
        
    @property
    def client_id(self) -> str:
        return self.client_data.get("id", "")
        
    @property
    def name(self) -> str:
        return self.client_data.get("name", self.global_settings.DEFAULT_CLIENT_NAME)
        
    @property
    def domain(self) -> str:
        return self.client_data.get("domain", self.global_settings.DEFAULT_CLIENT_DOMAIN)
        
    @property 
    def evolution_api_url(self) -> str:
        return self.client_data.get("evolution_api_url") or self.global_settings.EVOLUTION_API_URL
        
    @property
    def evolution_api_key(self) -> str:
        return self.client_data.get("evolution_api_key") or self.global_settings.EVOLUTION_API_KEY
        
    @property
    def evolution_instance(self) -> str:
        return self.client_data.get("evolution_instance") or self.global_settings.DEFAULT_EVOLUTION_INSTANCE
        
    @property
    def gemini_api_key(self) -> str:
        return self.client_data.get("gemini_api_key") or self.global_settings.GEMINI_API_KEY
        
    @property
    def gemini_model(self) -> str:
        return self.client_data.get("gemini_model") or self.global_settings.GEMINI_MODEL
        
    @property
    def session_timeout(self) -> int:
        return self.client_data.get("session_timeout") or self.global_settings.SESSION_TIMEOUT
        
    @property
    def max_history(self) -> int:
        return self.client_data.get("max_history") or self.global_settings.MAX_HISTORY_MESSAGES
        
    @property
    def context_window_size(self) -> int:
        return self.client_data.get("context_window_size") or self.global_settings.CONTEXT_WINDOW_SIZE
        
    @property
    def agent_name(self) -> str:
        return self.client_data.get("agent_name", "SDR Assistant")
        
    @property
    def agent_persona(self) -> str:
        return self.client_data.get("agent_persona", "")
        
    @property
    def welcome_message(self) -> str:
        return self.client_data.get("welcome_message", "Olá! Como posso ajudá-lo?")
        
    @property
    def ai_temperature(self) -> float:
        # Convert from 0-100 scale to 0-1 scale
        temp_scale = self.client_data.get("ai_temperature", 70)
        return temp_scale / 100.0
        
    @property
    def rate_limit_enabled(self) -> bool:
        return self.client_data.get("rate_limit_enabled", True)
        
    @property
    def rate_limit_calls(self) -> int:
        return self.client_data.get("rate_limit_calls") or self.global_settings.RATE_LIMIT_CALLS
        
    @property
    def rate_limit_period(self) -> int:
        return self.client_data.get("rate_limit_period") or self.global_settings.RATE_LIMIT_PERIOD
        
    @property
    def business_hours(self) -> Dict[str, Any]:
        return self.client_data.get("business_hours", {})
        
    @property
    def timezone(self) -> str:
        return self.client_data.get("timezone", "UTC")


@lru_cache()
def get_settings() -> Settings:
    """Get cached global settings instance"""
    return Settings()


# Global settings instance for backward compatibility
settings = get_settings()