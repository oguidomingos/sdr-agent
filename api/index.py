"""
Basic API handler for Vercel - Working version with real Supabase integration
"""
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import time
import os
import uuid
import requests
import google.generativeai as genai
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import threading
import asyncio
from collections import defaultdict
import time as time_module

# Supabase integration
_supabase_client = None

# Message cooldown system
message_buffer = defaultdict(list)  # {user_phone: [messages]}
cooldown_timers = {}  # {user_phone: timer_object}
COOLDOWN_SECONDS = 90  # 1.5 minutes

def should_process_message_db(user_phone: str, client_id: str, cooldown_seconds: int = 90) -> bool:
    """Check if message should be processed based on database cooldown state"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            print("⚠️ No Supabase client, processing immediately")
            return True
            
        # Check existing cooldown record
        result = supabase.table('message_cooldown')\
            .select('last_message_at, last_processed_at')\
            .eq('user_phone', user_phone)\
            .execute()
        
        now = datetime.now(timezone.utc)
        
        if not result.data:
            print(f"🆕 First message from {user_phone}, creating cooldown record")
            # Create new cooldown record
            supabase.table('message_cooldown').insert({
                'user_phone': user_phone,
                'client_id': client_id,
                'last_message_at': now.isoformat(),
                'cooldown_seconds': cooldown_seconds
            }).execute()
            return False  # Don't process immediately, wait for cooldown
            
        record = result.data[0]
        last_message_at = record['last_message_at']
        if isinstance(last_message_at, str):
            last_message_at = datetime.fromisoformat(last_message_at.replace('Z', '+00:00'))
        if last_message_at.tzinfo is None:
            last_message_at = last_message_at.replace(tzinfo=timezone.utc)
        time_diff = (now - last_message_at).total_seconds()
        
        print(f"⏱️ Last message was {time_diff:.1f}s ago (cooldown: {cooldown_seconds}s)")
        
        return time_diff >= cooldown_seconds
        
    except Exception as e:
        print(f"❌ Error checking cooldown: {e}")
        # If table doesn't exist, process immediately with simple message
        if "does not exist" in str(e):
            print("⚠️ Cooldown table not available, processing message immediately")
            return True
        return True  # Process on error to avoid blocking

def add_message_to_cooldown_db(user_phone: str, message_text: str, instance_name: str, client_config: Dict[str, Any], user_name: str = ""):
    """Add message to database cooldown system"""
    try:
        print(f"📥 Adding message to DB cooldown for {user_phone}: {message_text}")
        
        supabase = get_supabase_client()
        if not supabase:
            print("⚠️ No Supabase client available")
            return
            
        client_id = client_config.get('id')
        now = datetime.now(timezone.utc)
        
        # Get existing cooldown record
        result = supabase.table('message_cooldown')\
            .select('pending_messages')\
            .eq('user_phone', user_phone)\
            .execute()
        
        pending_messages = []
        if result.data:
            pending_messages = result.data[0].get('pending_messages', [])
        
        # Add new message to pending list
        new_message = {
            'text': message_text,
            'timestamp': now.isoformat(),
            'instance_name': instance_name
        }
        pending_messages.append(new_message)
        
        # Update cooldown record
        supabase.table('message_cooldown').upsert({
            'user_phone': user_phone,
            'client_id': client_id,
            'last_message_at': now.isoformat(),
            'pending_messages': pending_messages,
            'cooldown_seconds': COOLDOWN_SECONDS
        }).execute()
        
        print(f"📋 Updated DB cooldown - {len(pending_messages)} pending messages")
        
    except Exception as e:
        print(f"❌ Error adding message to DB cooldown: {e}")

def process_with_gemini_ai(message_text: str, client_config: Dict[str, Any]) -> str:
    """Process message with Gemini AI and return response"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        gemini_key = client_config.get('gemini_api_key')
        if not gemini_key:
            print("⚠️ No Gemini API key configured - v2.10.0")
            return "Desculpe, não consegui processar sua mensagem no momento."
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(client_config.get('gemini_model', 'gemini-2.0-flash'))
        
        # Create prompt with agent configuration
        agent_prompt = client_config.get('agent_prompt', '')
        agent_name = client_config.get('agent_name', 'Assistente')
        
        system_prompt = f"""Você é {agent_name}, um assistente de vendas especializado.
        
{agent_prompt}

Responda de forma natural, conversacional e focada em vendas. 
Sua resposta deve ser concisa (máximo 2-3 parágrafos).
"""
        
        # Generate response
        response = model.generate_content(f"{system_prompt}\n\nMensagem do cliente: {message_text}")
        ai_response = response.text.strip()
        
        print(f"🤖 Gemini response: {ai_response[:100]}...")
        return ai_response
        
    except Exception as e:
        print(f"❌ Error processing with Gemini: {e}")
        return "Desculpe, não consegui processar sua mensagem no momento. Um atendente entrará em contato em breve."

def send_whatsapp_message(user_phone: str, message: str, instance_name: str, client_config: Dict[str, Any]) -> bool:
    """Send WhatsApp message via Evolution API"""
    try:
        import requests
        
        evolution_url = client_config.get('evolution_api_url')
        evolution_key = client_config.get('evolution_api_key')
        
        if not evolution_url or not evolution_key:
            print("⚠️ Evolution API not configured")
            return False
            
        # Clean phone number
        clean_phone = user_phone.replace('@s.whatsapp.net', '')
        
        # Send message
        url = f"{evolution_url}/message/sendText/{instance_name}"
        headers = {
            'Content-Type': 'application/json',
            'apikey': evolution_key
        }
        
        payload = {
            'number': clean_phone,
            'text': message
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"📤 Message sent to {user_phone}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")
        return False

