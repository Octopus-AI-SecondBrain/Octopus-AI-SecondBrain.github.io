from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.models import db, note
from backend.routes.auth import get_current_user

router = APIRouter()


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


@router.get("/")
def get_map(
    db_session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    min_similarity: float = Query(0.45, ge=0.0, le=1.0),
    top_k: int = Query(3, ge=1, le=20),
    max_nodes: int = Query(200, ge=2, le=2000),
    include_isolates: bool = Query(True),
):
    """Return a neural graph built from notes for the logged-in user."""
    try:
        # Get notes from database
        notes = (
            db_session.query(note.Note)
            .filter(note.Note.owner_id == current_user.id)
            .limit(max_nodes)
            .all()
        )
        
        if not notes:
            return {
                "nodes": [],
                "edges": [],
                "message": "No notes found. Create some notes to see the neural map!"
            }
        
        # Build nodes with enhanced metadata
        nodes = []
        for i, n in enumerate(notes):
            # Determine node type based on content
            content_length = len(n.content or "")
            title_length = len(n.title or "")
            
            # Simple categorization
            if "business" in (n.title or "").lower() or "idea" in (n.title or "").lower():
                node_type = "idea"
                color = "#FF6B6B"  # Red for ideas
            elif content_length > 500:
                node_type = "detailed"
                color = "#4ECDC4"  # Teal for detailed notes
            elif "AI" in (n.title or "") or "tech" in (n.title or "").lower():
                node_type = "technology"
                color = "#45B7D1"  # Blue for tech
            else:
                node_type = "note"
                color = "#96CEB4"  # Green for regular notes
            
            nodes.append({
                "id": str(n.id),
                "label": n.title or f"Note {n.id}",
                "title": n.title or f"Note {n.id}",
                "preview": _preview(n.content or ""),
                "content": n.content or "",
                "type": node_type,
                "color": color,
                "size": min(30 + content_length / 20, 100),  # Size based on content length
                "degree": 0,  # Will be calculated below
                "position": {
                    "x": (i % 10) * 100,  # Simple grid layout
                    "y": (i // 10) * 100,
                    "z": 0
                }
            })
        
        # Build edges based on content similarity
        edges = []
        edge_id = 0
        
        for i, node1 in enumerate(nodes):
            connections = 0
            for j, node2 in enumerate(nodes):
                if i >= j:  # Avoid duplicate edges
                    continue
                
                # Calculate simple similarity based on shared keywords
                similarity = calculate_similarity(node1, node2)
                
                if similarity >= min_similarity and connections < top_k:
                    edges.append({
                        "id": str(edge_id),
                        "source": node1["id"],
                        "target": node2["id"],
                        "weight": similarity,
                        "label": f"{similarity:.2f}",
                        "color": f"rgba(100, 100, 100, {similarity})"
                    })
                    
                    # Update node degrees
                    node1["degree"] += 1
                    node2["degree"] += 1
                    connections += 1
                    edge_id += 1
        
        # Filter isolated nodes if requested
        if not include_isolates:
            connected_node_ids = set()
            for edge in edges:
                connected_node_ids.add(edge["source"])
                connected_node_ids.add(edge["target"])
            nodes = [n for n in nodes if n["id"] in connected_node_ids]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "avg_degree": sum(n["degree"] for n in nodes) / len(nodes) if nodes else 0
            },
            "message": f"Neural map with {len(nodes)} notes and {len(edges)} connections"
        }
        
    except Exception as e:
        return {"nodes": [], "edges": [], "error": f"Map fetch failed: {e}"}


def calculate_similarity(node1: Dict[str, Any], node2: Dict[str, Any]) -> float:
    """Calculate simple text similarity between two nodes."""
    import re
    
    # Extract keywords from both nodes
    def extract_keywords(text: str) -> set:
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    # Get text content for comparison
    text1 = f"{node1.get('title', '')} {node1.get('content', '')}"
    text2 = f"{node2.get('title', '')} {node2.get('content', '')}"
    
    keywords1 = extract_keywords(text1)
    keywords2 = extract_keywords(text2)
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1.union(keywords2))
    
    return intersection / union if union > 0 else 0.0
