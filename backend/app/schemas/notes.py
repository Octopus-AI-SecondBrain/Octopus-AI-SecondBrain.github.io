"""
Octopus AI Second Brain - Note Schemas
Request and response models for notes endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteCreateRequest(BaseModel):
    """Create note request"""
    title: str = Field(..., min_length=1, max_length=500, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    tags: Optional[list[str]] = Field(None, description="Note tags")


class NoteUpdateRequest(BaseModel):
    """Update note request"""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Note title")
    content: Optional[str] = Field(None, min_length=1, description="Note content")
    tags: Optional[list[str]] = Field(None, description="Note tags")


class NoteResponse(BaseModel):
    """Note response"""
    id: int = Field(..., description="Note ID")
    user_id: int = Field(..., description="Owner user ID")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    tags: Optional[list[str]] = Field(None, description="Note tags")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """List of notes response"""
    notes: list[NoteResponse] = Field(default_factory=list, description="List of notes")
    total: int = Field(..., description="Total number of notes")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Page size")
