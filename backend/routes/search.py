from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from backend.models import db, note
from backend.routes.auth import get_current_user
from backend.core.logging import get_logger

router = APIRouter()
logger = get_logger("search")


class SearchFilters(BaseModel):
    tags: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort_by: str = "relevance"


class SearchQuery(BaseModel):
    query: str
    filters: Optional[SearchFilters] = None


class ExplainQuery(BaseModel):
    query: str
    results: List[Dict[str, Any]]


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
        
        # Build base query with filters
        base_query = db.query(note.Note).filter(note.Note.owner_id == current_user.id)
        
        # Apply filters if provided
        if payload.filters:
            # Tag filter
            if payload.filters.tags:
                for tag in payload.filters.tags:
                    base_query = base_query.filter(note.Note.tags.contains([tag]))
            
            # Date range filters
            if payload.filters.date_from:
                try:
                    date_from = datetime.fromisoformat(payload.filters.date_from)
                    base_query = base_query.filter(note.Note.created_at >= date_from)
                except ValueError:
                    pass
            
            if payload.filters.date_to:
                try:
                    date_to = datetime.fromisoformat(payload.filters.date_to)
                    base_query = base_query.filter(note.Note.created_at <= date_to)
                except ValueError:
                    pass
        
        # Try vector search first - increase limit for more results
        vector_results = search_similar_notes(db, current_user.id, payload.query, limit=50)
        
        logger.info(f"Vector search for '{payload.query}' returned {len(vector_results)} results")
        
        # Filter vector results by applying filters
        if vector_results and payload.filters:
            filtered_ids = [n.id for n in base_query.all()]
            vector_results = [n for n in vector_results if n.id in filtered_ids]
            logger.info(f"After filtering: {len(vector_results)} results")
        
        # Fallback to text search if vector search returns no results
        if not vector_results:
            notes = (
                base_query
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
            
            # Create highlighted preview
            preview_text = _preview(n.content or "", 150)
            highlighted_preview = _highlight_text(preview_text, search_term)
            
            results.append({
                "id": n.id,
                "title": n.title or f"Note {n.id}",
                "content": n.content or "",
                "preview": preview_text,
                "highlighted_preview": highlighted_preview,
                "score": min(score, 1.0),
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "tags": n.tags or [],
                "search_method": "vector" if vector_results else "keyword"
            })
        
        # Apply sorting
        if payload.filters and payload.filters.sort_by:
            if payload.filters.sort_by == "date_desc":
                results.sort(key=lambda x: x.get("created_at") or "", reverse=True)
            elif payload.filters.sort_by == "date_asc":
                results.sort(key=lambda x: x.get("created_at") or "")
            elif payload.filters.sort_by == "title":
                results.sort(key=lambda x: x.get("title", "").lower())
            else:  # relevance (default)
                results.sort(key=lambda x: x["score"], reverse=True)
        else:
            # Default sort by relevance
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


def _highlight_text(text: str, query: str) -> str:
    """Highlight query terms in text."""
    if not query or not text:
        return text
    
    import re
    # Simple highlighting - replace query words with highlighted versions
    words = query.lower().split()
    highlighted = text
    
    for word in words:
        if len(word) > 2:  # Only highlight meaningful words
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlighted = pattern.sub(f"**{word}**", highlighted)
    
    return highlighted


@router.post("/explain")
def explain_search_results(
    payload: ExplainQuery,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Provide LLM-powered explanation of search results."""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            # Fallback explanation without LLM
            return {
                "query": payload.query,
                "explanation": f"Found {len(payload.results)} notes related to '{payload.query}'. "
                             f"The results are ranked by relevance using {'semantic similarity' if any(r.get('search_method') == 'vector' for r in payload.results) else 'keyword matching'}. "
                             f"Consider the highest scoring results first as they are most likely to contain the information you're looking for.",
                "method": "rule-based",
                "llm_available": False
            }
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            # Prepare context from results
            context_items = []
            for i, result in enumerate(payload.results[:5]):  # Limit to top 5 results
                context_items.append(f"{i+1}. {result.get('title', 'Untitled')} (Score: {result.get('score', 0):.2f})\n   {result.get('preview', '')[:200]}")
            
            context = "\n\n".join(context_items)
            
            prompt = f"""You are analyzing search results for a personal knowledge base. 

Query: "{payload.query}"

Search Results:
{context}

Provide a concise, helpful explanation of what these results show and how they relate to the user's query. Focus on:
1. What topics/themes emerge from the results
2. How the results connect to each other
3. Key insights or patterns
4. Suggestions for further exploration

Keep the response under 150 words and make it actionable."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            explanation = response.choices[0].message.content or ""
            
            return {
                "query": payload.query,
                "explanation": explanation,
                "method": "llm",
                "llm_available": True
            }
            
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}")
            # Fallback if OpenAI call fails
            return {
                "query": payload.query,
                "explanation": f"Found {len(payload.results)} notes related to '{payload.query}'. "
                             f"While I couldn't provide AI analysis due to API limitations, these results are ranked by relevance. "
                             f"The highest scoring items likely contain the most relevant information.",
                "method": "fallback",
                "llm_available": True,
                "error": "LLM temporarily unavailable"
            }
            
    except Exception as e:
        logger.error(f"Explain results error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to explain results: {str(e)}")
