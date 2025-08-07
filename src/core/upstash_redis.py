"""
Upstash Redis configuration and client setup for SDR Agent
"""
import os
import json
import redis
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class UpstashRedisClient:
    """Upstash Redis client for session management and caching"""
    
    def __init__(self):
        self.redis_url = os.environ.get("UPSTASH_REDIS_REST_URL")
        self.redis_token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
        
        if not all([self.redis_url, self.redis_token]):
            raise ValueError("Missing required Upstash Redis environment variables")
        
        # Create Redis client
        self.client = redis.from_url(
            self.redis_url,
            password=self.redis_token,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def set_with_expiry(self, key: str, value: Any, expiry_seconds: int = 3600) -> bool:
        """Set a key with expiration"""
        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            return self.client.setex(key, expiry_seconds, serialized_value)
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a key value"""
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check key existence {key}: {e}")
            return False

class SessionManager:
    """Session management using Upstash Redis"""
    
    def __init__(self):
        self.redis = UpstashRedisClient()
        self.default_expiry = 3600  # 1 hour
    
    def _get_session_key(self, client_id: str, user_id: str) -> str:
        """Generate session key"""
        return f"session:{client_id}:{user_id}"
    
    def _get_conversation_key(self, client_id: str, user_id: str) -> str:
        """Generate conversation history key"""
        return f"conversation:{client_id}:{user_id}"
    
    async def store_session(self, client_id: str, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Store user session data"""
        key = self._get_session_key(client_id, user_id)
        session_data['last_activity'] = datetime.now(timezone.utc).isoformat()
        return await self.redis.set_with_expiry(key, session_data, self.default_expiry)
    
    async def get_session(self, client_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        key = self._get_session_key(client_id, user_id)
        return await self.redis.get(key)
    
    async def update_session(self, client_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        session = await self.get_session(client_id, user_id)
        if session:
            session.update(updates)
            session['last_activity'] = datetime.now(timezone.utc).isoformat()
            return await self.store_session(client_id, user_id, session)
        return False
    
    async def delete_session(self, client_id: str, user_id: str) -> bool:
        """Delete user session"""
        session_key = self._get_session_key(client_id, user_id)
        conversation_key = self._get_conversation_key(client_id, user_id)
        
        # Delete both session and conversation history
        session_deleted = await self.redis.delete(session_key)
        conversation_deleted = await self.redis.delete(conversation_key)
        
        return session_deleted or conversation_deleted
    
    async def store_conversation_history(self, client_id: str, user_id: str, messages: list, max_messages: int = 50) -> bool:
        """Store conversation history with message limit"""
        key = self._get_conversation_key(client_id, user_id)
        
        # Keep only the last max_messages
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
        
        conversation_data = {
            'messages': messages,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        return await self.redis.set_with_expiry(key, conversation_data, self.default_expiry * 24)  # 24 hours for conversation
    
    async def get_conversation_history(self, client_id: str, user_id: str) -> list:
        """Get conversation history"""
        key = self._get_conversation_key(client_id, user_id)
        data = await self.redis.get(key)
        
        if data and isinstance(data, dict):
            return data.get('messages', [])
        return []
    
    async def add_message_to_conversation(self, client_id: str, user_id: str, message: Dict[str, Any]) -> bool:
        """Add a single message to conversation history"""
        messages = await self.get_conversation_history(client_id, user_id)
        messages.append(message)
        return await self.store_conversation_history(client_id, user_id, messages)

# Global instances
redis_client = None
session_manager = None

def get_redis_client() -> UpstashRedisClient:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = UpstashRedisClient()
    return redis_client

def get_session_manager() -> SessionManager:
    """Get session manager instance"""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager