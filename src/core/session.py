from typing import Optional, List
from datetime import datetime
import json
import redis

from src.types.schemas import Message, SessionContext
from src.config.settings import settings


class SessionManager:
    """
    Gerencia o estado e contexto das conversas
    """
    
    def __init__(self):
        self.redis = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True
        )

    def _get_session_key(self, user_id: str) -> str:
        """
        Gera a chave Redis para a sessão do usuário
        """
        return f"session:{user_id}"

    async def get_session(self, user_id: str) -> Optional[SessionContext]:
        """
        Recupera o contexto da sessão do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            SessionContext: Contexto da sessão ou None se não existir
        """
        try:
            session_data = self.redis.get(self._get_session_key(user_id))
            if not session_data:
                return None
                
            # Converte o JSON armazenado em SessionContext
            data = json.loads(session_data)
            
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
            
        except Exception as e:
            print(f"Erro ao recuperar sessão: {str(e)}")
            return None

    async def update_session(
        self, 
        user_id: str,
        message: Message,
        metadata: Optional[dict] = None
    ) -> SessionContext:
        """
        Atualiza ou cria uma nova sessão
        
        Args:
            user_id: ID do usuário
            message: Nova mensagem
            metadata: Metadados opcionais para a sessão
            
        Returns:
            SessionContext: Sessão atualizada
        """
        try:
            # Recupera ou cria nova sessão
            session = await self.get_session(user_id)
            if not session:
                session = SessionContext(
                    user_id=user_id,
                    messages=[],
                    metadata=metadata or {}
                )
            
            # Atualiza a sessão
            session.messages.append(message)
            session.last_interaction = datetime.now()
            
            # Mantém apenas as últimas N mensagens (janela deslizante)
            if len(session.messages) > settings.CONTEXT_WINDOW_SIZE:
                session.messages = session.messages[-settings.CONTEXT_WINDOW_SIZE:]
            
            # Atualiza metadados se fornecidos
            if metadata:
                session.metadata = {
                    **(session.metadata or {}),
                    **metadata
                }
            
            # Salva no Redis
            session_data = {
                'user_id': session.user_id,
                'messages': [
                    {
                        **msg.dict(),
                        'timestamp': msg.timestamp.isoformat()
                    } for msg in session.messages
                ],
                'last_interaction': session.last_interaction.isoformat(),
                'metadata': session.metadata
            }
            
            self.redis.setex(
                self._get_session_key(user_id),
                settings.SESSION_TIMEOUT,
                json.dumps(session_data)
            )
            
            return session
            
        except Exception as e:
            print(f"Erro ao atualizar sessão: {str(e)}")
            # Retorna uma nova sessão em caso de erro
            return SessionContext(
                user_id=user_id,
                messages=[message],
                metadata=metadata or {}
            )

    async def delete_session(self, user_id: str) -> bool:
        """
        Remove a sessão do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            bool: True se removida com sucesso
        """
        try:
            self.redis.delete(self._get_session_key(user_id))
            return True
        except Exception as e:
            print(f"Erro ao deletar sessão: {str(e)}")
            return False

    async def get_session_messages(
        self, 
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Recupera as mensagens da sessão
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de mensagens
            
        Returns:
            List[Message]: Lista de mensagens
        """
        session = await self.get_session(user_id)
        if not session:
            return []
            
        messages = session.messages
        if limit:
            messages = messages[-limit:]
            
        return messages

    async def update_session_metadata(
        self,
        user_id: str,
        metadata: dict
    ) -> bool:
        """
        Atualiza os metadados da sessão
        
        Args:
            user_id: ID do usuário
            metadata: Novos metadados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            session = await self.get_session(user_id)
            if not session:
                return False
                
            session.metadata = {
                **(session.metadata or {}),
                **metadata
            }
            
            # Atualiza no Redis
            session_data = {
                'user_id': session.user_id,
                'messages': [msg.dict() for msg in session.messages],
                'last_interaction': session.last_interaction.isoformat(),
                'metadata': session.metadata
            }
            
            self.redis.setex(
                self._get_session_key(user_id),
                settings.SESSION_TIMEOUT,
                json.dumps(session_data)
            )
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar metadados: {str(e)}")
            return False