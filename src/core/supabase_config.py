"""
Supabase configuration and client setup for SDR Agent
"""
import os
from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SupabaseConfig:
    """Supabase configuration and client management"""
    
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.anon_key = os.environ.get("SUPABASE_ANON_KEY") 
        self.service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.url, self.anon_key, self.service_role_key]):
            raise ValueError("Missing required Supabase environment variables")
    
    def get_client(self, use_service_role: bool = True) -> Client:
        """
        Get Supabase client
        
        Args:
            use_service_role: If True, uses service role key (for backend operations)
                            If False, uses anon key (for frontend operations)
        """
        key = self.service_role_key if use_service_role else self.anon_key
        return create_client(self.url, key)
    
    def get_admin_client(self) -> Client:
        """Get admin client with service role permissions"""
        return self.get_client(use_service_role=True)
    
    def get_public_client(self) -> Client:
        """Get public client with anon key"""
        return self.get_client(use_service_role=False)

# Global instance
supabase_config = SupabaseConfig()

def get_supabase_client(admin: bool = True) -> Client:
    """
    Get Supabase client instance
    
    Args:
        admin: If True, returns admin client with service role
               If False, returns public client with anon key
    """
    try:
        if admin:
            return supabase_config.get_admin_client()
        else:
            return supabase_config.get_public_client()
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise