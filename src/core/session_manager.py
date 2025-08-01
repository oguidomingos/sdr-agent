"""
Refactored Session Manager for Supabase + Upstash Redis architecture
Replaces the old session.py with cloud-native session management
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid
import logging

from src.types.schemas import Message, SessionContext
from src.core.upstash_redis import get_session_manager as get_redis_session_manager
from src.core.supabase_db import get_supabase_db
from src.config.settings import settings

logger = logging.getLogger(__name__)

class CloudSessionManager:
    """
    Cloud-native session manager using Supabase + Upstash Redis
    Provides multi-tenant session management with proper isolation
    """
    
    def __init__(self):
        self.redis_session = get_redis_session_manager()
        self.db = get_supabase_db()
        self.default_timeout = 3600  # 1 hour
    
    async def get_session(self, user_id: str, client_id: str) -> Optional[SessionContext]:
        """
        Retrieve user session context with client isolation
        
        Args:
            user_id: WhatsApp user ID
            client_id: Client ID for multi-tenant isolation
            
        Returns:
            SessionContext or None if doesn't exist
        """
        try:
            # First try to get from Redis cache
            session_data = await self.redis_session.get_session(client_id, user_id)
            
            if session_data:
                # Convert cached data back to SessionContext
                messages = [
                    Message(**msg) for msg in session_data.get('messages', [])
                ]
                
                return SessionContext(
                    user_id=user_id,
                    messages=messages,
                    last_interaction=datetime.fromisoformat(session_data['last_interaction']),
                    metadata=session_data.get('metadata', {})
                )
            
            # If not in cache, fetch from Supabase
            conversation_history = await self.db.get_conversation_history(client_id, user_id, limit=50)
            
            if not conversation_history:
                return None
            
            # Convert database messages to Message objects
            messages = []
            for db_msg in conversation_history:
                messages.append(Message(
                    user_id=db_msg['user_id'],
                    user_name=db_msg.get('user_name', ''),
                    message_direction=db_msg['message_direction'],
                    content=db_msg['content'],
                    timestamp=datetime.fromisoformat(db_msg['timestamp']) if isinstance(db_msg['timestamp'], str) else db_msg['timestamp'],
                    metadata=db_msg.get('message_metadata', {})
                ))
            
            # Create session context
            session_context = SessionContext(
                user_id=user_id,
                messages=messages,
                last_interaction=messages[-1].timestamp if messages else datetime.utcnow(),
                metadata=messages[-1].metadata if messages else {}
            )
            
            # Cache in Redis for future requests
            await self._cache_session(client_id, user_id, session_context)
            
            return session_context
            
        except Exception as e:
            logger.error(f"Error retrieving session for user {user_id}, client {client_id}: {e}")
            return None
    
    async def update_session(
        self,
        user_id: str,
        client_id: str,
        message: Message,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionContext:
        """
        Update or create session with new message
        
        Args:
            user_id: WhatsApp user ID
            client_id: Client ID for multi-tenant isolation
            message: New message to add
            metadata: Optional session metadata
            
        Returns:
            Updated SessionContext
        """
        try:
            # Save message to Supabase
            message_data = {
                'id': str(uuid.uuid4()),
                'client_id': client_id,
                'user_id': user_id,
                'user_name': message.user_name,
                'message_direction': message.message_direction,
                'content': message.content,
                'timestamp': message.timestamp.isoformat() if isinstance(message.timestamp, datetime) else message.timestamp,
                'message_metadata': message.metadata or {}
            }
            
            await self.db.create_message(message_data)
            
            # Get updated conversation history
            conversation_history = await self.db.get_conversation_history(client_id, user_id, limit=50)
            
            # Convert to Message objects
            messages = []
            for db_msg in conversation_history:
                messages.append(Message(
                    user_id=db_msg['user_id'],
                    user_name=db_msg.get('user_name', ''),
                    message_direction=db_msg['message_direction'],
                    content=db_msg['content'],
                    timestamp=datetime.fromisoformat(db_msg['timestamp']) if isinstance(db_msg['timestamp'], str) else db_msg['timestamp'],
                    metadata=db_msg.get('message_metadata', {})
                ))
            
            # Create updated session context
            session_context = SessionContext(
                user_id=user_id,
                messages=messages,
                last_interaction=datetime.utcnow(),
                metadata={
                    **(messages[-2].metadata if len(messages) > 1 else {}),
                    **(metadata or {})
                }
            )
            
            # Update cache
            await self._cache_session(client_id, user_id, session_context)
            
            return session_context
            
        except Exception as e:
            logger.error(f"Error updating session for user {user_id}, client {client_id}: {e}")
            # Return minimal session context in case of error
            return SessionContext(
                user_id=user_id,
                messages=[message],
                last_interaction=datetime.utcnow(),
                metadata=metadata or {}
            )
    
    async def delete_session(self, user_id: str, client_id: str) -> bool:
        """
        Delete user session from cache
        Note: This doesn't delete from Supabase, only from Redis cache
        
        Args:
            user_id: WhatsApp user ID
            client_id: Client ID for multi-tenant isolation
            
        Returns:
            True if successfully deleted
        """
        try:
            return await self.redis_session.delete_session(client_id, user_id)
        except Exception as e:
            logger.error(f"Error deleting session for user {user_id}, client {client_id}: {e}")
            return False
    
    async def get_session_messages(
        self,
        user_id: str,
        client_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get session messages with optional limit
        
        Args:
            user_id: WhatsApp user ID
            client_id: Client ID for multi-tenant isolation
            limit: Maximum number of messages to return
            
        Returns:
            List of Message objects
        """
        try:
            session = await self.get_session(user_id, client_id)
            if not session:
                return []
            
            messages = session.messages
            if limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting session messages for user {user_id}, client {client_id}: {e}")
            return []
    
    async def update_session_metadata(
        self,
        user_id: str,
        client_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update session metadata
        
        Args:
            user_id: WhatsApp user ID
            client_id: Client ID for multi-tenant isolation
            metadata: New metadata to merge
            
        Returns:
            True if successfully updated
        """
        try:
            session = await self.get_session(user_id, client_id)
            if not session:
                return False
            
            # Merge metadata
            session.metadata = {
                **(session.metadata or {}),
                **metadata
            }
            
            # Update cache
            await self._cache_session(client_id, user_id, session)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating session metadata for user {user_id}, client {client_id}: {e}")
            return False
    
    async def _cache_session(self, client_id: str, user_id: str, session: SessionContext):
        """
        Cache session in Redis
        
        Args:
            client_id: Client ID
            user_id: User ID
            session: SessionContext to cache
        """
        try:
            # Convert messages to serializable format
            messages_data = []
            for msg in session.messages:
                msg_dict = msg.dict()
                if isinstance(msg_dict.get('timestamp'), datetime):
                    msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
                messages_data.append(msg_dict)
            
            session_data = {
                'user_id': session.user_id,
                'messages': messages_data,
                'last_interaction': session.last_interaction.isoformat() if isinstance(session.last_interaction, datetime) else session.last_interaction,
                'metadata': session.metadata or {}
            }
            
            # Store in Redis with client isolation
            await self.redis_session.store_session(client_id, user_id, session_data)
            
        except Exception as e:
            logger.error(f"Error caching session for user {user_id}, client {client_id}: {e}")
    
    async def get_client_settings(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get client settings from Supabase
        
        Args:
            client_id: Client ID
            
        Returns:
            Client settings dictionary or None
        """
        try:
            return await self.db.get_client_by_id(client_id)
        except Exception as e:
            logger.error(f"Error getting client settings for {client_id}: {e}")
            return None

# Global instance
_cloud_session_manager = None

def get_cloud_session_manager() -> CloudSessionManager:
    """Get global CloudSessionManager instance"""
    global _cloud_session_manager
    if _cloud_session_manager is None:
        _cloud_session_manager = CloudSessionManager()
    return _cloud_session_manager

# Compatibility alias for existing code
SessionManager = CloudSessionManager