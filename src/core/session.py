from typing import Optional, List
from datetime import datetime
import json
import redis
import uuid
from sqlalchemy import select

from src.types.schemas import Message, SessionContext
from src.config.settings import settings, ClientSettings
from src.core.db import AsyncSessionLocal, Message as DBMessage, MessageDirection, Client


class SessionManager:
    """
    Multi-client session manager with proper tenant isolation.
    Manages conversation state and context with client-specific configurations.
    """
    
    def __init__(self, client_settings: Optional[ClientSettings] = None):
        self.redis = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
        self.client_settings = client_settings

    def _get_session_key(self, user_id: str, client_id: Optional[str] = None) -> str:
        """
        Generate Redis key for user session with client isolation.
        Format: session:{client_id}:{user_id}
        """
        if client_id:
            return f"session:{client_id}:{user_id}"
        elif self.client_settings:
            return f"session:{self.client_settings.client_id}:{user_id}"
        else:
            # Fallback to old format for backward compatibility
            return f"session:{user_id}"
    
    async def _get_client_settings(self, client_id: str) -> Optional[ClientSettings]:
        """Load client settings from database"""
        if not client_id:
            return None
            
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Client).where(Client.id == client_id))
            client = result.scalar_one_or_none()
            
            if client:
                client_data = {
                    "id": client.id,
                    "name": client.name,
                    "domain": client.domain,
                    "evolution_api_url": client.evolution_api_url,
                    "evolution_api_key": client.evolution_api_key,
                    "evolution_instance": client.evolution_instance,
                    "gemini_api_key": client.gemini_api_key,
                    "gemini_model": client.gemini_model,
                    "session_timeout": client.session_timeout,
                    "max_history": client.max_history,
                    "context_window_size": client.context_window_size,
                    "agent_name": client.agent_name,
                    "agent_persona": client.agent_persona,
                    "welcome_message": client.welcome_message,
                    "ai_temperature": client.ai_temperature,
                    "rate_limit_enabled": client.rate_limit_enabled,
                    "rate_limit_calls": client.rate_limit_calls,
                    "rate_limit_period": client.rate_limit_period,
                    "business_hours": client.business_hours,
                    "timezone": client.timezone
                }
                return ClientSettings(client_data, settings)
        return None

    async def get_session(self, user_id: str, client_id: Optional[str] = None) -> Optional[SessionContext]:
        """
        Retrieve user session context with client isolation.
        
        Args:
            user_id: User ID
            client_id: Client ID for multi-tenant isolation
            
        Returns:
            SessionContext: Session context or None if doesn't exist
        """
        # Use client_id parameter or fall back to instance client settings
        effective_client_id = client_id or (self.client_settings.client_id if self.client_settings else None)
        try:
            # Test Redis connection
            if not self.redis.ping():
                print("Redis não está respondendo")
                return None

            session_data = self.redis.get(self._get_session_key(user_id, effective_client_id))
            if session_data:
                # Tenta converter o JSON
                try:
                    data = json.loads(session_data)
                except json.JSONDecodeError:
                    print("Erro ao decodificar dados da sessão")
                    return None
                    
                # Valida estrutura dos dados
                if not isinstance(data, dict) or 'messages' not in data:
                    print("Formato de dados inválido no Redis")
                    return None
                
                # Converte as mensagens de dict para objetos Message
                messages = [
                    Message(**msg) for msg in data.get('messages', [])
                ]
                
                # Reconstrói o objeto SessionContext
                return SessionContext(
                    user_id=data['user_id'],
                    messages=messages,
                    last_interaction=datetime.fromisoformat(data['last_interaction']),
                    metadata=data.get('metadata')
                )
            else:
                # If not in Redis, fetch from database with client filtering
                async with AsyncSessionLocal() as session:
                    query = select(DBMessage).where(DBMessage.user_id == user_id)
                    if effective_client_id:
                        query = query.where(DBMessage.client_id == effective_client_id)
                    
                    result = await session.execute(query.order_by(DBMessage.timestamp))
                    db_messages = result.scalars().all()

                    if not db_messages:
                        return None

                    messages = [
                        Message(
                            user_id=msg.user_id,
                            user_name=msg.user_name or "",
                            content=msg.content,
                            timestamp=msg.timestamp,
                            metadata=msg.message_metadata or {}
                        ) for msg in db_messages
                    ]

                    session_context = SessionContext(
                        user_id=user_id,
                        messages=messages,
                        last_interaction=messages[-1].timestamp,
                        metadata=messages[-1].metadata or {}
                    )

                    # Save reconstructed session to Redis
                    await self.update_session_in_redis(session_context, effective_client_id)

                    return session_context
            
        except Exception as e:
            print(f"Erro ao recuperar sessão: {str(e)}")
            return None

    async def update_session_in_redis(self, session: SessionContext, client_id: Optional[str] = None):
        """Update session in Redis with client isolation"""
        messages_data = []
        for msg in session.messages:
            msg_dict = msg.dict()
            if isinstance(msg_dict.get('timestamp'), datetime):
                msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
            messages_data.append(msg_dict)

        session_data = {
            'user_id': session.user_id,
            'messages': messages_data,
            'last_interaction': datetime.now().isoformat(),
            'metadata': session.metadata or {}
        }
        
        # Get timeout from client settings if available
        timeout = settings.session_config['timeout']
        if self.client_settings:
            timeout = self.client_settings.session_timeout
        
        effective_client_id = client_id or (self.client_settings.client_id if self.client_settings else None)
        
        for attempt in range(3):
            try:
                self.redis.setex(
                    self._get_session_key(session.user_id, effective_client_id),
                    timeout,
                    json.dumps(session_data)
                )
                break
            except redis.RedisError as e:
                print(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt == 2:
                    print("Todas as tentativas de salvar no Redis falharam")

    async def update_session(
        self, 
        user_id: str,
        message: Message,
        metadata: Optional[dict] = None,
        client_id: Optional[str] = None
    ) -> SessionContext:
        """
        Update or create a new session with client isolation.
        
        Args:
            user_id: User ID
            message: New message
            metadata: Optional session metadata
            client_id: Client ID for multi-tenant isolation
            
        Returns:
            SessionContext: Updated session
        """
        effective_client_id = client_id or (self.client_settings.client_id if self.client_settings else None)
        try:
            # Save message to database with client isolation
            async with AsyncSessionLocal() as session:
                db_message = DBMessage(
                    id=str(uuid.uuid4()),
                    client_id=effective_client_id or "default",
                    user_id=user_id,
                    user_name=message.user_name,
                    message_direction=MessageDirection.INBOUND if not message.metadata.get("from_me") else MessageDirection.OUTBOUND, # Renomeado para corresponder ao banco de dados
                    content=message.content,
                    timestamp=message.timestamp,
                    message_metadata=message.metadata
                )
                session.add(db_message)
                await session.commit()

            # Retrieve complete message history from database with client filtering
            async with AsyncSessionLocal() as session:
                query = select(DBMessage).where(DBMessage.user_id == user_id)
                if effective_client_id:
                    query = query.where(DBMessage.client_id == effective_client_id)
                
                result = await session.execute(query.order_by(DBMessage.timestamp))
                db_messages = result.scalars().all()

            messages = [
                Message(
                    user_id=msg.user_id,
                    user_name=msg.user_name or "",
                    content=msg.content,
                    timestamp=msg.timestamp,
                    metadata=msg.message_metadata or {}
                ) for msg in db_messages
            ]

            # Create or update session context
            session_context = SessionContext(
                user_id=user_id,
                messages=messages,
                metadata={
                    **(messages[-2].metadata if len(messages) > 1 else {}),
                    **(metadata or {})
                }
            )

            # Update session in Redis with client isolation
            await self.update_session_in_redis(session_context, effective_client_id)

            return session_context
            
        except Exception as e:
            print(f"Erro ao atualizar sessão: {str(e)}")
            # Retorna uma nova sessão em caso de erro
            return SessionContext(
                user_id=user_id,
                messages=[message],
                metadata=metadata or {}
            )

    async def delete_session(self, user_id: str, client_id: Optional[str] = None) -> bool:
        """
        Remove user session with client isolation.
        
        Args:
            user_id: User ID
            client_id: Client ID for multi-tenant isolation
            
        Returns:
            bool: True if successfully removed
        """
        try:
            effective_client_id = client_id or (self.client_settings.client_id if self.client_settings else None)
            self.redis.delete(self._get_session_key(user_id, effective_client_id))
            return True
        except Exception as e:
            print(f"Erro ao deletar sessão: {str(e)}")
            return False

    async def get_session_messages(
        self, 
        user_id: str,
        limit: Optional[int] = None,
        client_id: Optional[str] = None
    ) -> List[Message]:
        """
        Retrieve session messages with client isolation.
        
        Args:
            user_id: User ID
            limit: Maximum number of messages
            client_id: Client ID for multi-tenant isolation
            
        Returns:
            List[Message]: List of messages
        """
        session = await self.get_session(user_id, client_id)
        if not session:
            return []
            
        messages = session.messages
        if limit:
            messages = messages[-limit:]
            
        return messages

    async def update_session_metadata(
        self,
        user_id: str,
        metadata: dict,
        client_id: Optional[str] = None
    ) -> bool:
        """
        Update session metadata with client isolation.
        
        Args:
            user_id: User ID
            metadata: New metadata
            client_id: Client ID for multi-tenant isolation
            
        Returns:
            bool: True if successfully updated
        """
        try:
            session = await self.get_session(user_id, client_id)
            if not session:
                return False
                
            session.metadata = {
                **(session.metadata or {}),
                **metadata
            }
            
            effective_client_id = client_id or (self.client_settings.client_id if self.client_settings else None)
            
            # Update in Redis with client isolation
            session_data = {
                'user_id': session.user_id,
                'messages': [msg.dict() for msg in session.messages],
                'last_interaction': session.last_interaction.isoformat(),
                'metadata': session.metadata
            }
            
            timeout = settings.session_config['timeout']
            if self.client_settings:
                timeout = self.client_settings.session_timeout
            
            self.redis.setex(
                self._get_session_key(user_id, effective_client_id),
                timeout,
                json.dumps(session_data)
            )
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar metadados: {str(e)}")
            return False