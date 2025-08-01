"""
Messages list endpoint for Vercel serverless deployment
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import jwt
import os

from src.core.supabase_db import get_supabase_db

app = FastAPI()
security = HTTPBearer()

class MessageResponse(BaseModel):
    id: str
    client_id: str
    user_id: str
    user_name: Optional[str]
    message_direction: str
    content: str
    timestamp: str
    message_metadata: Optional[Dict[str, Any]]
    status: str
    conversation_stage: Optional[str]
    lead_score: int

class MessageStats(BaseModel):
    total_messages: int
    inbound_messages: int
    outbound_messages: int
    qualified_leads: int
    active_conversations: int
    date_range: Dict[str, str]

# JWT configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "your-jwt-secret-here")
JWT_ALGORITHM = "HS256"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/", response_model=List[MessageResponse])
async def get_messages(
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by message status"),
    date_from: Optional[date] = Query(None, description="Filter messages from this date"),
    date_to: Optional[date] = Query(None, description="Filter messages until this date"),
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of messages to return"),
    token_data: dict = Depends(verify_token)
):
    """Get messages with filtering options"""
    db = get_supabase_db()
    
    # If client_id is provided, verify user owns the client
    if client_id:
        client = await db.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        if client['owner_id'] != token_data['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        messages = await db.get_messages_by_client(client_id, limit=limit + skip)
    else:
        # Get messages from all user's clients
        user_clients = await db.get_clients_by_owner(token_data['user_id'])
        client_ids = [client['id'] for client in user_clients]
        
        if not client_ids:
            return []
        
        # For now, get messages from first client (can be enhanced to get from all)
        messages = await db.get_messages_by_client(client_ids[0], limit=limit + skip)
    
    # Apply additional filters
    filtered_messages = messages
    
    if user_id:
        filtered_messages = [msg for msg in filtered_messages if msg.get('user_id') == user_id]
    
    if status:
        filtered_messages = [msg for msg in filtered_messages if msg.get('status') == status]
    
    if date_from or date_to:
        def filter_by_date(msg):
            msg_date = datetime.fromisoformat(msg['timestamp']).date()
            if date_from and msg_date < date_from:
                return False
            if date_to and msg_date > date_to:
                return False
            return True
        
        filtered_messages = [msg for msg in filtered_messages if filter_by_date(msg)]
    
    # Apply pagination
    paginated_messages = filtered_messages[skip:skip + limit]
    
    return [
        MessageResponse(
            id=msg['id'],
            client_id=msg['client_id'],
            user_id=msg['user_id'],
            user_name=msg.get('user_name'),
            message_direction=msg['message_direction'],
            content=msg['content'],
            timestamp=msg['timestamp'],
            message_metadata=msg.get('message_metadata'),
            status=msg.get('status', 'none'),
            conversation_stage=msg.get('conversation_stage'),
            lead_score=msg.get('lead_score', 0)
        )
        for msg in paginated_messages
    ]