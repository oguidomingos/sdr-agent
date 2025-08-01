"""
Evolution API External Service Integration
Replaces local Evolution API with centralsupernova.com.br external service
"""
import os
import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EvolutionExternalClient:
    """
    Client for Evolution API external service at centralsupernova.com.br
    """
    
    def __init__(self):
        self.base_url = os.environ.get("EVOLUTION_API_URL", "https://evolutionapi.centralsupernova.com.br")
        self.api_key = os.environ.get("EVOLUTION_API_KEY", "509dbd54-c20c-4a5b-b889-a0494a861f5a")
        
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        # HTTP client with timeout and retry settings
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to Evolution API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data or None if failed
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )
                
                response.raise_for_status()
                
                # Try to parse JSON response
                try:
                    return response.json()
                except json.JSONDecodeError:
                    logger.warning(f"Non-JSON response from {endpoint}: {response.text}")
                    return {"success": True, "text": response.text}
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout making request to {endpoint}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {endpoint}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error making request to {endpoint}: {e}")
            return None
    
    async def create_instance(self, instance_name: str, webhook_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new WhatsApp instance
        
        Args:
            instance_name: Name for the instance
            webhook_url: Optional webhook URL for receiving messages
            
        Returns:
            Instance creation response
        """
        data = {
            "instanceName": instance_name,
            "token": instance_name,
            "qrcode": True
        }
        
        if webhook_url:
            data["webhook"] = webhook_url
        
        logger.info(f"Creating Evolution API instance: {instance_name}")
        return await self._make_request("POST", "/instance/create", data)
    
    async def get_instance_info(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Get instance information
        
        Args:
            instance_name: Instance name
            
        Returns:
            Instance information
        """
        return await self._make_request("GET", f"/instance/fetchInstances/{instance_name}")
    
    async def get_qr_code(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Get QR code for WhatsApp connection
        
        Args:
            instance_name: Instance name
            
        Returns:
            QR code data
        """
        return await self._make_request("GET", f"/instance/connect/{instance_name}")
    
    async def get_connection_status(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Get connection status of instance
        
        Args:
            instance_name: Instance name
            
        Returns:
            Connection status
        """
        return await self._make_request("GET", f"/instance/connectionState/{instance_name}")
    
    async def send_text_message(
        self,
        instance_name: str,
        number: str,
        message: str,
        delay: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send text message
        
        Args:
            instance_name: Instance name
            number: WhatsApp number (with country code)
            message: Message text
            delay: Optional delay in milliseconds
            
        Returns:
            Send message response
        """
        data = {
            "number": number,
            "text": message
        }
        
        if delay:
            data["delay"] = delay
        
        logger.info(f"Sending message to {number} via instance {instance_name}")
        return await self._make_request("POST", f"/message/sendText/{instance_name}", data)
    
    async def send_media_message(
        self,
        instance_name: str,
        number: str,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "image"
    ) -> Optional[Dict[str, Any]]:
        """
        Send media message
        
        Args:
            instance_name: Instance name
            number: WhatsApp number
            media_url: URL of media file
            caption: Optional caption
            media_type: Type of media (image, video, audio, document)
            
        Returns:
            Send message response
        """
        data = {
            "number": number,
            "mediaMessage": {
                "mediatype": media_type,
                "media": media_url
            }
        }
        
        if caption:
            data["mediaMessage"]["caption"] = caption
        
        return await self._make_request("POST", f"/message/sendMedia/{instance_name}", data)
    
    async def set_webhook(self, instance_name: str, webhook_url: str) -> Optional[Dict[str, Any]]:
        """
        Set webhook URL for instance
        
        Args:
            instance_name: Instance name
            webhook_url: Webhook URL
            
        Returns:
            Webhook configuration response
        """
        data = {
            "webhook": webhook_url,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGE_UPDATE",
                "MESSAGES_DELETE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE",
                "PRESENCE_UPDATE",
                "CHATS_SET",
                "CHATS_UPSERT",
                "CHATS_UPDATE",
                "CHATS_DELETE",
                "CONTACTS_SET",
                "CONTACTS_UPSERT",
                "CONTACTS_UPDATE",
                "GROUPS_UPSERT",
                "GROUP_UPDATE",
                "GROUP_PARTICIPANTS_UPDATE"
            ]
        }
        
        logger.info(f"Setting webhook for instance {instance_name}: {webhook_url}")
        return await self._make_request("POST", f"/webhook/set/{instance_name}", data)
    
    async def delete_instance(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Delete instance
        
        Args:
            instance_name: Instance name
            
        Returns:
            Delete response
        """
        logger.info(f"Deleting Evolution API instance: {instance_name}")
        return await self._make_request("DELETE", f"/instance/delete/{instance_name}")
    
    async def logout_instance(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Logout from WhatsApp
        
        Args:
            instance_name: Instance name
            
        Returns:
            Logout response
        """
        return await self._make_request("DELETE", f"/instance/logout/{instance_name}")
    
    async def restart_instance(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Restart instance
        
        Args:
            instance_name: Instance name
            
        Returns:
            Restart response
        """
        return await self._make_request("PUT", f"/instance/restart/{instance_name}")
    
    async def get_profile_picture(self, instance_name: str, number: str) -> Optional[Dict[str, Any]]:
        """
        Get profile picture URL
        
        Args:
            instance_name: Instance name
            number: WhatsApp number
            
        Returns:
            Profile picture data
        """
        return await self._make_request("GET", f"/chat/whatsappProfile/{instance_name}", params={"number": number})
    
    async def get_contacts(self, instance_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get all contacts
        
        Args:
            instance_name: Instance name
            
        Returns:
            List of contacts
        """
        response = await self._make_request("GET", f"/chat/findContacts/{instance_name}")
        return response if isinstance(response, list) else []
    
    async def health_check(self) -> bool:
        """
        Check if Evolution API service is healthy
        
        Returns:
            True if service is responding
        """
        try:
            response = await self._make_request("GET", "/")
            return response is not None
        except Exception as e:
            logger.error(f"Evolution API health check failed: {e}")
            return False

class EvolutionClientManager:
    """
    Manager for Evolution API clients with multi-tenant support
    """
    
    def __init__(self):
        self.evolution_client = EvolutionExternalClient()
    
    async def get_or_create_instance(
        self,
        client_id: str,
        client_config: Dict[str, Any],
        webhook_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Get existing instance or create new one for client
        
        Args:
            client_id: Client ID
            client_config: Client configuration
            webhook_url: Webhook URL for this client
            
        Returns:
            Instance name or None if failed
        """
        instance_name = client_config.get('evolution_instance') or f"client_{client_id}"
        
        # Check if instance exists
        instance_info = await self.evolution_client.get_instance_info(instance_name)
        
        if not instance_info:
            # Create new instance
            logger.info(f"Creating new Evolution instance for client {client_id}")
            create_result = await self.evolution_client.create_instance(instance_name, webhook_url)
            
            if not create_result:
                logger.error(f"Failed to create instance for client {client_id}")
                return None
        
        # Set webhook if provided
        if webhook_url:
            await self.evolution_client.set_webhook(instance_name, webhook_url)
        
        return instance_name
    
    async def send_message_for_client(
        self,
        client_id: str,
        client_config: Dict[str, Any],
        number: str,
        message: str
    ) -> bool:
        """
        Send message for specific client
        
        Args:
            client_id: Client ID
            client_config: Client configuration
            number: WhatsApp number
            message: Message text
            
        Returns:
            True if message sent successfully
        """
        instance_name = client_config.get('evolution_instance') or f"client_{client_id}"
        
        result = await self.evolution_client.send_text_message(instance_name, number, message)
        
        if result:
            logger.info(f"Message sent successfully for client {client_id} to {number}")
            return True
        else:
            logger.error(f"Failed to send message for client {client_id} to {number}")
            return False
    
    async def get_connection_status_for_client(
        self,
        client_id: str,
        client_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get connection status for client's instance
        
        Args:
            client_id: Client ID
            client_config: Client configuration
            
        Returns:
            Connection status or None
        """
        instance_name = client_config.get('evolution_instance') or f"client_{client_id}"
        return await self.evolution_client.get_connection_status(instance_name)

# Global instances
_evolution_client = None
_evolution_manager = None

def get_evolution_client() -> EvolutionExternalClient:
    """Get global Evolution client instance"""
    global _evolution_client
    if _evolution_client is None:
        _evolution_client = EvolutionExternalClient()
    return _evolution_client

def get_evolution_manager() -> EvolutionClientManager:
    """Get global Evolution manager instance"""
    global _evolution_manager
    if _evolution_manager is None:
        _evolution_manager = EvolutionClientManager()
    return _evolution_manager