def process_pending_messages_db(user_phone: str, instance_name: str, client_config: Dict[str, Any], current_message: str = None, user_name: str = ""):
    """Process all pending messages from database after cooldown"""
    try:
        print(f"⏰ Processing pending messages from DB for {user_phone}")
        
        supabase = get_supabase_client()
        if not supabase:
            print("⚠️ No Supabase client available")
            # Process current message directly if no DB
            if current_message:
                process_single_message(user_phone, current_message, instance_name, client_config, user_name)
            return
            
        # Get pending messages
        result = supabase.table('message_cooldown')\
            .select('pending_messages')\
            .eq('user_phone', user_phone)\
            .execute()
        
        if not result.data or not result.data[0].get('pending_messages'):
            print(f"⚠️ No pending messages found for {user_phone}")
            # Process current message if provided
            if current_message:
                process_single_message(user_phone, current_message, instance_name, client_config, user_name)
            return
            
        pending_messages = result.data[0]['pending_messages']
        print(f"📨 Found {len(pending_messages)} pending messages")
        
        # Add current message if provided
        if current_message:
            pending_messages.append({
                'text': current_message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        # Combine all messages into context
        combined_text = "\n".join([msg['text'] for msg in pending_messages])
        print(f"📝 Combined message text: {combined_text}")
        
        # Process with AI
        response = process_with_gemini_ai(combined_text, client_config)
        if response:
            send_whatsapp_message(user_phone, response, instance_name, client_config)
        
        # Save messages to database
        client_id = client_config.get('id')
        if client_id:
            for msg in pending_messages:
                save_message_to_database(client_id, user_phone, msg['text'], 'inbound', user_name)
            # Save AI response
            if response:
                save_message_to_database(client_id, user_phone, response, 'outbound', user_name)
        
        # Update cooldown record - clear pending messages and set processed timestamp
        now = datetime.now(timezone.utc)
        supabase.table('message_cooldown').update({
            'pending_messages': [],
            'last_processed_at': now.isoformat()
        }).eq('user_phone', user_phone).execute()
        
        print(f"✅ Processed and cleared {len(pending_messages)} messages for {user_phone}")
        
    except Exception as e:
        print(f"❌ Error processing pending messages: {e}")
        # If table doesn't exist, process current message directly
        if "does not exist" in str(e) and current_message:
            print("⚠️ Cooldown table not available, processing current message")
            process_single_message(user_phone, current_message, instance_name, client_config, user_name)

def process_single_message(user_phone: str, message_text: str, instance_name: str, client_config: Dict[str, Any], user_name: str = ""):
    """Process a single message with AI - fallback when cooldown system unavailable"""
    try:
        print(f"📨 Processing single message: {message_text}")
        
        # Process with AI
        response = process_with_gemini_ai(message_text, client_config)
        if response:
            send_whatsapp_message(user_phone, response, instance_name, client_config)
            
        # Save messages to database
        client_id = client_config.get('id')
        if client_id:
            save_message_to_database(client_id, user_phone, message_text, 'inbound', user_name)
            if response:
                save_message_to_database(client_id, user_phone, response, 'outbound', user_name)
                
        print(f"✅ Successfully processed single message for {user_phone}")
        
    except Exception as e:
        print(f"❌ Error processing single message: {e}")

def get_supabase_client():
    """Get Supabase client instance with robust error handling"""
    global _supabase_client
    
    if _supabase_client is None:
        try:
            # Import supabase module
            from supabase import create_client
            
            url = os.environ.get("SUPABASE_URL", "").strip()
            key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
            
            # Check credentials
            if not url or not key:
                print("❌ Missing Supabase credentials")
                print(f"   URL: {'✅' if url else '❌'}")
                print(f"   KEY: {'✅' if key else '❌'}")
                return None
            
            print(f"🔗 Creating Supabase client...")
            print(f"   URL: {url[:50]}...")
            
            # Create client without immediate connection test
            _supabase_client = create_client(url, key)
            print("✅ Supabase client created successfully")
            
        except ImportError as e:
            print(f"❌ Supabase import failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Supabase client creation failed: {e}")
            _supabase_client = None
            return None
    
    return _supabase_client

def configure_evolution_webhook(instance_name, evolution_url, evolution_api_key):
    """Configure webhook for Evolution API instance"""
    try:
        webhook_url = f"{evolution_url}/webhook/set/{instance_name}"
        
        webhook_payload = {
            "webhook": {
                "url": f"https://sdr-agent-five.vercel.app/api/webhook/whatsapp/{instance_name}",
                "enabled": True,
                "webhookByEvents": True,
                "webhookBase64": False,
                "events": [
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE", 
                    "SEND_MESSAGE",
                    "CONNECTION_UPDATE",
                    "PRESENCE_UPDATE",
                    "QRCODE_UPDATED"
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "apikey": evolution_api_key
        }
        
        print(f"🔗 Configuring webhook for instance: {instance_name}")
        response = requests.post(webhook_url, json=webhook_payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Webhook configured for instance: {instance_name}")
            return True
        else:
            print(f"⚠️ Webhook configuration failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook configuration exception: {e}")
        return False

def reconfigure_existing_webhooks():
    """Reconfigure webhooks for all existing clients"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
            
        # Get all clients with Evolution instances
        result = (supabase.table('clients')
                 .select('*')
                 .neq('evolution_instance', None)
                 .execute())
        
        if not result.data:
            print("No clients with Evolution instances found")
            return True
            
        evolution_url = "https://evolutionapi.centralsupernova.com.br"
        evolution_api_key = os.environ.get("AUTHENTICATION_API_KEY", "")
        
        if not evolution_api_key:
            print("⚠️ AUTHENTICATION_API_KEY not configured")
            return False
            
        success_count = 0
        for client in result.data:
            instance_name = client.get('evolution_instance')
            if instance_name:
                success = configure_evolution_webhook(instance_name, evolution_url, evolution_api_key)
                if success:
                    success_count += 1
                    print(f"✅ Reconfigured webhook for {client.get('name', instance_name)}")
                else:
                    print(f"❌ Failed to reconfigure webhook for {client.get('name', instance_name)}")
        
        print(f"🔧 Reconfigured {success_count} out of {len(result.data)} webhooks")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error reconfiguring webhooks: {e}")
        return False

def create_evolution_instance(client_name, client_id):
    """Create an instance in Evolution API and configure webhook"""
    try:
        evolution_url = "https://evolutionapi.centralsupernova.com.br"
        evolution_api_key = os.environ.get("AUTHENTICATION_API_KEY", "")
        evolution_global_key = os.environ.get("AUTHENTICATION_API_KEY", "")
        
        if not evolution_api_key:
            print("⚠️ AUTHENTICATION_API_KEY not configured")
            return None
        
        # Generate instance name based on client (shorter name)
        instance_name = f"sdr_{client_id[:8]}"
        
        # Step 1: Create instance
        url = f"{evolution_url}/instance/create"
        
        payload = {
            "instanceName": instance_name,
            "token": evolution_global_key,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        headers = {
            "Content-Type": "application/json",
            "apikey": evolution_api_key
        }
        
        print(f"🔗 Creating Evolution instance: {instance_name}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Evolution instance created: {instance_name}")
            
            # Step 2: Configure webhook automatically
            webhook_configured = configure_evolution_webhook(instance_name, evolution_url, evolution_api_key)
            
            if webhook_configured:
                print(f"✅ Webhook configured for new instance: {instance_name}")
            else:
                print(f"❌ Failed to configure webhook for instance: {instance_name}")
            
            return {
                "instance_name": instance_name,
                "instance_data": data,
                "webhook_configured": webhook_configured
            }
        else:
            print(f"❌ Evolution API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Evolution API exception: {e}")
        return None

def get_client_by_instance(instance_name: str) -> Optional[Dict[str, Any]]:
    """Get client configuration by Evolution instance name"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
            
        result = (supabase.table('clients')
                 .select('*')
                 .eq('evolution_instance', instance_name)
                 .execute())
        
        if result.data:
            return result.data[0]
        return None
        
    except Exception as e:
        print(f"❌ Error getting client by instance: {e}")
        return None

def send_whatsapp_message_simple(message: str, phone_number: str, instance_name: str, evolution_api_key: str) -> bool:
    """Send message via Evolution API"""
    try:
        import requests
        
        evolution_url = "https://evolutionapi.centralsupernova.com.br"
        url = f"{evolution_url}/message/sendText/{instance_name}"
        
        payload = {
            "number": phone_number,
            "text": message
        }
        
        headers = {
            "Content-Type": "application/json",
            "apikey": evolution_api_key
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            print(f"✅ Message sent to {phone_number}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")
        return False

def process_message_with_ai(message_text: str, user_phone: str, client_config: Dict[str, Any]) -> Optional[str]:
    """Process message with Gemini AI using client configuration"""
    try:
        gemini_api_key = client_config.get('gemini_api_key')
        gemini_model = client_config.get('gemini_model', 'gemini-2.0-flash-exp')
        agent_persona = client_config.get('agent_persona', '')
        
        if not gemini_api_key:
            print("⚠️ No Gemini API key configured for client")
            return None
            
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(gemini_model)
        
        # Build context prompt
        system_prompt = f"""
Você é um assistente de vendas inteligente. 

PERSONA DO AGENTE:
{agent_persona}

INSTRUÇÕES:
- Use a persona fornecida para responder
- Seja natural e conversacional
- Faça perguntas para qualificar o lead
- Mantenha respostas concisas (máximo 200 caracteres)
- Use o método SPIN Selling quando apropriado

MENSAGEM DO USUÁRIO: {message_text}

Responda de forma profissional e útil:
"""
        
        # Generate response
        response = model.generate_content(system_prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error processing message with AI: {e}")
        return None

def process_buffered_messages(user_phone: str, instance_name: str, client_config: Dict[str, Any]):
    """Process all buffered messages for a user after cooldown period"""
    try:
        print(f"⏰ Processing buffered messages for {user_phone}")
        
        # Get all buffered messages for this user
        messages = message_buffer.get(user_phone, [])
        
        if not messages:
            print(f"⚠️ No messages found in buffer for {user_phone}")
            return
            
        # Combine all messages into one context
        combined_text = "\n".join([msg['text'] for msg in messages])
        print(f"📝 Combined message text: {combined_text}")
        
        # Save all incoming messages to database
        for msg in messages:
            save_message_to_database(
                client_config['id'],
                user_phone,
                msg['text'],
                'inbound'
            )
        
        # Process combined message with AI
        ai_response = process_message_with_ai(
            combined_text,
            user_phone,
            client_config
        )
        
        if ai_response:
            print(f"🤖 AI generated response for buffered messages: {ai_response}")
            
            # Send AI response via WhatsApp using client config
            success = send_whatsapp_message(user_phone, ai_response, instance_name, client_config)
            
            if success:
                # Save outgoing message to database
                save_message_to_database(
                    client_config['id'],
                    user_phone,
                    ai_response,
                    'outbound'
                )
                print(f"✅ AI response sent and saved for buffered messages")
            else:
                print(f"❌ Failed to send AI response for buffered messages")
        else:
            print(f"⚠️ No AI response generated for buffered messages")
            
        # Clear buffer and timer for this user
        if user_phone in message_buffer:
            del message_buffer[user_phone]
        if user_phone in cooldown_timers:
            del cooldown_timers[user_phone]
            
        print(f"🧹 Cleared buffer and timer for {user_phone}")
        
    except Exception as e:
        print(f"❌ Error processing buffered messages: {e}")
        # Clean up even if there's an error
        if user_phone in message_buffer:
            del message_buffer[user_phone]
        if user_phone in cooldown_timers:
            del cooldown_timers[user_phone]

def add_message_to_buffer(user_phone: str, message_text: str, instance_name: str, client_config: Dict[str, Any]):
    """Add message to buffer and start/reset cooldown timer"""
    try:
        print(f"📥 Adding message to buffer for {user_phone}: {message_text}")
        
        # Add message to buffer
        message_data = {
            'text': message_text,
            'timestamp': time_module.time(),
            'instance_name': instance_name,
            'client_config': client_config
        }
        message_buffer[user_phone].append(message_data)
        
        # Cancel existing timer if it exists
        if user_phone in cooldown_timers:
            cooldown_timers[user_phone].cancel()
            print(f"⏲️ Cancelled existing timer for {user_phone}")
        
        # Start new timer
        timer = threading.Timer(
            COOLDOWN_SECONDS,
            process_buffered_messages,
            args=[user_phone, instance_name, client_config]
        )
        cooldown_timers[user_phone] = timer
        timer.start()
        
        print(f"⏲️ Started {COOLDOWN_SECONDS}s cooldown timer for {user_phone}")
        
    except Exception as e:
        print(f"❌ Error adding message to buffer: {e}")

def save_message_to_database(client_id: str, user_phone: str, message_text: str, direction: str, user_name: str = "") -> bool:
    """Save message to Supabase"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
            
        message_data = {
            "client_id": client_id,
            "user_id": user_phone,
            "user_name": user_name,
            "message_direction": direction,
            "content": message_text,
            "message_metadata": {},
            "status": "none",
            "lead_score": 0
        }
        
        result = supabase.table('messages').insert(message_data).execute()
        return bool(result.data)
        
    except Exception as e:
        print(f"❌ Error saving message: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self, status_code=200):
        """Send CORS headers"""
        self.send_response(status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-type', 'application/json')
        # Add caching headers for better performance
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers"""
        self._send_cors_headers(status_code)
        self.wfile.write(json.dumps(data).encode())
    
    def _get_request_body(self):
        """Get request body as JSON"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            print(f"🔍 _get_request_body called - Content-Length: {content_length}")
            if content_length > 0:
                body = self.rfile.read(content_length)
                print(f"🔍 Raw body bytes: {body}")
                decoded_body = body.decode('utf-8')
                print(f"🔍 Decoded body: {decoded_body}")
                # Try to parse JSON
                parsed_body = json.loads(decoded_body)
                print(f"🔍 Parsed JSON: {parsed_body}")
                return parsed_body
            else:
                print("🔍 No content length - returning empty dict")
            return {}
        except json.JSONDecodeError as e:
            # Return error info for debugging
            return {"_json_error": str(e), "_raw_body": decoded_body[:200] if 'decoded_body' in locals() else "no_body"}
        except Exception as e:
            # Return generic error info
            return {"_error": str(e)}
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse URL and query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.strip('/')
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Remove /api prefix if present
        if path.startswith('api/'):
            path = path[4:]
        
        # Remove trailing slash
        path = path.rstrip('/')
        
        if path == 'health' or path == '':
            # Check environment variables
            supabase_url = os.environ.get("SUPABASE_URL", "").strip()
            supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
            jwt_secret = os.environ.get("JWT_SECRET", "").strip()
            
            # Test Supabase connection
            supabase = get_supabase_client()
            supabase_status = "not_connected"
            
            if supabase:
                try:
                    # Test actual connectivity
                    result = supabase.table('users').select('id').limit(1).execute()
                    supabase_status = "connected"
                except Exception as e:
                    supabase_status = f"error: {str(e)[:50]}"
            
            self._send_json_response({
                "status": "healthy",
                "version": "2.9.0",
                "cors": "enabled",
                "vercel": os.environ.get("VERCEL", "0") == "1",
                "supabase": supabase_status,
                "mode": "supabase_integrated",
                "environment_vars": {
                    "SUPABASE_URL": "✅" if supabase_url else "❌",
                    "SUPABASE_SERVICE_ROLE_KEY": "✅" if supabase_key else "❌",
                    "JWT_SECRET": "✅" if jwt_secret else "❌"
                }
            })
        elif path == 'auth/me':
            # Get current user info
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            # Extract token and return REAL user data for our test user
            token = auth_header.replace('Bearer ', '')
            
            # Check if this is our test user token
            if 'oguigodomingos' in token or 'guigo' in token.lower():
                # Return REAL user data
                self._send_json_response({
                    "id": "9eadc58c-4dd0-4ce6-9dd4-1cf55169c9db",
                    "email": "oguigodomingos@gmail.com",
                    "first_name": "Guigo",
                    "last_name": "Domingos",
                    "status": "active",
                    "plan": "free",
                    "created_at": "2025-01-08T12:00:00Z"
                })
            else:
                # Generic user for other tokens
                self._send_json_response({
                    "id": "user_123",
                    "email": "user@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "status": "active",
                    "plan": "free",
                    "created_at": "2025-01-08T12:00:00Z"
                })
        elif path == 'clients':
            # List clients
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            # Get query parameters
            skip = int(query_params.get('skip', ['0'])[0])
            limit = int(query_params.get('limit', ['100'])[0])
            
            # Get Supabase client
            supabase = get_supabase_client()
            if not supabase:
                # Fallback to empty list if Supabase not available
                self._send_json_response({
                    "clients": [],
                    "total": 0,
                    "skip": skip,
                    "limit": limit
                })
                return
            
            try:
                # Get ALL clients from Supabase (temporarily for debug)
                result = (supabase.table('clients')
                         .select('*')
                         .range(skip, skip + limit - 1)
                         .execute())
                
                # Get total count of ALL clients
                count_result = (supabase.table('clients')
                               .select('id', count='exact')
                               .execute())
                
                clients = result.data or []
                total = count_result.count or 0
                
                self._send_json_response({
                    "clients": clients,
                    "total": total,
                    "skip": skip,
                    "limit": limit
                })
                
            except Exception as e:
                self._send_json_response({
                    "error": f"Database error: {str(e)}",
                    "debug_info": {"supabase_error": str(e)}
                }, 500)
        elif path == 'webhook/reconfigure':
            # Endpoint to reconfigure all existing webhooks
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            success = reconfigure_existing_webhooks()
            self._send_json_response({
                "status": "success" if success else "partial_failure",
                "message": "Webhook reconfiguration completed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        elif path == 'test-ai-processing':
            # Test endpoint for AI processing
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            # Simulate webhook processing
            try:
                client_config = {
                    "id": "3f30b5be-2e5d-4bf8-8c76-24f39d1d548e",
                    "evolution_api_key": "509dbd54-c20c-4a5b-b889-a0494a861f5a",
                    "gemini_api_key": "AIzaSyASsQw-arw3Mqp7q01qy37Wxkrj-Lo0oHk",
                    "gemini_model": "gemini-2.0-flash-exp",
                    "agent_persona": "Sou um assistente para testar as melhorias no webhook do Evolution API."
                }
                
                # Test AI processing
                ai_response = process_message_with_ai("oi", "5561936180578@s.whatsapp.net", client_config)
                print(f"🤖 AI Test Response: {ai_response}")
                
                # Test sending message
                if ai_response:
                    success = send_whatsapp_message_simple(
                        ai_response,
                        "5561936180578",
                        "sdr_3f30b5be", 
                        client_config["evolution_api_key"]
                    )
                    
                    self._send_json_response({
                        "status": "success",
                        "ai_response": ai_response,
                        "message_sent": success,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                else:
                    self._send_json_response({
                        "status": "error",
                        "error": "AI did not generate response",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, 500)
                    
            except Exception as e:
                print(f"❌ Test AI processing error: {e}")
                self._send_json_response({
                    "status": "error", 
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, 500)
        elif path.startswith('clients/') and path.endswith('/qrcode'):
            # Get QR code for specific client
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            # Extract client ID from path (clients/{id}/qrcode)
            path_parts = path.split('/')
            if len(path_parts) >= 2:
                client_id = path_parts[1]
                
                # Get client info from Supabase
                supabase = get_supabase_client()
                if not supabase:
                    self._send_json_response({
                        "error": "Database not available"
                    }, 500)
                    return
                
                try:
                    result = (supabase.table('clients')
                             .select('*')
                             .eq('id', client_id)
                             .execute())
                    
                    if not result.data:
                        self._send_json_response({
                            "error": "Client not found"
                        }, 404)
                        return
                    
                    client = result.data[0]
                    evolution_instance = client.get('evolution_instance')
                    
                    if not evolution_instance:
                        self._send_json_response({
                            "error": "No Evolution instance configured"
                        }, 400)
                        return
                    
                    # Get QR code from Evolution API
                    try:
                        evolution_api_key = os.environ.get("AUTHENTICATION_API_KEY", "")
                        if not evolution_api_key:
                            self._send_json_response({
                                "error": "Evolution API key not configured"
                            }, 500)
                            return
                        
                        evolution_url = "https://evolutionapi.centralsupernova.com.br"
                        qr_url = f"{evolution_url}/instance/connect/{evolution_instance}"
                        headers = {"apikey": evolution_api_key}
                        
                        qr_response = requests.get(qr_url, headers=headers, timeout=10)
                        
                        if qr_response.status_code == 200:
                            qr_data = qr_response.json()
                            self._send_json_response({
                                "client_id": client_id,
                                "client_name": client.get('name'),
                                "evolution_instance": evolution_instance,
                                "qr_code": qr_data.get('code'),
                                "qr_base64": qr_data.get('base64'),
                                "status": "ready"
                            })
                        else:
                            self._send_json_response({
                                "error": f"Failed to get QR code: {qr_response.status_code}",
                                "evolution_instance": evolution_instance
                            }, 500)
                            
                    except Exception as e:
                        self._send_json_response({
                            "error": f"Error getting QR code: {str(e)}",
                            "evolution_instance": evolution_instance
                        }, 500)
                        
                except Exception as e:
                    self._send_json_response({
                        "error": f"Database error: {str(e)}"
                    }, 500)
            else:
                self._send_json_response({
                    "error": "Invalid client ID"
                }, 400)
        elif path.startswith('webhook/whatsapp'):
            # GET request to webhook - for testing purposes
            self._send_json_response({
                "message": "Webhook endpoint is active",
                "path": path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "ready"
            })
        else:
            self._send_json_response({
                "error": "Endpoint not found",
                "path": self.path,
                "method": "GET",
                "available_endpoints": ["health", "auth/me", "clients"]
            }, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        # FORCE LOG - POST REQUEST DEBUG
        print(f"🚨 POST REQUEST TO: {self.path}")
        
        # Parse URL and query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.strip('/')
        
        # Remove /api prefix if present
        if path.startswith('api/'):
            path = path[4:]
        
        # Remove trailing slash
        path = path.rstrip('/')
        
        body = self._get_request_body()
        
        if path == 'auth/register':
            # User registration
            email = body.get('email', '')
            password = body.get('password', '')
            first_name = body.get('first_name', '')
            last_name = body.get('last_name', '')
            
            if not email or not password:
                self._send_json_response({
                    "error": "Email and password are required",
                    "code": "MISSING_FIELDS"
                }, 400)
                return
            
            # Return success for registration
            self._send_json_response({
                "id": f"user_{hash(email) % 10000}",
                "email": email,
                "first_name": first_name,
                "last_name": last_name or "",
                "status": "active",
                "plan": "free",
                "created_at": "2025-01-08T12:00:00Z"
            }, 201)
            
        elif path == 'auth/login':
            # User login
            email = body.get('email', '')
            password = body.get('password', '')
            
            if not email or not password:
                self._send_json_response({
                    "error": "Email and password are required"
                }, 400)
                return
            
            # Check for our test user
            if email == 'oguigodomingos@gmail.com' and password == '180121430':
                # Return token with user info embedded
                self._send_json_response({
                    "access_token": f"jwt_token_guigo_{hash(email) % 10000}_{int(time.time())}",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user_id": "9eadc58c-4dd0-4ce6-9dd4-1cf55169c9db",
                    "email": email
                })
            else:
                # Generic login for other users
                self._send_json_response({
                    "access_token": f"jwt_token_{hash(email) % 10000}_{int(time.time())}",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user_id": f"user_{hash(email) % 10000}",
                    "email": email
                })
        elif path == 'clients':
            # Create client
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            # Check for parsing errors first
            if '_json_error' in body or '_error' in body:
                self._send_json_response({
                    "error": "Invalid JSON in request body",
                    "debug_info": body
                }, 400)
                return
            
            name = body.get('name', '')
            if not name:
                self._send_json_response({
                    "error": "Name is required",
                    "debug_body": body  # Include body in error for debugging
                }, 400)
                return
            
            # Generate unique domain if empty to avoid constraint violations
            domain = body.get('domain', '')
            if not domain:
                domain = f"{name.lower().replace(' ', '-')}-{int(time.time())}.sdr-agent.com"
            
            # Get Supabase client
            supabase = get_supabase_client()
            if not supabase:
                # Fallback to mock data if Supabase not available
                client_id = f"client_{int(time.time())}_{hash(name) % 1000}"
                current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                
                client_data = {
                    "id": client_id,
                    "name": name,
                    "description": body.get('description', ''),
                    "domain": domain,
                    "status": "active",
                    "whatsapp_number": body.get('whatsapp_number', ''),
                    "evolution_api_url": body.get('evolution_api_url', ''),
                    "evolution_api_key": body.get('evolution_api_key', ''),
                    "evolution_instance": body.get('evolution_instance', ''),
                    "gemini_api_key": body.get('gemini_api_key', ''),
                    "gemini_model": body.get('gemini_model', 'gemini-2.0-flash'),
                    "session_timeout": body.get('session_timeout', 3600),
                    "max_history": body.get('max_history', 50),
                    "context_window_size": body.get('context_window_size', 4000),
                    "agent_name": body.get('agent_name', 'Assistant'),
                    "agent_persona": body.get('agent_persona', ''),
                    "welcome_message": body.get('welcome_message', 'Hello! How can I help you?'),
                    "logo_url": body.get('logo_url', ''),
                    "contact_email": body.get('contact_email', ''),
                    "contact_phone": body.get('contact_phone', ''),
                    "business_hours": body.get('business_hours', {}),
                    "timezone": body.get('timezone', 'America/Sao_Paulo'),
                    "ai_temperature": body.get('ai_temperature', 70),
                    "rate_limit_enabled": body.get('rate_limit_enabled', True),
                    "rate_limit_calls": body.get('rate_limit_calls', 100),
                    "rate_limit_period": body.get('rate_limit_period', 3600),
                    "created_at": current_time,
                    "updated_at": current_time,
                    "owner_id": "9eadc58c-4dd0-4ce6-9dd4-1cf55169c9db"  # Your user ID
                }
                
                self._send_json_response(client_data, 201)
                return
            
            # Create client in Supabase
            try:
                client_id = str(uuid.uuid4())
                current_time = datetime.now(timezone.utc).isoformat()
                
                client_data = {
                    "id": client_id,
                    "owner_id": "9eadc58c-4dd0-4ce6-9dd4-1cf55169c9db",  # Your user ID
                    "name": name,
                    "description": body.get('description', ''),
                    "domain": domain,
                    "status": "active",
                    "whatsapp_number": body.get('whatsapp_number', ''),
                    "evolution_api_url": body.get('evolution_api_url', ''),
                    "evolution_api_key": body.get('evolution_api_key', ''),
                    "evolution_instance": body.get('evolution_instance', ''),
                    "gemini_api_key": body.get('gemini_api_key', ''),
                    "gemini_model": body.get('gemini_model', 'gemini-2.0-flash'),
                    "session_timeout": body.get('session_timeout', 3600),
                    "max_history": body.get('max_history', 50),
                    "context_window_size": body.get('context_window_size', 4000),
                    "agent_name": body.get('agent_name', 'Assistant'),
                    "agent_persona": body.get('agent_persona', ''),
                    "welcome_message": body.get('welcome_message', 'Hello! How can I help you?'),
                    "logo_url": body.get('logo_url', ''),
                    "contact_email": body.get('contact_email', ''),
                    "contact_phone": body.get('contact_phone', ''),
                    "business_hours": body.get('business_hours', {}),
                    "timezone": body.get('timezone', 'America/Sao_Paulo'),
                    "ai_temperature": body.get('ai_temperature', 70),
                    "rate_limit_enabled": body.get('rate_limit_enabled', True),
                    "rate_limit_calls": body.get('rate_limit_calls', 100),
                    "rate_limit_period": body.get('rate_limit_period', 3600)
                }
                
                # Insert into Supabase
                result = supabase.table('clients').insert(client_data).execute()
                
                if result.data and len(result.data) > 0:
                    created_client = result.data[0]
                    
                    # Try to create Evolution API instance
                    evolution_result = create_evolution_instance(name, client_id)
                    
                    if evolution_result:
                        # Update client with Evolution instance info
                        try:
                            update_data = {
                                "evolution_instance": evolution_result["instance_name"],
                                "evolution_api_url": "https://evolutionapi.centralsupernova.com.br"
                            }
                            
                            updated_result = supabase.table('clients').update(update_data).eq('id', client_id).execute()
                            
                            if updated_result.data:
                                created_client = updated_result.data[0]
                                print(f"✅ Client updated with Evolution instance: {evolution_result['instance_name']}")
                        except Exception as e:
                            print(f"⚠️ Failed to update client with Evolution info: {e}")
                    
                    # Return the created client data
                    self._send_json_response(created_client, 201)
                else:
                    self._send_json_response({
                        "error": "Failed to create client in database"
                    }, 500)
                    
            except Exception as e:
                self._send_json_response({
                    "error": f"Database error: {str(e)}",
                    "debug_info": {"supabase_error": str(e)}
                }, 500)
        elif path == 'webhook/reconfigure':
            # Endpoint to reconfigure all existing webhooks
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            success = reconfigure_existing_webhooks()
            self._send_json_response({
                "status": "success" if success else "partial_failure",
                "message": "Webhook reconfiguration completed",
                        "timestamp": datetime.now(timezone.utc).isoformat()
            })
        elif path == 'webhook/whatsapp' or path.startswith('webhook/whatsapp/'):
            # Webhook endpoint for Evolution API with AI processing
            try:
                # Extract instance from URL if provided (webhook/whatsapp/instance_name)
                url_instance = None
                if path.startswith('webhook/whatsapp/'):
                    url_parts = path.split('/')
                    if len(url_parts) >= 3:
                        url_instance = url_parts[2]
                
                # FORCE PRINT - ESSENTIAL DEBUG INFO
                print("=" * 80)
                print(f"🚨 WEBHOOK RECEIVED AT {datetime.now(timezone.utc).isoformat()}")
                print(f"🚨 METHOD: {getattr(self, 'command', 'UNKNOWN')}")
                print(f"🚨 FULL PATH: {self.path}")
                print(f"🚨 PARSED PATH: {path}")
                print(f"🚨 URL INSTANCE: {url_instance}")
                print(f"🚨 CONTENT-TYPE: {self.headers.get('Content-Type', 'NONE')}")
                print(f"🚨 CONTENT-LENGTH: {self.headers.get('Content-Length', 'NONE')}")
                print(f"🚨 RAW BODY TYPE: {type(body)}")
                print(f"🚨 RAW BODY: {body}")
                print("=" * 80)
                
                # Additional body analysis
                if isinstance(body, dict) and body:
                    print(f"🔍 BODY KEYS: {list(body.keys())}")
                    for key, value in body.items():
                        print(f"🔍 {key}: {value}")
                elif body == {}:
                    print("⚠️ EMPTY BODY RECEIVED")
                else:
                    print(f"⚠️ UNUSUAL BODY FORMAT: {body}")
                
                # Process different webhook events
                event_type = body.get('event', '')
                instance_data = body.get('instance', {})
                
                # Handle different instance formats
                if isinstance(instance_data, str):
                    # Instance is just a string (instance name)
                    instance_name_from_data = instance_data
                    instance_data = {'instanceName': instance_data}
                else:
                    # Instance is an object
                    instance_name_from_data = instance_data.get('instanceName', '')
                data = body.get('data', {})
                
                if event_type in ['MESSAGES_UPSERT', 'MESSAGES_UPDATE', 'messages.upsert', 'messages.update']:
                    # Handle incoming message with AI processing (support both formats)
                    print(f"🔍 Processing message event: {event_type}")
                    
                    # Handle the new webhook format where data contains key directly
                    message_key = data.get('key', {})
                    message_content = data.get('message', {})
                    
                    # If no key in data, try the old format
                    if not message_key:
                        message = data.get('message', {})
                        message_key = message.get('key', {})
                        from_user = message_key.get('remoteJid', '')
                        from_me = message_key.get('fromMe', False)
                    else:
                        # New format: key and message are directly in data
                        from_user = message_key.get('remoteJid', '')
                        from_me = message_key.get('fromMe', False)
                    
                    print(f"🔍 Message key: {message_key}")
                    print(f"🔍 Message content: {message_content}")
                    print(f"🔍 From user: {from_user}")
                    print(f"🔍 From me: {from_me}")
                    
                    # Skip messages sent by us
                    if from_me:
                        print(f"📤 Ignoring outbound message")
                        self._send_json_response({
                            "status": "success",
                            "received": True,
                            "action": "ignored_outbound"
                        })
                        return
                    
                    # Extract message text with new webhook format
                    message_text = (
                        message_content.get('conversation') or 
                        message_content.get('extendedTextMessage', {}).get('text') or
                        message_content.get('text') or
                        data.get('text') or
                        ''
                    )
                    
                    # Extract user name from webhook data
                    user_name = (
                        data.get('pushName') or
                        data.get('senderName') or
                        body.get('pushName') or
                        ''
                    )
                    
                    print(f"🔍 Message content structure: {message_content}")
                    print(f"🔍 Extracted message text: '{message_text}'")
                    
                    if not message_text:
                        print(f"⚠️ No text content found in message")
                        self._send_json_response({
                            "status": "success",
                            "received": True,
                            "action": "no_text_content"
                        })
                        return
                    
                    print(f"📩 New message from {from_user}: {message_text}")
                    
                    # Get instance name from URL or webhook data (with new format support)
                    instance_name = url_instance or instance_name_from_data or instance_data.get('instanceName', '')
                    if not instance_name:
                        print(f"⚠️ No instance name in URL or webhook data")
                        self._send_json_response({
                            "status": "success", 
                            "received": True,
                            "action": "no_instance_name"
                        })
                        return
                    
                    # Get client configuration by instance
                    client_config = get_client_by_instance(instance_name)
                    if not client_config:
                        print(f"⚠️ No client found for instance: {instance_name}")
                        self._send_json_response({
                            "status": "success",
                            "received": True,
                            "action": "client_not_found"
                        })
                        return
                    
                    print(f"🔍 Found client: {client_config.get('name', 'Unknown')}")
                    
                    # Use database-based cooldown system
                    client_id = client_config.get('id')
                    should_process = should_process_message_db(from_user, client_id, COOLDOWN_SECONDS)
                    
                    if should_process:
                        print(f"✅ Processing message immediately (cooldown elapsed)")
                        process_pending_messages_db(from_user, instance_name, client_config, message_text, user_name)
                    else:
                        print(f"⏳ Adding to cooldown buffer (within cooldown period)")
                        add_message_to_cooldown_db(from_user, message_text, instance_name, client_config, user_name)
                    
                elif event_type == 'CONNECTION_UPDATE':
                    # Handle connection status updates
                    state = data.get('state', '')
                    print(f"🔗 Connection update: {state}")
                    
                elif event_type == 'SEND_MESSAGE':
                    # Handle sent message events
                    print(f"📤 Message sent event")
                
                # Always return success to Evolution API
                self._send_json_response({
                    "status": "success",
                    "received": True,
                    "event": event_type,
                    "processed": True,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
            except Exception as e:
                print(f"❌ Webhook processing error: {e}")
                # Still return success to avoid Evolution API retries
                self._send_json_response({
                    "status": "error",
                    "error": str(e),
                    "received": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        else:
            self._send_json_response({
                "error": "Endpoint not found",
                "path": self.path,
                "method": "POST",
                "available_endpoints": ["auth/register", "auth/login", "clients/", "webhook/whatsapp"]
            }, 404)
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def do_PUT(self):
        """Handle PUT requests"""
        self._send_json_response({
            "error": "PUT method not implemented",
            "path": self.path,
            "method": "PUT"
        }, 405)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        # Parse URL and query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.strip('/')
        
        # Remove /api prefix if present
        if path.startswith('api/'):
            path = path[4:]
        
        # Remove trailing slash
        path = path.rstrip('/')
        
        if path.startswith('clients/'):
            # Delete specific client
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_json_response({
                    "error": "Authentication required"
                }, 401)
                return
            
            # Extract client ID from path
            client_id = path.split('/')[-1]
            if not client_id:
                self._send_json_response({
                    "error": "Client ID required"
                }, 400)
                return
            
            # Get Supabase client
            supabase = get_supabase_client()
            if not supabase:
                self._send_json_response({
                    "error": "Database not available"
                }, 500)
                return
            
            try:
                # First, get client info to delete Evolution instance
                client_result = (supabase.table('clients')
                               .select('*')
                               .eq('id', client_id)
                               .execute())
                
                if not client_result.data:
                    self._send_json_response({
                        "error": "Client not found"
                    }, 404)
                    return
                
                client = client_result.data[0]
                evolution_instance = client.get('evolution_instance')
                
                # Delete from Evolution API if instance exists
                if evolution_instance:
                    try:
                        evolution_api_key = os.environ.get("AUTHENTICATION_API_KEY", "")
                        if evolution_api_key:
                            evolution_url = "https://evolutionapi.centralsupernova.com.br"
                            delete_url = f"{evolution_url}/instance/delete/{evolution_instance}"
                            headers = {"apikey": evolution_api_key}
                            
                            print(f"🗑️ Deleting Evolution instance: {evolution_instance}")
                            delete_response = requests.delete(delete_url, headers=headers, timeout=10)
                            
                            if delete_response.status_code == 200:
                                print(f"✅ Evolution instance deleted: {evolution_instance}")
                            else:
                                print(f"⚠️ Failed to delete Evolution instance: {delete_response.status_code}")
                    except Exception as e:
                        print(f"⚠️ Error deleting Evolution instance: {e}")
                
                # Delete from Supabase
                delete_result = (supabase.table('clients')
                               .delete()
                               .eq('id', client_id)
                               .execute())
                
                if delete_result.data:
                    print(f"✅ Client deleted: {client['name']} ({client_id})")
                    self._send_json_response({
                        "message": "Client deleted successfully",
                        "client_id": client_id,
                        "evolution_instance": evolution_instance
                    })
                else:
                    self._send_json_response({
                        "error": "Failed to delete client"
                    }, 500)
                    
            except Exception as e:
                print(f"❌ Error deleting client: {e}")
                self._send_json_response({
                    "error": f"Database error: {str(e)}"
                }, 500)
        else:
            self._send_json_response({
                "error": "DELETE endpoint not found",
                "path": self.path,
                "method": "DELETE",
                "available_endpoints": ["clients/{id}"]
            }, 404)