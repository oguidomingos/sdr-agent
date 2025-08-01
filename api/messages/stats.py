"""
Messages statistics endpoint for Vercel serverless deployment
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, date
import jwt
import os

from src.core.supabase_db import get_supabase_db

app = FastAPI()
security = HTTPBearer()

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

@app.get("/", response_model=MessageStats)
async def get_message_stats(
    client_id: Optional[str] = Query(None, description="Get stats for specific client"),
    date_from: Optional[date] = Query(None, description="Calculate stats from this date"),
    date_to: Optional[date] = Query(None, description="Calculate stats until this date"),
    token_data: dict = Depends(verify_token)
):
    """Get message statistics"""
    db = get_supabase_db()
    
    # Determine which clients to include
    if client_id:
        client = await db.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        if client['owner_id'] != token_data['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        client_ids = [client_id]
    else:
        user_clients = await db.get_clients_by_owner(token_data['user_id'])
        client_ids = [client['id'] for client in user_clients]
    
    if not client_ids:
        return MessageStats(
            total_messages=0,
            inbound_messages=0,
            outbound_messages=0,
            qualified_leads=0,
            active_conversations=0,
            date_range={"from": "", "to": ""}
        )
    
    # Get messages for all relevant clients
    all_messages = []
    for cid in client_ids:
        messages = await db.get_messages_by_client(cid, limit=1000)  # Reasonable limit for stats
        all_messages.extend(messages)
    
    # Apply date filters
    if date_from or date_to:
        def filter_by_date(msg):
            msg_date = datetime.fromisoformat(msg['timestamp']).date()
            if date_from and msg_date < date_from:
                return False
            if date_to and msg_date > date_to:
                return False
            return True
        
        all_messages = [msg for msg in all_messages if filter_by_date(msg)]
    
    # Calculate statistics
    total_messages = len(all_messages)
    inbound_messages = len([msg for msg in all_messages if msg.get('message_direction') == 'inbound'])
    outbound_messages = len([msg for msg in all_messages if msg.get('message_direction') == 'outbound'])
    qualified_leads = len([msg for msg in all_messages if msg.get('status') == 'qualified'])
    
    # Count active conversations (unique user_ids with recent messages)
    recent_cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    recent_users = set()
    for msg in all_messages:
        msg_date = datetime.fromisoformat(msg['timestamp'])
        if msg_date >= recent_cutoff:
            recent_users.add(msg['user_id'])
    
    active_conversations = len(recent_users)
    
    return MessageStats(
        total_messages=total_messages,
        inbound_messages=inbound_messages,
        outbound_messages=outbound_messages,
        qualified_leads=qualified_leads,
        active_conversations=active_conversations,
        date_range={
            "from": date_from.isoformat() if date_from else "",
            "to": date_to.isoformat() if date_to else ""
        }
    )