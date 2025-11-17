"""
Octopus AI Second Brain - Notes Endpoints
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..db.models.user import User
from ..db.models.note import Note
from ..schemas.notes import (
    NoteCreateRequest,
    NoteUpdateRequest,
    NoteResponse,
    NoteListResponse,
)
from ..schemas.common import MessageResponse
from ..api.auth import get_current_user
from ..core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: NoteCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Note:
    """
    Create a new note.
    
    Args:
        data: Note creation data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Created note
    """
    note = Note(
        title=data.title,
        content=data.content,
        tags=data.tags,
        user_id=current_user.id,
    )
    
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
    logger.info(f"Created note {note.id} for user {current_user.username}")
    
    return note


@router.get("", response_model=NoteListResponse)
async def list_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of notes to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of notes to return"),
    tag: str | None = Query(None, description="Filter by tag"),
) -> NoteListResponse:
    """
    List user's notes with pagination.
    
    Args:
        current_user: Authenticated user
        db: Database session
        skip: Number of notes to skip
        limit: Number of notes to return
        tag: Optional tag filter
        
    Returns:
        Paginated list of notes
    """
    # Build query
    query = select(Note).where(Note.user_id == current_user.id)
    
    # Apply tag filter if provided
    if tag:
        query = query.where(Note.tags.contains([tag]))  # type: ignore
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Apply pagination and order
    query = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    notes = list(result.scalars().all())
    
    logger.info(f"Listed {len(notes)} notes for user {current_user.username}")
    
    # Calculate page number
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return NoteListResponse(
        notes=[NoteResponse.model_validate(note) for note in notes],
        total=total,
        page=page,
        page_size=limit,
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Note:
    """
    Get a specific note by ID.
    
    Args:
        note_id: Note ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Note details
        
    Raises:
        HTTPException: If note not found or not owned by user
    """
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    data: NoteUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Note:
    """
    Update a note.
    
    Args:
        note_id: Note ID
        data: Note update data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated note
        
    Raises:
        HTTPException: If note not found or not owned by user
    """
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    
    # Update fields
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.tags is not None:
        note.tags = data.tags
    
    await db.commit()
    await db.refresh(note)
    
    logger.info(f"Updated note {note.id} for user {current_user.username}")
    
    return note


@router.delete("/{note_id}", response_model=MessageResponse)
async def delete_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Delete a note.
    
    Args:
        note_id: Note ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If note not found or not owned by user
    """
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    
    await db.delete(note)
    await db.commit()
    
    logger.info(f"Deleted note {note_id} for user {current_user.username}")
    
    return MessageResponse(
        message=f"Note {note_id} deleted successfully",
        success=True,
    )
