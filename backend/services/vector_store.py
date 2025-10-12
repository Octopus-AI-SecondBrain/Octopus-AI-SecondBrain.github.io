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
        
    Raises:
        RuntimeError: If embedding generation or storage fails
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
        
        db_session.commit()
        logger.info(f"Successfully processed embeddings for user {owner_id}")
        
    except Exception as exc:
        logger.error(f"Error ensuring embeddings for user {owner_id}: {exc}", exc_info=True)
        db_session.rollback()
        raise RuntimeError(f"Failed to ensure embeddings: {exc}")


def search_similar_notes(
    db_session: Session, 
    owner_id: int, 
    query: str, 
    limit: int = 10
) -> List[note.Note]:
    """
    Search for similar notes using vector similarity.
    
    Args:
        db_session: SQLAlchemy database session
        owner_id: User ID to search notes for
        query: Search query text
        limit: Maximum number of results to return
        
    Returns:
        List of similar notes ordered by similarity
    """
    try:
        collection = get_collection()
        
        # Generate embedding for the query
        try:
            query_embedding, _ = generate_embedding(query)
        except Exception as exc:
            logger.error(f"Failed to generate query embedding: {exc}", exc_info=True)
            return []
        
        # Search in ChromaDB
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                where=build_where(owner_id),
                n_results=limit
            )
        except Exception as exc:
            logger.error(f"ChromaDB query failed: {exc}", exc_info=True)
            return []
        
        if not results["ids"] or not results["ids"][0]:
            logger.debug(f"No similar notes found for user {owner_id}")
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
        
        logger.info(f"Found {len(ordered_notes)} similar notes for user {owner_id}")
        return ordered_notes
        
    except Exception as exc:
        logger.error(f"Error searching notes for user {owner_id}: {exc}", exc_info=True)
        return []


def add_note_to_vector_store(db_session: Session, note_obj: note.Note) -> None:
    """
    Add a single note to the vector store.
    
    Args:
        db_session: SQLAlchemy database session
        note_obj: Note object to add
        
    Raises:
        RuntimeError: If embedding generation or storage fails
    """
    try:
        collection = get_collection()
        
        # Generate embedding
        try:
            embedding, model_id = generate_embedding(note_obj.content or "")
        except Exception as exc:
            logger.error(f"Failed to generate embedding for note {note_obj.id}: {exc}", exc_info=True)
            raise RuntimeError(f"Embedding generation failed: {exc}")
        
        # Store in ChromaDB
        try:
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
        except Exception as exc:
            logger.error(f"Failed to store embedding in ChromaDB for note {note_obj.id}: {exc}", exc_info=True)
            raise RuntimeError(f"ChromaDB storage failed: {exc}")
        
        # Update the note in the database
        note_obj.embedding_model = model_id
        db_session.add(note_obj)
        db_session.commit()
        
        logger.info(f"Successfully added note {note_obj.id} to vector store")
        
    except RuntimeError:
        db_session.rollback()
        raise
    except Exception as exc:
        logger.error(f"Unexpected error adding note {note_obj.id} to vector store: {exc}", exc_info=True)
        db_session.rollback()
        raise RuntimeError(f"Failed to add note to vector store: {exc}")


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

