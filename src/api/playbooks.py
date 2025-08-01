from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid

from src.core.db import get_db, Client, Playbook, PlaybookStatus
from src.types.schemas import (
    PlaybookResponse,
    PlaybookListResponse,
    PlaybookCreate,
    PlaybookUpdate,
)

router = APIRouter(tags=["playbooks"])

@router.get("/clients/{client_id}/playbooks", response_model=PlaybookListResponse)
async def get_playbooks(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all playbooks for a specific client with pagination"""
    
    # Verify client exists
    client_stmt = select(Client).where(Client.id == client_id)
    client_result = await db.execute(client_stmt)
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get total count
    count_stmt = select(func.count(Playbook.id)).where(Playbook.client_id == client_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # Get playbooks
    stmt = (
        select(Playbook)
        .where(Playbook.client_id == client_id)
        .offset(skip)
        .limit(limit)
        .order_by(Playbook.created_at.desc())
    )
    result = await db.execute(stmt)
    playbooks = result.scalars().all()
    
    return PlaybookListResponse(
        playbooks=[PlaybookResponse.model_validate(playbook) for playbook in playbooks],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/clients/{client_id}/playbooks/{playbook_id}", response_model=PlaybookResponse)
async def get_playbook(
    client_id: str,
    playbook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific playbook by ID"""
    stmt = select(Playbook).where(
        Playbook.client_id == client_id,
        Playbook.id == playbook_id
    )
    result = await db.execute(stmt)
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    return PlaybookResponse.model_validate(playbook)

@router.post("/clients/{client_id}/playbooks", response_model=PlaybookResponse)
async def create_playbook(
    client_id: str,
    playbook_data: PlaybookCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new playbook for a specific client"""
    
    # Verify client exists
    client_stmt = select(Client).where(Client.id == client_id)
    client_result = await db.execute(client_stmt)
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # If this is set as default, unset other default playbooks for this client
    if playbook_data.is_default:
        update_stmt = (
            select(Playbook)
            .where(Playbook.client_id == client_id, Playbook.is_default == True)
        )
        existing_defaults = await db.execute(update_stmt)
        for existing_default in existing_defaults.scalars():
            existing_default.is_default = False
    
    # Create playbook
    playbook = Playbook(
        id=str(uuid.uuid4()),
        client_id=client_id,
        name=playbook_data.name,
        description=playbook_data.description,
        status=PlaybookStatus.DRAFT,  # Always start as draft
        is_default=playbook_data.is_default,
        steps=playbook_data.steps or [],
        conditions=playbook_data.conditions,
        fallback_messages=playbook_data.fallback_messages or [],
        situation_prompts=playbook_data.situation_prompts or [],
        problem_prompts=playbook_data.problem_prompts or [],
        implication_prompts=playbook_data.implication_prompts or [],
        need_payoff_prompts=playbook_data.need_payoff_prompts or []
    )
    
    db.add(playbook)
    await db.commit()
    await db.refresh(playbook)
    
    return PlaybookResponse.model_validate(playbook)

@router.put("/clients/{client_id}/playbooks/{playbook_id}", response_model=PlaybookResponse)
async def update_playbook(
    client_id: str,
    playbook_id: str,
    playbook_data: PlaybookUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing playbook"""
    stmt = select(Playbook).where(
        Playbook.client_id == client_id,
        Playbook.id == playbook_id
    )
    result = await db.execute(stmt)
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    # If this is being set as default, unset other default playbooks for this client
    if playbook_data.is_default and not playbook.is_default:
        update_stmt = (
            select(Playbook)
            .where(
                Playbook.client_id == client_id,
                Playbook.is_default == True,
                Playbook.id != playbook_id
            )
        )
        existing_defaults = await db.execute(update_stmt)
        for existing_default in existing_defaults.scalars():
            existing_default.is_default = False
    
    # Update fields
    update_data = playbook_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(playbook, field):
            setattr(playbook, field, value)
    
    # Increment version when activating
    if playbook_data.status == PlaybookStatus.ACTIVE and playbook.status != PlaybookStatus.ACTIVE:
        playbook.version += 1
    
    await db.commit()
    await db.refresh(playbook)
    
    return PlaybookResponse.model_validate(playbook)

@router.delete("/clients/{client_id}/playbooks/{playbook_id}")
async def delete_playbook(
    client_id: str,
    playbook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a playbook"""
    stmt = select(Playbook).where(
        Playbook.client_id == client_id,
        Playbook.id == playbook_id
    )
    result = await db.execute(stmt)
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    # Prevent deletion of the default playbook
    if playbook.is_default:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the default playbook. Set another playbook as default first."
        )
    
    await db.delete(playbook)
    await db.commit()
    
    return {"message": "Playbook deleted successfully"}

@router.post("/clients/{client_id}/playbooks/{playbook_id}/activate", response_model=PlaybookResponse)
async def activate_playbook(
    client_id: str,
    playbook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Activate a playbook (change status to active)"""
    stmt = select(Playbook).where(
        Playbook.client_id == client_id,
        Playbook.id == playbook_id
    )
    result = await db.execute(stmt)
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    if playbook.status == PlaybookStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Playbook is already active")
    
    playbook.status = PlaybookStatus.ACTIVE
    playbook.version += 1
    
    await db.commit()
    await db.refresh(playbook)
    
    return PlaybookResponse.model_validate(playbook)

@router.post("/clients/{client_id}/playbooks/{playbook_id}/deactivate", response_model=PlaybookResponse)
async def deactivate_playbook(
    client_id: str,
    playbook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a playbook (change status to draft)"""
    stmt = select(Playbook).where(
        Playbook.client_id == client_id,
        Playbook.id == playbook_id
    )
    result = await db.execute(stmt)
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    if playbook.status != PlaybookStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Playbook is not active")
    
    playbook.status = PlaybookStatus.DRAFT
    
    await db.commit()
    await db.refresh(playbook)
    
    return PlaybookResponse.model_validate(playbook)

@router.post("/clients/{client_id}/playbooks/{playbook_id}/duplicate", response_model=PlaybookResponse)
async def duplicate_playbook(
    client_id: str,
    playbook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Duplicate an existing playbook"""
    stmt = select(Playbook).where(
        Playbook.client_id == client_id,
        Playbook.id == playbook_id
    )
    result = await db.execute(stmt)
    original_playbook = result.scalar_one_or_none()
    
    if not original_playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    # Create duplicate
    duplicate = Playbook(
        id=str(uuid.uuid4()),
        client_id=client_id,
        name=f"{original_playbook.name} (Copy)",
        description=f"Copy of {original_playbook.description}" if original_playbook.description else None,
        status=PlaybookStatus.DRAFT,  # Always start as draft
        is_default=False,  # Duplicates are never default
        steps=original_playbook.steps,
        conditions=original_playbook.conditions,
        fallback_messages=original_playbook.fallback_messages,
        situation_prompts=original_playbook.situation_prompts,
        problem_prompts=original_playbook.problem_prompts,
        implication_prompts=original_playbook.implication_prompts,
        need_payoff_prompts=original_playbook.need_payoff_prompts
    )
    
    db.add(duplicate)
    await db.commit()
    await db.refresh(duplicate)
    
    return PlaybookResponse.model_validate(duplicate)