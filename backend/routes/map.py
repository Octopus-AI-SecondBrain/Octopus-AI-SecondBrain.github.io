from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import numpy as np

from backend.models import db, note
from backend.routes.auth import get_current_user
from backend.services.vector_store import get_collection, ensure_user_embeddings
from backend.core.logging import get_logger

router = APIRouter()
logger = get_logger("secondbrain.map")


def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

# ---- Helpers ----

def _preview(text: str, n: int = 120) -> str:
    t = (text or "").strip().replace("\n", " ")
    return t[:n] + ("…" if len(t) > n else "")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    try:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot_product = np.dot(v1, v2)
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm_product == 0:
            return 0.0
        return float(dot_product / norm_product)
    except Exception as e:
        logger.error(f"Error computing cosine similarity: {e}")
        return 0.0


def calculate_tag_similarity(tags1: List[str], tags2: List[str]) -> float:
    """Calculate Jaccard similarity between two tag sets."""
    if not tags1 or not tags2:
        return 0.0
    set1 = set(tags1)
    set2 = set(tags2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


def calculate_keyword_similarity(title1: str, content1: str, title2: str, content2: str) -> float:
    """Calculate simple text similarity between two notes using keywords."""
    import re
    
    # Extract keywords from text
    def extract_keywords(text: str) -> set:
        words = re.findall(r'\b\w+\b', (text or "").lower())
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'it', 'this', 'that'}
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    # Get text content for comparison
    text1 = f"{title1 or ''} {content1 or ''}"
    text2 = f"{title2 or ''} {content2 or ''}"
    
    keywords1 = extract_keywords(text1)
    keywords2 = extract_keywords(text2)
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1.union(keywords2))
    
    return intersection / union if union > 0 else 0.0


