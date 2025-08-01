from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from src.core.db import get_db, Message, Client, MessageStatus, User
from src.core.auth import get_current_active_user
from src.types.schemas import MessageHistoryResponse, MessageHistory, StatsResponse
from datetime import date, datetime
from typing import Optional
from uuid import UUID

router = APIRouter(tags=["Messages"])

@router.get("/clients/{client_id}/messages", response_model=MessageHistoryResponse)
async def get_client_messages(
    client_id: str,
    date_from: Optional[date] = Query(None, description="Filter messages from this date"),
    date_to: Optional[date] = Query(None, description="Filter messages until this date"),
    status: Optional[str] = Query(None, description="Filter by message status"),
    keyword: Optional[str] = Query(None, description="Search keyword in message content"),
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of messages to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated message history for a specific client with filtering options
    """
    # Validate client exists and belongs to current user
    client_result = await db.execute(
        select(Client).where(
            and_(Client.id == client_id, Client.owner_id == current_user.id)
        )
    )
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found or access denied")

    # Build query
    query = select(Message).where(Message.client_id == client_id)
    
    # Apply filters
    if date_from:
        query = query.where(Message.timestamp >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(Message.timestamp <= datetime.combine(date_to, datetime.max.time()))
    if status:
        try:
            status_enum = MessageStatus(status)
            query = query.where(Message.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if keyword:
        query = query.where(Message.content.ilike(f"%{keyword}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and ordering
    query = query.order_by(Message.timestamp.desc()).offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    messages = result.scalars().all()

    # Convert to response format
    message_responses = [
        MessageHistory(
            id=msg.id,
            client_id=msg.client_id,
            user_id=msg.user_id or "",
            user_name=msg.user_name,
            message_direction=msg.message_direction.value if msg.message_direction else "inbound",
            content=msg.content or "",
            timestamp=msg.timestamp,
            metadata=msg.message_metadata,
            status=msg.status.value if msg.status else None,
            conversation_stage=msg.conversation_stage,
            lead_score=msg.lead_score or 0
        )
        for msg in messages
    ]

    return MessageHistoryResponse(
        messages=message_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/clients/{client_id}/stats", response_model=StatsResponse)
async def get_client_stats(
    client_id: str,
    date_from: Optional[date] = Query(None, description="Calculate stats from this date"),
    date_to: Optional[date] = Query(None, description="Calculate stats until this date"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated statistics for a specific client
    """
    # Validate client exists and belongs to current user
    client_result = await db.execute(
        select(Client).where(
            and_(Client.id == client_id, Client.owner_id == current_user.id)
        )
    )
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found or access denied")

    # Build base query
    base_query = select(Message).where(Message.client_id == client_id)
    
    # Apply date filters
    period_start = None
    period_end = None
    if date_from:
        period_start = datetime.combine(date_from, datetime.min.time())
        base_query = base_query.where(Message.timestamp >= period_start)
    if date_to:
        period_end = datetime.combine(date_to, datetime.max.time())
        base_query = base_query.where(Message.timestamp <= period_end)

    # Get total conversations (unique user_id)
    conversations_query = select(func.count(distinct(Message.user_id))).select_from(base_query.subquery())
    conversations_result = await db.execute(conversations_query)
    total_conversations = conversations_result.scalar() or 0

    # Get qualified leads
    qualified_query = select(func.count(distinct(Message.user_id))).where(
        and_(
            Message.client_id == client_id,
            Message.status == MessageStatus.QUALIFIED,
            Message.timestamp >= period_start if period_start else True,
            Message.timestamp <= period_end if period_end else True
        )
    )
    qualified_result = await db.execute(qualified_query)
    leads_qualified = qualified_result.scalar() or 0

    # Get scheduled appointments
    scheduled_query = select(func.count(distinct(Message.user_id))).where(
        and_(
            Message.client_id == client_id,
            Message.status == MessageStatus.SCHEDULED,
            Message.timestamp >= period_start if period_start else True,
            Message.timestamp <= period_end if period_end else True
        )
    )
    scheduled_result = await db.execute(scheduled_query)
    appointments_scheduled = scheduled_result.scalar() or 0

    return StatsResponse(
        total_conversations=total_conversations,
        leads_qualified=leads_qualified,
        appointments_scheduled=appointments_scheduled,
        period_start=period_start,
        period_end=period_end
    )