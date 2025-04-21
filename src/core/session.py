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
            # Testa conexão com Redis
            if not self.redis.ping():
                print("Redis não está respondendo")
                return None

            session_data = self.redis.get(self._get_session_key(user_id))
            if not session_data:
                return None
                
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
            # Recupera a sessão existente ou cria uma nova
            current_session = await self.get_session(user_id)
            
            # Somente processa se as sessões estiverem habilitadas
            if not settings.SESSION_CONFIG['enabled']:
                return SessionContext(
                    user_id=user_id,
                    messages=[message],
                    metadata=metadata or {}
                )

            # Inicializa a lista de mensagens
            messages = []
            
            if current_session:
                # Adiciona mensagens existentes
                messages.extend(current_session.messages)
                
                # Remove mensagens antigas se exceder o limite
                max_history = settings.SESSION_CONFIG['max_history']
                if len(messages) >= max_history:
                    messages = messages[-(max_history-1):]  # Remove mais antigas mantendo espaço para nova
            
            # Adiciona a nova mensagem
            messages.append(message)
            
            # Cria ou atualiza a sessão
            session = SessionContext(
                user_id=user_id,
                messages=messages,
                metadata={
                    **(current_session.metadata if current_session else {}),
                    **(metadata or {})
                }
            )
            
            # Prepara dados para salvar no Redis
            messages_data = []
            for msg in session.messages:
                msg_dict = msg.dict()
                # Garante que timestamp seja string
                if isinstance(msg_dict.get('timestamp'), datetime):
                    msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
                messages_data.append(msg_dict)

            session_data = {
                'user_id': session.user_id,
                'messages': messages_data,
                'last_interaction': datetime.now().isoformat(),
                'metadata': session.metadata or {}
            }
            
            # Tenta salvar no Redis com retry
            for attempt in range(3):  # 3 tentativas
                try:
                    self.redis.setex(
                        self._get_session_key(user_id),
                        settings.SESSION_CONFIG['timeout'],
                        json.dumps(session_data)
                    )
                    break
                except redis.RedisError as e:
                    print(f"Tentativa {attempt + 1} falhou: {str(e)}")
                    if attempt == 2:  # última tentativa
                        print("Todas as tentativas de salvar no Redis falharam")
                        return session
            
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
                settings.SESSION_CONFIG['timeout'],
                json.dumps(session_data)
            )
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar metadados: {str(e)}")
            return False