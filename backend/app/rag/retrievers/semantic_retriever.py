"""
Octopus AI Second Brain - Semantic Retriever
Retrieves relevant documents using semantic search.
"""
from typing import Any, Optional

from ..interfaces import Retriever, Embedder, VectorStore, QueryResult
from ...core.logging import get_logger

logger = get_logger(__name__)


class SemanticRetriever(Retriever):
    """
    Retriever that uses semantic similarity search.
    
    Combines embedding and vector store for retrieval.
    """
    
    def __init__(self, embedder: Embedder, vector_store: VectorStore) -> None:
        """
        Initialize the semantic retriever.
        
        Args:
            embedder: Embedder for query encoding
            vector_store: Vector store for similarity search
        """
        self.embedder = embedder
        self.vector_store = vector_store
        logger.info("Initialized SemanticRetriever")
    
    async def retrieve_async(
        self,
        query: str,
        k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> QueryResult:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query string
            k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            QueryResult with documents and scores
        """
        # Embed the query
        query_embedding = self.embedder.embed_query(query)
        
        # Search vector store
        result = await self.vector_store.search_async(
            query_embedding=query_embedding,
            k=k,
            filters=filters,
        )
        
        # Add query to result
        result.query = query
        
        logger.info(f"Retrieved {len(result.documents)} documents for query: {query[:50]}")
        
        return result
