from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Optional

import chromadb
from chromadb.config import Settings
from sqlalchemy.orm import Session

from backend.config.config import get_settings
from backend.core.embeddings import generate_embedding
from backend.models import note

# Get settings
settings = get_settings()

# ChromaDB setup
_client = None
_collection = None
CHROMA_PATH = settings.vector_store.chroma_path

def get_client():
    """Get or create the ChromaDB client."""
    global _client
    if _client is None:
        # Use the configured chroma_db directory
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)

        _client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    return _client

def get_collection():
    """Return the shared collection for notes."""
    global _collection
    if _collection is None:
        client = get_client()
        try:
            _collection = client.get_or_create_collection(
                name="notes",
                metadata={"hnsw:space": "cosine"},
            )
        except AttributeError:
            try:
                _collection = client.get_collection("notes")
            except Exception:
                _collection = client.create_collection(
                    name="notes",
                    metadata={"hnsw:space": "cosine"}
                )
    return _collection


def _flatten_ids(raw_ids: Iterable | None) -> List[str]:
    if not raw_ids:
        return []
    flattened: List[str] = []
    for item in raw_ids:
        if isinstance(item, (list, tuple)):
            flattened.extend(str(i) for i in item)
        else:
            flattened.append(str(item))
    return flattened


def build_where(owner_id: int, embedding_model: Optional[str] = None) -> dict:
    """Build a where clause for ChromaDB queries."""
    clauses: List[dict] = [{"owner_id": owner_id}]
    if embedding_model:
        clauses.append({"embedding_model": embedding_model})
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def ensure_user_embeddings(db_session: Session, owner_id: int) -> None:
    """Ensure all user notes have embeddings in ChromaDB."""
    try:
        collection = get_collection()
        
        # Get all notes for this user that don't have embeddings
        notes_without_embeddings = (
            db_session.query(note.Note)
            .filter(note.Note.owner_id == owner_id)
            .filter(note.Note.embedding_model.is_(None))
            .all()
        )
        
        for note_obj in notes_without_embeddings:
            # Generate embedding for the note content
            embedding, model_id = generate_embedding(note_obj.content or "")
            
            # Store in ChromaDB
            collection.add(
                ids=[str(note_obj.id)],
                embeddings=[embedding],
                metadatas=[{
                    "owner_id": owner_id,
                    "embedding_model": model_id,
                    "title": note_obj.title or "",
                    "created_at": note_obj.created_at.isoformat() if note_obj.created_at else "",
                }],
                documents=[note_obj.content or ""]
            )
            
            # Update the note in the database
            note_obj.embedding_model = model_id
            db_session.add(note_obj)
        
        db_session.commit()
        
    except Exception as e:
        print(f"Error ensuring embeddings: {e}")
        db_session.rollback()


def search_similar_notes(
    db_session: Session, 
    owner_id: int, 
    query: str, 
    limit: int = 10
) -> List[note.Note]:
    """Search for similar notes using vector similarity."""
    try:
        collection = get_collection()
        
        # Generate embedding for the query
        query_embedding, _ = generate_embedding(query)
        
        # Search in ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            where=build_where(owner_id),
            n_results=limit
        )
        
        if not results["ids"] or not results["ids"][0]:
            return []
        
        # Get the note IDs
        note_ids = [int(id_) for id_ in results["ids"][0]]
        
        # Fetch the actual notes from the database
        notes = (
            db_session.query(note.Note)
            .filter(note.Note.id.in_(note_ids))
            .filter(note.Note.owner_id == owner_id)
            .all()
        )
        
        # Order notes by the similarity score order from ChromaDB
        note_dict = {n.id: n for n in notes}
        ordered_notes = [note_dict[note_id] for note_id in note_ids if note_id in note_dict]
        
        return ordered_notes
        
    except Exception as e:
        print(f"Error searching notes: {e}")
        return []


def add_note_to_vector_store(db_session: Session, note_obj: note.Note) -> None:
    """Add a single note to the vector store."""
    try:
        collection = get_collection()
        
        # Generate embedding
        embedding, model_id = generate_embedding(note_obj.content or "")
        
        # Store in ChromaDB
        collection.add(
            ids=[str(note_obj.id)],
            embeddings=[embedding],
            metadatas=[{
                "owner_id": note_obj.owner_id,
                "embedding_model": model_id,
                "title": note_obj.title or "",
                "created_at": note_obj.created_at.isoformat() if note_obj.created_at else "",
            }],
            documents=[note_obj.content or ""]
        )
        
        # Update the note in the database
        note_obj.embedding_model = model_id
        db_session.add(note_obj)
        db_session.commit()
        
    except Exception as e:
        print(f"Error adding note to vector store: {e}")
        db_session.rollback()


def delete_note_from_vector_store(note_id: int) -> None:
    """Remove a note from the vector store."""
    try:
        collection = get_collection()
        collection.delete(ids=[str(note_id)])
    except Exception as e:
        print(f"Error deleting note from vector store: {e}")
