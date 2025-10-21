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
    tags: List[str] = []

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: List[str] | None = None

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str] = []
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
    from backend.services.vector_store import add_note_to_vector_store
    from backend.core.logging import get_logger
    
    logger = get_logger("notes")
    
    # 1) Create the note in the DB first to get a stable ID
    new_note = note.Note(
        title=note_in.title,
        content=note_in.content,
        tags=note_in.tags or [],
        owner_id=current_user.id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    # 2) Try to add to vector store - this won't commit, so we need to commit again
    try:
        add_note_to_vector_store(db, new_note)
        db.commit()
        db.refresh(new_note)
        logger.info(f"Note {new_note.id} added to vector store successfully")
    except Exception as e:
        # Rollback any partial changes from vector store
        db.rollback()
        # Refresh to get back to committed state
        db.refresh(new_note)
        logger.warning(f"Failed to add note {new_note.id} to vector store: {e}")
        # Note is still created successfully, just without embedding

    return new_note

# List notes
@router.get("/", response_model=List[NoteOut])
def list_notes(
    tag: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    try:
        from backend.services.vector_store import ensure_user_embeddings
        
        # Ensure all notes have embeddings
        ensure_user_embeddings(db, current_user.id)
        
        query = db.query(note.Note).filter(note.Note.owner_id == current_user.id)
        
        # Filter by tag if provided
        if tag:
            query = query.filter(note.Note.tags.contains([tag]))
        
        # Apply pagination
        query = query.order_by(note.Note.created_at.desc()).offset(offset).limit(limit)
        
        return query.all()
    except Exception as e:
        # If vector store fails, still return notes
        print(f"Warning: Vector store error: {e}")
        query = db.query(note.Note).filter(note.Note.owner_id == current_user.id)
        if tag:
            query = query.filter(note.Note.tags.contains([tag]))
        return query.all()

# Count notes
@router.get("/count/total")
def count_notes(
    tag: str | None = None,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    query = db.query(note.Note).filter(note.Note.owner_id == current_user.id)
    
    if tag:
        query = query.filter(note.Note.tags.contains([tag]))
    
    return {"total": query.count()}

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
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    from backend.services.vector_store import add_note_to_vector_store, delete_note_from_vector_store
    from backend.core.logging import get_logger
    
    logger = get_logger("notes")
    
    note_obj = db.query(note.Note).filter(
        note.Note.id == note_id,
        note.Note.owner_id == current_user.id
    ).first()
    
    if not note_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update note in database first
    if note_in.title is not None:
        note_obj.title = note_in.title
    if note_in.content is not None:
        note_obj.content = note_in.content
    if note_in.tags is not None:
        note_obj.tags = note_in.tags
    
    # Reset embedding_model to trigger re-embedding if content/title changed
    if note_in.title is not None or note_in.content is not None:
        note_obj.embedding_model = None
    
    db.commit()
    db.refresh(note_obj)
    
    # Try to update vector store - don't fail if this fails (only if content changed)
    if note_in.title is not None or note_in.content is not None:
        try:
            delete_note_from_vector_store(note_id)
            add_note_to_vector_store(db, note_obj)
            db.commit()
            db.refresh(note_obj)
            logger.info(f"Note {note_id} updated in vector store successfully")
        except Exception as e:
            # Rollback any partial changes from vector store
            db.rollback()
            # Refresh to get back to committed state
            db.refresh(note_obj)
            logger.warning(f"Failed to update note {note_id} in vector store: {e}")
            # Note is still updated successfully, just without embedding
    
    return note_obj

# Delete note
@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    from backend.services.vector_store import delete_note_from_vector_store
    from backend.core.logging import get_logger
    
    logger = get_logger("notes")
    
    note_obj = db.query(note.Note).filter(
        note.Note.id == note_id,
        note.Note.owner_id == current_user.id
    ).first()
    
    if not note_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Delete from database first
    db.delete(note_obj)
    db.commit()
    
    # Try to remove from vector store - don't fail if this fails
    try:
        delete_note_from_vector_store(note_id)
        logger.info(f"Note {note_id} removed from vector store successfully")
    except Exception as e:
        logger.warning(f"Failed to remove note {note_id} from vector store: {e}")
        # Note is still deleted successfully from database
    
    return {"message": "Note deleted successfully"}

# Get all unique tags
@router.get("/tags/all", response_model=List[str])
def get_all_tags(
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    """Get all unique tags used by the current user's notes."""
    notes = db.query(note.Note).filter(note.Note.owner_id == current_user.id).all()
    
    # Collect all unique tags
    all_tags = set()
    for n in notes:
        if n.tags:
            all_tags.update(n.tags)
    
    return sorted(list(all_tags))

# Export notes
@router.get("/export/{format}")
def export_notes(
    format: str,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    """Export all notes in JSON, Markdown, or CSV format."""
    from fastapi.responses import Response
    import json
    import csv
    import io
    
    notes = db.query(note.Note).filter(note.Note.owner_id == current_user.id).all()
    
    if format == "json":
        data = [
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "tags": n.tags or [],
                "created_at": n.created_at.isoformat(),
                "updated_at": n.updated_at.isoformat(),
            }
            for n in notes
        ]
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=notes.json"}
        )
    
    elif format == "markdown":
        md_content = "# My Notes\n\n"
        for n in notes:
            md_content += f"## {n.title}\n\n"
            if n.tags:
                md_content += f"**Tags:** {', '.join(n.tags)}\n\n"
            # Strip HTML tags from content
            import re
            clean_content = re.sub('<[^<]+?>', '', n.content)
            md_content += f"{clean_content}\n\n"
            md_content += f"*Created: {n.created_at.strftime('%Y-%m-%d')}*\n\n"
            md_content += "---\n\n"
        
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=notes.md"}
        )
    
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Title", "Content", "Tags", "Created", "Updated"])
        
        for n in notes:
            import re
            clean_content = re.sub('<[^<]+?>', '', n.content)
            writer.writerow([
                n.id,
                n.title,
                clean_content,
                ", ".join(n.tags or []),
                n.created_at.strftime('%Y-%m-%d'),
                n.updated_at.strftime('%Y-%m-%d'),
            ])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=notes.csv"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use json, markdown, or csv")

# Import notes
class ImportRequest(BaseModel):
    file_content: str
    format: str = "json"

@router.post("/import")
def import_notes(
    request: ImportRequest,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_user),
):
    """Import notes from JSON, Markdown, or plain text."""
    from backend.services.vector_store import add_note_to_vector_store
    from backend.core.logging import get_logger
    import json
    import re
    
    logger = get_logger("notes")
    imported_count = 0
    file_content = request.file_content
    format = request.format
    
    try:
        if format == "json":
            data = json.loads(file_content)
            if not isinstance(data, list):
                data = [data]
            
            for item in data:
                new_note = note.Note(
                    title=item.get("title", "Untitled"),
                    content=item.get("content", ""),
                    tags=item.get("tags", []),
                    owner_id=current_user.id
                )
                db.add(new_note)
                db.commit()
                db.refresh(new_note)
                
                # Try to add to vector store
                try:
                    add_note_to_vector_store(db, new_note)
                    db.commit()
                except Exception as e:
                    logger.warning(f"Failed to add imported note {new_note.id} to vector store: {e}")
                
                imported_count += 1
        
        elif format == "markdown" or format == "text":
            # Split by horizontal rules or double newlines
            sections = re.split(r'\n---+\n|\n\n\n+', file_content)
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Try to extract title from first line if it starts with #
                lines = section.split('\n')
                title = "Imported Note"
                content = section
                
                if lines[0].startswith('#'):
                    title = lines[0].lstrip('#').strip()
                    content = '\n'.join(lines[1:]).strip()
                
                new_note = note.Note(
                    title=title,
                    content=content,
                    tags=[],
                    owner_id=current_user.id
                )
                db.add(new_note)
                db.commit()
                db.refresh(new_note)
                
                # Try to add to vector store
                try:
                    add_note_to_vector_store(db, new_note)
                    db.commit()
                except Exception as e:
                    logger.warning(f"Failed to add imported note {new_note.id} to vector store: {e}")
                
                imported_count += 1
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use json, markdown, or text")
        
        return {"message": f"Successfully imported {imported_count} notes", "count": imported_count}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
