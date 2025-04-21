from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic BaseSettings.
    Carrega automaticamente variáveis de ambiente ou arquivo .env
    """
    # API Keys e Endpoints
    GEMINI_API_KEY: str
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: Optional[str] = None
    
    # Configurações do Redis
    REDIS_HOST: str = "redis"  # Nome do serviço no docker-compose
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Configurações do Webhook
    WEBHOOK_SECRET: str
    WEBHOOK_PATH: str = "/webhook"
    
    # Configurações da Sessão
    SESSION_TIMEOUT: int = 86400  # 24 horas em segundos
    CONTEXT_WINDOW_SIZE: int = 20  # Número de mensagens mantidas no contexto
    
    # Configurações do Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    GEMINI_MODEL: str = "gemini-2.0-flash"  # Modelo mais adequado para chat
    
    # Configurações de Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hora em segundos

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def redis_url(self) -> str:
        """
        Constrói a URL de conexão do Redis
        """
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Instância global das configurações
settings = Settings()