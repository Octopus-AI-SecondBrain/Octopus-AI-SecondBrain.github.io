from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.models import db, note, user
from backend.routes.auth import get_current_user

router = APIRouter()

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Pydantic schemas
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    embedding_model: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

# Create note
@router.post("/", response_model=NoteOut)
def create_note(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    try:
        from backend.services.vector_store import add_note_to_vector_store
        
        # 1) Create the note in the DB first to get a stable ID
        new_note = note.Note(
            title=note_in.title,
            content=note_in.content,
            owner_id=current_user.id
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        # 2) Add to vector store for semantic search
        add_note_to_vector_store(db, new_note)

        return new_note
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")

# List notes
@router.get("/", response_model=List[NoteOut])
def list_notes(
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    try:
        from backend.services.vector_store import ensure_user_embeddings
        
        # Ensure all notes have embeddings
        ensure_user_embeddings(db, current_user.id)
        
        return db.query(note.Note).filter(note.Note.owner_id == current_user.id).all()
    except Exception as e:
        # If vector store fails, still return notes
        print(f"Warning: Vector store error: {e}")
        return db.query(note.Note).filter(note.Note.owner_id == current_user.id).all()

# Get single note
@router.get("/{note_id}", response_model=NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    note_obj = db.query(note.Note).filter(
        note.Note.id == note_id,
        note.Note.owner_id == current_user.id
    ).first()
    
    if not note_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note_obj

# Update note
@router.put("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    try:
        from backend.services.vector_store import add_note_to_vector_store, delete_note_from_vector_store
        
        note_obj = db.query(note.Note).filter(
            note.Note.id == note_id,
            note.Note.owner_id == current_user.id
        ).first()
        
        if not note_obj:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Remove from vector store
        delete_note_from_vector_store(note_id)
        
        # Update note
        note_obj.title = note_in.title
        note_obj.content = note_in.content
        note_obj.embedding_model = None  # Reset to trigger re-embedding
        
        db.commit()
        db.refresh(note_obj)
        
        # Re-add to vector store with new content
        add_note_to_vector_store(db, note_obj)
        
        return note_obj
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")

# Delete note
@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    try:
        from backend.services.vector_store import delete_note_from_vector_store
        
        note_obj = db.query(note.Note).filter(
            note.Note.id == note_id,
            note.Note.owner_id == current_user.id
        ).first()
        
        if not note_obj:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Remove from vector store
        delete_note_from_vector_store(note_id)
        
        # Delete from database
        db.delete(note_obj)
        db.commit()
        
        return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")
