from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Iterable, List, Optional

import chromadb
from chromadb.config import Settings
from sqlalchemy.orm import Session

from backend.config.config import get_settings
from backend.core.embeddings import generate_embedding
from backend.core.logging import get_logger
from backend.models import note

# Get settings and logger
settings = get_settings()
logger = get_logger("secondbrain.vector_store")

# ChromaDB setup with thread-safe singleton pattern
_client = None
_collection = None
_lock = threading.Lock()
CHROMA_PATH = settings.vector_store.chroma_path


def get_client():
    """
    Get or create the ChromaDB client (thread-safe singleton).
    
    Returns:
        ChromaDB client instance
    """
    global _client
    if _client is None:
        with _lock:
            # Double-check pattern
            if _client is None:
                try:
                    # Ensure the chroma_db directory exists
                    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
                    
                    _client = chromadb.PersistentClient(
                        path=str(CHROMA_PATH),
                        settings=Settings(
                            anonymized_telemetry=False,
                            allow_reset=True
                        )
                    )
                    logger.info(f"ChromaDB client initialized at {CHROMA_PATH}")
                except Exception as exc:
                    logger.error(f"Failed to initialize ChromaDB client: {exc}", exc_info=True)
                    raise RuntimeError(f"ChromaDB initialization failed: {exc}")
    return _client


def get_collection():
    """
    Return the shared collection for notes (thread-safe singleton).
    
    Returns:
        ChromaDB collection instance
        
    Raises:
        RuntimeError: If collection cannot be created or retrieved
    """
    global _collection
    if _collection is None:
        with _lock:
            # Double-check pattern
            if _collection is None:
                try:
                    client = get_client()
                    _collection = client.get_or_create_collection(
                        name="notes",
                        metadata={"hnsw:space": "cosine"},
                    )
                    logger.info("ChromaDB collection 'notes' initialized")
                except AttributeError:
                    # Fallback for older chromadb versions
                    try:
                        _collection = client.get_collection("notes")
                        logger.info("Retrieved existing ChromaDB collection 'notes'")
                    except Exception:
                        _collection = client.create_collection(
                            name="notes",
                            metadata={"hnsw:space": "cosine"}
                        )
                        logger.info("Created new ChromaDB collection 'notes'")
                except Exception as exc:
                    logger.error(f"Failed to initialize ChromaDB collection: {exc}", exc_info=True)
                    raise RuntimeError(f"ChromaDB collection initialization failed: {exc}")
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
    """
    Ensure all user notes have embeddings in ChromaDB.
    
    Args:
        db_session: SQLAlchemy database session
        owner_id: User ID to process notes for
    """
    try:
        collection = get_collection()
        
        # Get all notes for this user that don't have embeddings
        notes_without_embeddings = (
            db_session.query(note.Note)
            .filter(note.Note.owner_id == owner_id)
            .filter(note.Note.embedding_model.is_(None))
            .all()
        )
        
        if not notes_without_embeddings:
            logger.debug(f"No notes without embeddings for user {owner_id}")
            return
        
        logger.info(f"Processing {len(notes_without_embeddings)} notes for user {owner_id}")
        
        for note_obj in notes_without_embeddings:
            try:
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
                        "tags": ",".join(note_obj.tags or []),
                        "created_at": note_obj.created_at.isoformat() if note_obj.created_at else "",
                    }],
                    documents=[note_obj.content or ""]
                )
                
                # Update the note in the database
                note_obj.embedding_model = model_id
                db_session.add(note_obj)
                
                logger.debug(f"Generated embedding for note {note_obj.id}")
                
            except Exception as exc:
                logger.error(
                    f"Failed to generate embedding for note {note_obj.id}: {exc}",
                    exc_info=True
                )
                # Continue processing other notes instead of failing completely
                continue
        
        try:
            db_session.commit()
            logger.info(f"Successfully processed embeddings for user {owner_id}")
        except Exception as commit_exc:
            logger.error(f"Database commit failed for user {owner_id}: {commit_exc}", exc_info=True)
            db_session.rollback()
            # Don't raise - the session is now clean
        
    except Exception as exc:
        logger.error(f"Error ensuring embeddings for user {owner_id}: {exc}", exc_info=True)
        try:
            db_session.rollback()
        except Exception:
            pass  # Already rolled back or session closed
        # Don't raise - allow the caller to continue without embeddings


