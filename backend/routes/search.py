from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models import db
from backend.routes.auth import get_current_user

router = APIRouter()


class SearchQuery(BaseModel):
    query: str


def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@router.post("/")
def semantic_search(
    payload: SearchQuery,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        from backend.models import note
        from backend.services.vector_store import search_similar_notes, ensure_user_embeddings
        
        search_term = payload.query.lower().strip()
        
        if not search_term:
            return {
                "query": payload.query,
                "results": [],
                "message": "Please enter a search term",
            }
        
        # Ensure user has embeddings
        ensure_user_embeddings(db, current_user.id)
        
        # Try vector search first
        vector_results = search_similar_notes(db, current_user.id, payload.query, limit=15)
        
        # Fallback to text search if vector search returns no results
        if not vector_results:
            notes = (
                db.query(note.Note)
                .filter(note.Note.owner_id == current_user.id)
                .filter(
                    (note.Note.title.ilike(f"%{search_term}%")) |
                    (note.Note.content.ilike(f"%{search_term}%"))
                )
                .limit(20)
                .all()
            )
        else:
            notes = vector_results
        
        # Format results
        results = []
        for i, n in enumerate(notes):
            # Calculate relevance score
            if vector_results:
                # Use position in vector search results as score
                score = 1.0 - (i * 0.05)  # Diminishing score
            else:
                # Calculate simple keyword matching score
                title_matches = search_term in (n.title or "").lower()
                content_matches = search_term in (n.content or "").lower()
                score = 0.8 if title_matches else 0.5
                if content_matches:
                    score += 0.3
            
            results.append({
                "id": n.id,
                "title": n.title or f"Note {n.id}",
                "content": n.content or "",
                "preview": _preview(n.content or "", 150),
                "score": min(score, 1.0),
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "search_method": "vector" if vector_results else "keyword"
            })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        search_method = "vector similarity" if vector_results else "keyword matching"
        
        return {
            "query": payload.query,
            "results": results,
            "count": len(results),
            "search_method": search_method,
            "message": f"Found {len(results)} notes using {search_method}"
        }
        
    except Exception as e:
        print(f"Search error: {e}")
        return {
            "query": payload.query,
            "results": [],
            "error": f"Search error: {str(e)}",
        }

def _preview(text: str, n: int = 120) -> str:
    """Generate a preview of text content."""
    t = (text or "").strip().replace("\n", " ")
    return t[:n] + ("…" if len(t) > n else "")
