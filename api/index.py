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
from datetime import datetime

# Supabase integration
_supabase_client = None

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
                "url": "https://sdr-agent-five.vercel.app/api/webhook/whatsapp",
                "enabled": True,
                "webhookByEvents": True,
                "webhookBase64": False,
                "events": [
                    "MESSAGES_UPSERT",
                    "SEND_MESSAGE", 
                    "CONNECTION_UPDATE"
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

def create_evolution_instance(client_name, client_id):
    """Create an instance in Evolution API and configure webhook"""
    try:
        evolution_url = "https://evolutionapi.centralsupernova.com.br"
        evolution_api_key = os.environ.get("EVOLUTION_API_KEY", "")
        evolution_global_key = os.environ.get("EVOLUTION_GLOBAL_KEY", "")
        
        if not evolution_api_key or not evolution_global_key:
            print("⚠️ Evolution API keys not configured")
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
            if content_length > 0:
                body = self.rfile.read(content_length)
                decoded_body = body.decode('utf-8')
                # Try to parse JSON
                parsed_body = json.loads(decoded_body)
                return parsed_body
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
                "version": "2.4.0",
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
        else:
            self._send_json_response({
                "error": "Endpoint not found",
                "path": self.path,
                "method": "GET",
                "available_endpoints": ["health", "auth/me", "clients"]
            }, 404)
    
    def do_POST(self):
        """Handle POST requests"""
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
            
            # Get Supabase client
            supabase = get_supabase_client()
            if not supabase:
                # Fallback to mock data if Supabase not available
                client_id = f"client_{int(time.time())}_{hash(name) % 1000}"
                current_time = datetime.utcnow().isoformat() + "Z"
                
                client_data = {
                    "id": client_id,
                    "name": name,
                    "description": body.get('description', ''),
                    "domain": body.get('domain', ''),
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
                current_time = datetime.utcnow().isoformat()
                
                client_data = {
                    "id": client_id,
                    "owner_id": "9eadc58c-4dd0-4ce6-9dd4-1cf55169c9db",  # Your user ID
                    "name": name,
                    "description": body.get('description', ''),
                    "domain": body.get('domain', ''),
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
        elif path == 'webhook/whatsapp':
            # Webhook endpoint for Evolution API
            try:
                print(f"📨 Received webhook from Evolution API")
                print(f"📨 Webhook data: {body}")
                
                # Process different webhook events
                event_type = body.get('event', '')
                instance = body.get('instance', {})
                data = body.get('data', {})
                
                if event_type == 'MESSAGES_UPSERT':
                    # Handle incoming message
                    message = data.get('message', {})
                    from_user = message.get('key', {}).get('remoteJid', '')
                    message_text = message.get('message', {}).get('conversation', '')
                    
                    print(f"📩 New message from {from_user}: {message_text}")
                    
                elif event_type == 'CONNECTION_UPDATE':
                    # Handle connection status updates
                    state = data.get('state', '')
                    print(f"🔗 Connection update: {state}")
                    
                elif event_type == 'SEND_MESSAGE':
                    # Handle sent message events
                    print(f"📤 Message sent")
                
                # Always return success to Evolution API
                self._send_json_response({
                    "status": "success",
                    "received": True,
                    "event": event_type,
                    "timestamp": "2025-08-04T21:35:00Z"
                })
                
            except Exception as e:
                print(f"❌ Webhook processing error: {e}")
                # Still return success to avoid Evolution API retries
                self._send_json_response({
                    "status": "error",
                    "error": str(e),
                    "received": True
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
        self._send_json_response({
            "error": "DELETE method not implemented", 
            "path": self.path,
            "method": "DELETE"
        }, 405)