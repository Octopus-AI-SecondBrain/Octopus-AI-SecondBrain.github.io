from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models import db, note
from backend.routes.auth import get_current_user

router = APIRouter()

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@router.get("/summary")
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get analytics summary for the dashboard."""
    try:
        # Get note count
        note_count = db.query(func.count(note.Note.id)).filter(
            note.Note.owner_id == current_user.id
        ).scalar() or 0
        
        # Get total words across all notes
        notes_with_content = db.query(note.Note).filter(
            note.Note.owner_id == current_user.id,
            note.Note.content.isnot(None)
        ).all()
        
        total_words = sum(
            len((n.content or "").split()) for n in notes_with_content
        )
        
        # Get notes created this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        notes_this_week = db.query(func.count(note.Note.id)).filter(
            note.Note.owner_id == current_user.id,
            note.Note.created_at >= week_ago
        ).scalar() or 0
        
        # Calculate average note length
        avg_note_length = total_words / note_count if note_count > 0 else 0
        
        # Get notes with embeddings (semantic search ready)
        notes_with_embeddings = db.query(func.count(note.Note.id)).filter(
            note.Note.owner_id == current_user.id,
            note.Note.embedding_model.isnot(None)
        ).scalar() or 0
        
        return {
            "note_count": note_count,
            "total_words": total_words,
            "notes_this_week": notes_this_week,
            "avg_note_length": round(avg_note_length, 1),
            "notes_with_embeddings": notes_with_embeddings,
            "search_ready_percentage": round(
                (notes_with_embeddings / note_count * 100) if note_count > 0 else 0, 1
            ),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "note_count": 0,
            "total_words": 0,
            "notes_this_week": 0,
            "avg_note_length": 0,
            "notes_with_embeddings": 0,
            "search_ready_percentage": 0,
            "error": str(e),
            "last_updated": datetime.utcnow().isoformat()
        }


@router.get("/trends")
def get_creation_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get note creation trends over time."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all notes created in the time period
        notes_in_period = db.query(note.Note).filter(
            note.Note.owner_id == current_user.id,
            note.Note.created_at >= start_date
        ).all()
        
        # Group by date
        daily_counts = {}
        for n in notes_in_period:
            if n.created_at:
                date_key = n.created_at.date().isoformat()
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        # Fill in missing dates with 0
        trend_data = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=days - i - 1)).date()
            date_key = date.isoformat()
            trend_data.append({
                "date": date_key,
                "count": daily_counts.get(date_key, 0)
            })
        
        return {
            "period_days": days,
            "trends": trend_data,
            "total_in_period": len(notes_in_period)
        }
        
    except Exception as e:
        return {
            "period_days": days,
            "trends": [],
            "total_in_period": 0,
            "error": str(e)
        }


@router.get("/tags")
def get_tag_distribution(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get distribution of tags across notes."""
    try:
        # Get all notes with tags
        notes_with_tags = db.query(note.Note).filter(
            note.Note.owner_id == current_user.id,
            note.Note.tags.isnot(None)
        ).all()
        
        # Count tag occurrences
        tag_counts = {}
        for n in notes_with_tags:
            if n.tags:
                for tag in n.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count and return top tags
        sorted_tags = sorted(
            [{"tag": tag, "count": count} for tag, count in tag_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )
        
        return {
            "tags": sorted_tags[:15],  # Top 15 tags
            "total_unique_tags": len(tag_counts),
            "total_notes_with_tags": len(notes_with_tags)
        }
        
    except Exception as e:
        return {
            "tags": [],
            "total_unique_tags": 0,
            "total_notes_with_tags": 0,
            "error": str(e)
        }