"""
Messages router for serverless deployment
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timezone

from src.core.supabase_db import get_supabase_db
from api.auth.router import verify_token

router = APIRouter()

# Pydantic models
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

@router.get("/", response_model=List[MessageResponse])
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
            msg_date = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).date()
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

@router.get("/stats", response_model=MessageStats)
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
            msg_date = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).date()
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
    recent_cutoff = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    recent_users = set()
    for msg in all_messages:
        msg_date = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
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

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    token_data: dict = Depends(verify_token)
):
    """Get a specific message by ID"""
    db = get_supabase_db()
    
    # This would require a get_message_by_id method in SupabaseDB
    # For now, we'll return a not implemented error
    raise HTTPException(status_code=501, detail="Get message by ID not implemented yet")

@router.put("/{message_id}/status")
async def update_message_status(
    message_id: str,
    status: str = Query(..., description="New status for the message"),
    token_data: dict = Depends(verify_token)
):
    """Update message status"""
    db = get_supabase_db()
    
    # Validate status
    valid_statuses = ['qualified', 'scheduled', 'none', 'lost', 'archived']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Update message status
    updated_message = await db.update_message_status(message_id, status)
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found or update failed")
    
    return {"message": "Message status updated successfully", "new_status": status}