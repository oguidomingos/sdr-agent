"""
Webhook router for serverless deployment
"""
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import hmac
import hashlib
import logging

from src.core.supabase_db import get_supabase_db
from src.core.session_manager import get_cloud_session_manager
from src.core.evolution_external import get_evolution_manager
from src.core.gemini import GeminiClient
from src.types.schemas import Message, MessageDirection

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class WebhookData(BaseModel):
    event: str
    instance: str
    data: Dict[str, Any]

class WhatsAppMessage(BaseModel):
    key: Dict[str, Any]
    message: Dict[str, Any]
    messageTimestamp: Optional[str] = None
    pushName: Optional[str] = None
    status: Optional[str] = None

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    if not signature or not secret:
        return True  # Skip verification if not configured
    
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False

async def get_client_by_instance(instance_name: str) -> Optional[Dict[str, Any]]:
    """Get client configuration by Evolution instance name"""
    db = get_supabase_db()
    
    # This is a simplified approach - in practice, you might need a more sophisticated lookup
    # For now, we'll assume instance name follows pattern "client_{client_id}"
    if instance_name.startswith("client_"):
        client_id = instance_name.replace("client_", "")
        return await db.get_client_by_id(client_id)
    
    # Fallback: search by evolution_instance field
    # This would require a new method in SupabaseDB
    # For now, return None
    return None

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    x_hub_signature: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """Handle WhatsApp webhook from Evolution API"""
    try:
        # Get request body
        body = await request.body()
        
        # Parse JSON data
        try:
            webhook_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Extract instance name
        instance_name = webhook_data.get('instance', '')
        if not instance_name:
            raise HTTPException(status_code=400, detail="Missing instance name")
        
        # Get client configuration
        client_config = await get_client_by_instance(instance_name)
        if not client_config:
            logger.warning(f"No client found for instance: {instance_name}")
            return {"status": "ignored", "reason": "unknown_instance"}
        
        # Verify webhook signature if configured
        webhook_secret = client_config.get('webhook_secret')
        signature = x_signature or x_hub_signature
        
        if webhook_secret and not verify_webhook_signature(body, signature or '', webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process webhook event
        event_type = webhook_data.get('event', '')
        event_data = webhook_data.get('data', {})
        
        if event_type == 'messages.upsert':
            return await handle_message_event(client_config, event_data)
        elif event_type == 'connection.update':
            return await handle_connection_event(client_config, event_data)
        else:
            logger.info(f"Unhandled webhook event: {event_type}")
            return {"status": "ignored", "reason": "unhandled_event"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_message_event(client_config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming message event"""
    try:
        # Extract message data
        messages = event_data.get('messages', [])
        if not messages:
            return {"status": "ignored", "reason": "no_messages"}
        
        # Process each message
        for msg_data in messages:
            # Skip messages from bot itself
            if msg_data.get('key', {}).get('fromMe', False):
                continue
            
            # Extract message details
            sender_number = msg_data.get('key', {}).get('remoteJid', '').replace('@s.whatsapp.net', '')
            push_name = msg_data.get('pushName', 'Unknown')
            message_content = ""
            
            # Extract message content based on type
            message = msg_data.get('message', {})
            if 'conversation' in message:
                message_content = message['conversation']
            elif 'extendedTextMessage' in message:
                message_content = message['extendedTextMessage'].get('text', '')
            elif 'imageMessage' in message:
                message_content = message['imageMessage'].get('caption', '[Image]')
            elif 'videoMessage' in message:
                message_content = message['videoMessage'].get('caption', '[Video]')
            elif 'audioMessage' in message:
                message_content = '[Audio]'
            elif 'documentMessage' in message:
                message_content = f"[Document: {message['documentMessage'].get('fileName', 'Unknown')}]"
            else:
                message_content = '[Unsupported message type]'
            
            if not message_content.strip():
                continue
            
            # Create message object
            user_message = Message(
                user_id=sender_number,
                user_name=push_name,
                message_direction=MessageDirection.INBOUND,
                content=message_content,
                timestamp=msg_data.get('messageTimestamp', ''),
                metadata={
                    "from_me": False,
                    "message_id": msg_data.get('key', {}).get('id', ''),
                    "instance": client_config.get('evolution_instance', '')
                }
            )
            
            # Process message
            await process_incoming_message(client_config, user_message)
        
        return {"status": "processed", "message_count": len(messages)}
    
    except Exception as e:
        logger.error(f"Error handling message event: {e}")
        return {"status": "error", "error": str(e)}

async def handle_connection_event(client_config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle connection status event"""
    try:
        connection_state = event_data.get('state', '')
        logger.info(f"Connection state for client {client_config['id']}: {connection_state}")
        
        # Update client connection status if needed
        # This could be stored in the database for monitoring
        
        return {"status": "processed", "connection_state": connection_state}
    
    except Exception as e:
        logger.error(f"Error handling connection event: {e}")
        return {"status": "error", "error": str(e)}

async def process_incoming_message(client_config: Dict[str, Any], message: Message):
    """Process incoming message with AI and send response"""
    try:
        client_id = client_config['id']
        user_id = message.user_id
        
        # Get session manager and update session
        session_manager = get_cloud_session_manager()
        session = await session_manager.update_session(user_id, client_id, message)
        
        # Check if this is the first message (send welcome)
        if len(session.messages) == 1:
            welcome_message = client_config.get('welcome_message', 'Olá! Como posso ajudá-lo?')
            await send_response_message(client_config, user_id, welcome_message)
            return
        
        # Process with AI
        gemini_client = GeminiClient()
        
        # Configure Gemini with client settings
        gemini_client.configure_for_client(
            api_key=client_config.get('gemini_api_key'),
            model=client_config.get('gemini_model', 'gemini-2.0-flash'),
            temperature=client_config.get('ai_temperature', 70) / 100.0
        )
        
        # Generate AI response
        ai_response = await gemini_client.process_session(
            session=session,
            client_config=client_config,
            user_message=message.content
        )
        
        if ai_response:
            await send_response_message(client_config, user_id, ai_response)
        
    except Exception as e:
        logger.error(f"Error processing incoming message: {e}")
        # Send fallback message
        fallback_message = "Desculpe, ocorreu um erro. Tente novamente em alguns instantes."
        await send_response_message(client_config, message.user_id, fallback_message)

async def send_response_message(client_config: Dict[str, Any], user_id: str, message_content: str):
    """Send response message via Evolution API"""
    try:
        evolution_manager = get_evolution_manager()
        
        # Format phone number
        phone_number = f"{user_id}@s.whatsapp.net"
        
        # Send message
        success = await evolution_manager.send_message_for_client(
            client_id=client_config['id'],
            client_config=client_config,
            number=phone_number,
            message=message_content
        )
        
        if success:
            # Store outbound message in session
            session_manager = get_cloud_session_manager()
            bot_message = Message(
                user_id=user_id,
                user_name=client_config.get('agent_name', 'Assistente'),
                message_direction=MessageDirection.OUTBOUND,
                content=message_content,
                timestamp=None,  # Will be set automatically
                metadata={"from_me": True}
            )
            
            await session_manager.update_session(user_id, client_config['id'], bot_message)
            logger.info(f"Response sent successfully to {user_id}")
        else:
            logger.error(f"Failed to send response to {user_id}")
    
    except Exception as e:
        logger.error(f"Error sending response message: {e}")

@router.get("/health")
async def webhook_health():
    """Webhook health check"""
    return {"status": "healthy", "service": "webhook"}

@router.post("/test")
async def test_webhook(test_data: Dict[str, Any]):
    """Test webhook endpoint for development"""
    logger.info(f"Test webhook received: {test_data}")
    return {"status": "received", "data": test_data}