def search_similar_notes(
    db_session: Session, 
    owner_id: int, 
    query: str, 
    limit: int = 10,
    min_similarity: float = 0.15  # Lower threshold for more results
) -> List[note.Note]:
    """
    Search for similar notes using vector similarity.
    
    Args:
        db_session: SQLAlchemy database session
        owner_id: User ID to search notes for
        query: Search query text
        limit: Maximum number of results to return
        min_similarity: Minimum cosine similarity score (0-1)
        
    Returns:
        List of similar notes ordered by similarity
    """
    try:
        collection = get_collection()
        
        # Generate embedding for the query
        try:
            query_embedding, model_used = generate_embedding(query)
            logger.info(f"Generated query embedding using {model_used}")
        except Exception as exc:
            logger.error(f"Failed to generate query embedding: {exc}", exc_info=True)
            return []
        
        # Search in ChromaDB with higher limit to allow filtering
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                where=build_where(owner_id),
                n_results=min(limit * 2, 100),  # Get more results to filter
                include=['distances']  # Include similarity scores
            )
        except Exception as exc:
            logger.error(f"ChromaDB query failed: {exc}", exc_info=True)
            return []
        
        if not results["ids"] or not results["ids"][0]:
            logger.debug(f"No similar notes found for user {owner_id}")
            return []
        
        # Get distances and filter by similarity threshold
        # ChromaDB returns cosine distance (0=identical, 2=opposite)
        # Convert to similarity: similarity = 1 - (distance / 2)
        note_ids_with_scores = []
        distances = results.get("distances")
        if distances and distances[0] and results["ids"] and results["ids"][0]:
            for note_id, distance in zip(results["ids"][0], distances[0]):
                similarity = 1.0 - (distance / 2.0)
                if similarity >= min_similarity:
                    note_ids_with_scores.append((int(note_id), similarity))
                    
            logger.info(f"Found {len(note_ids_with_scores)} notes above similarity threshold {min_similarity}")
        else:
            # Fallback if distances not available
            if results["ids"] and results["ids"][0]:
                note_ids_with_scores = [(int(id_), 0.5) for id_ in results["ids"][0][:limit]]
        
        # Sort by similarity and limit
        note_ids_with_scores.sort(key=lambda x: x[1], reverse=True)
        note_ids_with_scores = note_ids_with_scores[:limit]
        
        if not note_ids_with_scores:
            logger.info(f"No notes met similarity threshold {min_similarity}")
            return []
        
        # Get note IDs in order
        note_ids = [id_ for id_, _ in note_ids_with_scores]
        
        # Fetch the actual notes from the database
        notes = (
            db_session.query(note.Note)
            .filter(note.Note.id.in_(note_ids))
            .filter(note.Note.owner_id == owner_id)
            .all()
        )
        
        # Order notes by the similarity score order
        note_dict = {n.id: n for n in notes}
        ordered_notes = [note_dict[note_id] for note_id in note_ids if note_id in note_dict]
        
        logger.info(f"Returning {len(ordered_notes)} similar notes for user {owner_id} (query: '{query[:50]}')")
        return ordered_notes
        
    except Exception as exc:
        logger.error(f"Error searching notes for user {owner_id}: {exc}", exc_info=True)
        return []


def add_note_to_vector_store(db_session: Session, note_obj: note.Note) -> None:
    """
    Add a single note to the vector store.
    Does NOT commit the session - caller is responsible for commit.
    
    Args:
        db_session: SQLAlchemy database session
        note_obj: Note object to add
    """
    try:
        collection = get_collection()
        
        # Generate embedding
        try:
            embedding, model_id = generate_embedding(note_obj.content or "")
        except Exception as exc:
            logger.error(f"Failed to generate embedding for note {note_obj.id}: {exc}", exc_info=True)
            # Don't raise - allow note creation to succeed without embeddings
            return
        
        # Store in ChromaDB
        try:
            collection.add(
                ids=[str(note_obj.id)],
                embeddings=[embedding],
                metadatas=[{
                    "owner_id": note_obj.owner_id,
                    "embedding_model": model_id,
                    "title": note_obj.title or "",
                    "tags": ",".join(note_obj.tags or []),
                    "created_at": note_obj.created_at.isoformat() if note_obj.created_at else "",
                }],
                documents=[note_obj.content or ""]
            )
        except Exception as exc:
            logger.error(f"Failed to store embedding in ChromaDB for note {note_obj.id}: {exc}", exc_info=True)
            # Don't raise - allow note creation to succeed without embeddings
            return
        
        # Update the note in the database (don't commit - caller will do that)
        note_obj.embedding_model = model_id
        db_session.add(note_obj)
        logger.info(f"Successfully prepared note {note_obj.id} for vector store")
        
    except Exception as exc:
        logger.error(f"Unexpected error adding note {note_obj.id} to vector store: {exc}", exc_info=True)
        # Don't pollute the session - just log and continue


def delete_note_from_vector_store(note_id: int) -> None:
    """
    Remove a note from the vector store.
    
    Args:
        note_id: ID of the note to remove
    """
    try:
        collection = get_collection()
        collection.delete(ids=[str(note_id)])
        logger.info(f"Successfully deleted note {note_id} from vector store")
    except Exception as exc:
        logger.error(f"Error deleting note {note_id} from vector store: {exc}", exc_info=True)
        # Don't raise - deletion failures shouldn't block the main operation