@router.get("/")
def get_map(
    db_session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    min_similarity: float = Query(0.20, ge=0.0, le=1.0),
    top_k: int = Query(3, ge=1, le=20),
    max_nodes: int = Query(200, ge=2, le=2000),
    include_isolates: bool = Query(True),
    tags: Optional[str] = Query(None),
):
    """
    Return a neural graph built from notes for the logged-in user.
    Uses vector embeddings for semantic similarity when available,
    falls back to keyword/tag similarity otherwise.
    """
    try:
        # Ensure user embeddings are up to date
        try:
            ensure_user_embeddings(db_session, current_user.id)
        except Exception as e:
            logger.warning(f"Could not ensure embeddings for user {current_user.id}: {e}")
        
        # Get notes from database with optional tag filtering
        query = db_session.query(note.Note).filter(note.Note.owner_id == current_user.id)
        
        if tags:
            # Filter by tags if provided
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if tag_list:
                # Notes that have ANY of the specified tags
                query = query.filter(note.Note.tags.overlap(tag_list))
        
        notes = query.limit(max_nodes).all()
        
        if not notes:
            return {
                "nodes": [],
                "edges": [],
                "stats": {
                    "total_nodes": 0,
                    "total_edges": 0,
                    "avg_degree": 0,
                    "min_similarity": 0,
                    "max_similarity": 0,
                    "isolated_nodes": 0
                },
                "message": "No notes found. Create some notes to see the neural map!"
            }
        
        # Try to get embeddings from vector store
        embeddings_map = {}
        try:
            collection = get_collection()
            note_ids = [str(n.id) for n in notes]
            result = collection.get(ids=note_ids, include=["embeddings", "metadatas"])
            
            if result and result.get("ids"):
                embeddings = result.get("embeddings")
                if embeddings is not None:
                    for idx, note_id in enumerate(result["ids"]):
                        if idx < len(embeddings):
                            embeddings_map[note_id] = embeddings[idx]
                        
            logger.info(f"Retrieved {len(embeddings_map)} embeddings for {len(notes)} notes")
        except Exception as e:
            logger.warning(f"Could not retrieve embeddings from vector store: {e}")
        
        # Build nodes with enhanced metadata
        nodes = []
        note_lookup = {}
        
        for n in notes:
            # Determine node type based on tags and content
            note_tags = n.tags or []
            content_length = len(n.content or "")
            
            # Categorization based on tags first, then content
            if any(tag.lower() in ['idea', 'business', 'concept'] for tag in note_tags):
                node_type = "idea"
                color = "#F24D80"  # Primary brand color
            elif any(tag.lower() in ['ai', 'tech', 'technology', 'code'] for tag in note_tags):
                node_type = "technology"
                color = "#A855F7"  # Secondary brand color
            elif content_length > 500:
                node_type = "detailed"
                color = "#FF8F3C"  # Accent color
            else:
                node_type = "note"
                color = "#8B5CF6"  # Purple variant
            
            node_data = {
                "id": str(n.id),
                "label": n.title or f"Note {n.id}",
                "title": n.title or f"Note {n.id}",
                "preview": _preview(n.content or ""),
                "content": n.content or "",
                "tags": note_tags,
                "type": node_type,
                "color": color,
                "size": min(30 + content_length / 20, 100),
                "degree": 0,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "updated_at": n.updated_at.isoformat() if n.updated_at else None,
            }
            nodes.append(node_data)
            note_lookup[str(n.id)] = n
        
        # Build edges based on vector similarity (when available) or fallback
        edges = []
        edge_id = 0
        similarity_scores = []
        embedding_based_edges = 0
        
        for i, node1 in enumerate(nodes):
            # Track connections per node to respect top_k
            node_similarities = []
            
            for j, node2 in enumerate(nodes):
                if i >= j:  # Avoid duplicate edges
                    continue
                
                # Calculate similarity - prioritize embeddings when available
                similarity = 0.0
                has_embedding = False
                similarity_method = "keyword"
                
                if node1["id"] in embeddings_map and node2["id"] in embeddings_map:
                    # Use vector embeddings for semantic similarity (PRIMARY)
                    vec_sim = cosine_similarity(
                        embeddings_map[node1["id"]], 
                        embeddings_map[node2["id"]]
                    )
                    similarity = vec_sim
                    has_embedding = True
                    similarity_method = "embedding"
                else:
                    # Fallback to keyword similarity (SECONDARY)
                    n1 = note_lookup[node1["id"]]
                    n2 = note_lookup[node2["id"]]
                    similarity = calculate_keyword_similarity(
                        n1.title, n1.content, 
                        n2.title, n2.content
                    )
                    similarity_method = "keyword"
                
                # Add tag overlap bonus (up to +0.1 for better balance)
                tag_sim = calculate_tag_similarity(node1.get("tags", []), node2.get("tags", []))
                if tag_sim > 0:
                    # Boost similarity by tag overlap, capped at 1.0
                    tag_boost = tag_sim * 0.1
                    similarity = min(1.0, similarity + tag_boost)
                
                if similarity >= min_similarity:
                    node_similarities.append({
                        "target_id": node2["id"],
                        "similarity": similarity,
                        "has_embedding": has_embedding,
                        "method": similarity_method
                    })
            
            # Sort by similarity and take top_k connections
            node_similarities.sort(key=lambda x: x["similarity"], reverse=True)
            for conn in node_similarities[:top_k]:
                edges.append({
                    "id": str(edge_id),
                    "source": node1["id"],
                    "target": conn["target_id"],
                    "weight": conn["similarity"],
                    "similarity": conn["similarity"],
                    "label": f"{conn['similarity']:.2f}",
                    "color": f"rgba(242, 77, 128, {conn['similarity'] * 0.7})",
                    "has_embedding": conn["has_embedding"],
                    "method": conn["method"]
                })
                
                if conn["has_embedding"]:
                    embedding_based_edges += 1
                
                # Update node degrees
                node1["degree"] += 1
                # Find target node and update its degree
                for node in nodes:
                    if node["id"] == conn["target_id"]:
                        node["degree"] += 1
                        break
                
                similarity_scores.append(conn["similarity"])
                edge_id += 1
        
        # Calculate stats
        isolated_nodes = sum(1 for n in nodes if n["degree"] == 0)
        isolated_node_ids = [n["id"] for n in nodes if n["degree"] == 0]
        
        # Filter isolated nodes if requested
        if not include_isolates:
            connected_node_ids = set()
            for edge in edges:
                connected_node_ids.add(edge["source"])
                connected_node_ids.add(edge["target"])
            nodes = [n for n in nodes if n["id"] in connected_node_ids]
        
        # Enhanced statistics
        stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "avg_degree": sum(n["degree"] for n in nodes) / len(nodes) if nodes else 0,
            "min_similarity": min(similarity_scores) if similarity_scores else 0,
            "max_similarity": max(similarity_scores) if similarity_scores else 0,
            "avg_similarity": sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
            "isolated_nodes": isolated_nodes,
            "isolated_node_ids": isolated_node_ids[:10],  # Cap at 10 for response size
            "embedding_coverage": len(embeddings_map) / len(notes) if notes else 0,
            "embedding_based_edges": embedding_based_edges,
            "embedding_edge_ratio": embedding_based_edges / len(edges) if edges else 0
        }
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": stats,
            "message": f"Neural map with {len(nodes)} notes and {len(edges)} connections"
        }
        
    except Exception as e:
        logger.error(f"Map generation failed: {e}", exc_info=True)
        return {"nodes": [], "edges": [], "error": f"Map fetch failed: {str(e)}"}
