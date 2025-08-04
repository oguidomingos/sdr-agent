"""
Supabase database operations for SDR Agent
Replaces the traditional SQLAlchemy setup with Supabase client operations
"""
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseDB:
    """Supabase database operations manager"""
    
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.service_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required")
        
        try:
            self.client: Client = create_client(self.url, self.service_key)
            # Test connection immediately
            self._validate_connection()
        except Exception as e:
            raise ValueError(f"Failed to connect to Supabase: {str(e)}")
    
    def _validate_connection(self):
        """Validate Supabase connection on initialization"""
        try:
            # Test connection with a simple query
            result = self.client.table('users').select('id').limit(1).execute()
            if not hasattr(result, 'data'):
                raise Exception("Invalid Supabase response format")
            logger.info("✅ Supabase connection validated successfully")
        except Exception as e:
            logger.error(f"❌ Supabase connection validation failed: {e}")
            raise Exception(f"Supabase connection test failed: {str(e)}")
    
    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            result = self.client.table('users').insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.client.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.client.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user data"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('users').update(updates).eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return None
    
    # Client operations
    async def create_client(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new client"""
        try:
            result = self.client.table('clients').insert(client_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to create client: {e}")
            return None
    
    async def get_client_by_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID"""
        try:
            result = self.client.table('clients').select('*').eq('id', client_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get client by ID: {e}")
            return None
    
    async def get_client_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get client by domain"""
        try:
            result = self.client.table('clients').select('*').eq('domain', domain).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get client by domain: {e}")
            return None
    
    async def get_clients_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        """Get all clients owned by a user"""
        try:
            result = self.client.table('clients').select('*').eq('owner_id', owner_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get clients by owner: {e}")
            return []
    
    async def update_client(self, client_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update client data"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('clients').update(updates).eq('id', client_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update client: {e}")
            return None
    
    async def delete_client(self, client_id: str) -> bool:
        """Delete a client"""
        try:
            result = self.client.table('clients').delete().eq('id', client_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to delete client: {e}")
            return False
    
    # Message operations
    async def create_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new message"""
        try:
            result = self.client.table('messages').insert(message_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            return None
    
    async def get_messages_by_client(self, client_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages for a client"""
        try:
            result = (self.client.table('messages')
                     .select('*')
                     .eq('client_id', client_id)
                     .order('timestamp', desc=True)
                     .limit(limit)
                     .execute())
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get messages by client: {e}")
            return []
    
    async def get_conversation_history(self, client_id: str, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for a specific user"""
        try:
            result = (self.client.table('messages')
                     .select('*')
                     .eq('client_id', client_id)
                     .eq('user_id', user_id)
                     .order('timestamp', desc=True)
                     .limit(limit)
                     .execute())
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def update_message_status(self, message_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update message status"""
        try:
            result = self.client.table('messages').update({'status': status}).eq('id', message_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update message status: {e}")
            return None
    
    # Playbook operations
    async def create_playbook(self, playbook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new playbook"""
        try:
            result = self.client.table('playbooks').insert(playbook_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to create playbook: {e}")
            return None
    
    async def get_playbooks_by_client(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all playbooks for a client"""
        try:
            result = self.client.table('playbooks').select('*').eq('client_id', client_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get playbooks by client: {e}")
            return []
    
    async def get_default_playbook(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get the default playbook for a client"""
        try:
            result = (self.client.table('playbooks')
                     .select('*')
                     .eq('client_id', client_id)
                     .eq('is_default', True)
                     .eq('status', 'active')
                     .execute())
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get default playbook: {e}")
            return None
    
    async def update_playbook(self, playbook_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update playbook data"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('playbooks').update(updates).eq('id', playbook_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to update playbook: {e}")
            return None
    
    # Agent Config operations
    async def create_agent_config(self, config_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new agent config"""
        try:
            result = self.client.table('agent_configs').insert(config_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to create agent config: {e}")
            return None
    
    async def get_active_agent_config(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get the active agent config for a client"""
        try:
            result = (self.client.table('agent_configs')
                     .select('*')
                     .eq('client_id', client_id)
                     .eq('is_active', True)
                     .execute())
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get active agent config: {e}")
            return None
    
    # Health check
    async def health_check(self) -> bool:
        """Check if Supabase connection is healthy"""
        try:
            # Simple query to test connection
            result = self.client.table('users').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False

# Global instance
_supabase_db = None

def get_supabase_db() -> SupabaseDB:
    """Get Supabase database instance"""
    global _supabase_db
    if _supabase_db is None:
        _supabase_db = SupabaseDB()
    return _supabase_db

# Compatibility functions for existing code
async def get_db():
    """Compatibility function for dependency injection"""
    return get_supabase_db()

async def init_db():
    """Initialize database connection (compatibility function)"""
    try:
        db = get_supabase_db()
        is_healthy = await db.health_check()
        if is_healthy:
            print("✅ Supabase connection established successfully!")
        else:
            print("⚠️  Supabase connection test failed")
        return is_healthy
    except Exception as e:
        print(f"❌ Failed to initialize Supabase connection: {e}")
        return False