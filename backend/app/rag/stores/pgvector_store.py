"""
Octopus AI Second Brain - pgvector Vector Store
PostgreSQL-based vector storage using pgvector extension.
"""
from typing import Any, Optional
import uuid

import numpy as np
from numpy.typing import NDArray
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..interfaces import VectorStore, EmbeddedDocument, QueryResult
from ...db.models import Chunk, Embedding as EmbeddingModel, Document as DocumentModel
from ...core.logging import get_logger

logger = get_logger(__name__)


class PgVectorStore(VectorStore):
    """
    Vector store implementation using PostgreSQL + pgvector.
    
    This is the default vector store for Octopus AI Second Brain.
    It stores embeddings directly in PostgreSQL using the pgvector extension.
    """
    
    def __init__(self, session: AsyncSession, dimension: int = 384) -> None:
        """
        Initialize the pgvector store.
        
        Args:
            session: Async SQLAlchemy session
            dimension: Embedding vector dimension
        """
        self.session = session
        self.dimension = dimension
        logger.info(f"Initialized PgVectorStore with dimension={dimension}")
    
    async def add_documents_async(self, documents: list[EmbeddedDocument]) -> list[str]:
        """
        Add embedded documents to the vector store.
        
        Creates Chunk and Embedding records in the database.
        
        Args:
            documents: List of embedded documents to add
            
        Returns:
            List of document IDs (UUIDs as strings)
        """
        doc_ids = []
        
        for doc in documents:
            # Generate unique ID if not provided
            doc_id = doc.doc_id or str(uuid.uuid4())
            doc_ids.append(doc_id)
            
            # Get or create parent document
            # Note: In production, this should be passed or looked up properly
            # For now, we'll create a simple document record
            db_doc = DocumentModel(
                user_id=doc.metadata.get("user_id", 1),  # TODO: Get from context
                title=doc.metadata.get("title", "Untitled"),
                content=doc.content,
                doc_type=doc.metadata.get("modality", "text"),
                doc_metadata=doc.metadata,
                is_processed=True,
            )
            self.session.add(db_doc)
            await self.session.flush()
            
            # Create chunk
            chunk = Chunk(
                document_id=db_doc.id,
                content=doc.content,
                chunk_index=doc.metadata.get("chunk_index", 0),
                chunk_metadata=doc.metadata,
            )
            self.session.add(chunk)
            await self.session.flush()
            
            # Create embedding
            embedding = EmbeddingModel(
                chunk_id=chunk.id,
                embedding_vector=doc.embedding.tolist(),
                model_name=doc.embedding_model or "unknown",
                embedding_dimension=len(doc.embedding),
            )
            self.session.add(embedding)
            
            logger.debug(f"Added document {doc_id} with chunk {chunk.id}")
        
        await self.session.commit()
        logger.info(f"Added {len(doc_ids)} documents to pgvector store")
        
        return doc_ids
    
    async def search_async(
        self,
        query_embedding: NDArray[np.float32],
        k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> QueryResult:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filters: Optional metadata filters (modality, user_id, etc.)
            
        Returns:
            QueryResult with documents and similarity scores
        """
        # Import Vector type for runtime use
        from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
        from sqlalchemy import func
        
        # Build query
        query = (
            select(
                EmbeddingModel,
                Chunk,
                DocumentModel,
                # Cosine distance (1 - cosine similarity)
                EmbeddingModel.embedding_vector.cosine_distance(query_embedding.tolist()).label("distance")
            )
            .join(Chunk, Chunk.id == EmbeddingModel.chunk_id)
            .join(DocumentModel, DocumentModel.id == Chunk.document_id)
        )
        
        # Apply filters if provided
        if filters:
            if "user_id" in filters:
                query = query.where(DocumentModel.user_id == filters["user_id"])
            if "modality" in filters:
                query = query.where(DocumentModel.doc_type == filters["modality"])
        
        # Order by similarity and limit
        query = query.order_by("distance").limit(k)
        
        # Execute query
        result = await self.session.execute(query)
        rows = result.all()
        
        # Convert to EmbeddedDocument objects
        documents = []
        scores = []
        
        for emb, chunk, doc, distance in rows:
            # Convert distance to similarity score (1 - distance for cosine)
            similarity = 1.0 - distance
            scores.append(float(similarity))
            
            # Create EmbeddedDocument
            embedded_doc = EmbeddedDocument(
                content=chunk.content,
                metadata={
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "source": doc.title,
                    "modality": doc.doc_type,
                    **chunk.chunk_metadata,
                },
                doc_id=str(chunk.id),
                embedding=np.array(emb.embedding_vector, dtype=np.float32),
                embedding_model=emb.model_name,
            )
            documents.append(embedded_doc)
        
        logger.info(f"Retrieved {len(documents)} documents from pgvector store")
        
        return QueryResult(
            documents=documents,
            scores=scores,
            query="",  # Query text not stored here
            metadata={"store": "pgvector", "total_results": len(documents)},
        )
    
    async def search_keywords_async(
        self,
        query: str,
        k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> QueryResult:
        """
        Search for documents using BM25-style keyword search (PostgreSQL full-text search).

        Args:
            query: Query string
            k: Number of results to return
            filters: Optional metadata filters

        Returns:
            QueryResult with documents and relevance scores
        """
        from sqlalchemy import func, text

        # Create tsquery from plain text
        # PostgreSQL's to_tsquery with 'english' dictionary
        ts_query = func.plainto_tsquery('english', query)

        # Build query using PostgreSQL full-text search
        query_stmt = (
            select(
                EmbeddingModel,
                Chunk,
                DocumentModel,
                # ts_rank_cd provides BM25-like ranking
                func.ts_rank_cd(
                    func.to_tsvector('english', Chunk.content),
                    ts_query
                ).label("rank")
            )
            .join(Chunk, Chunk.id == EmbeddingModel.chunk_id)
            .join(DocumentModel, DocumentModel.id == Chunk.document_id)
            .where(
                func.to_tsvector('english', Chunk.content).op('@@')(ts_query)
            )
        )

        # Apply filters
        if filters:
            if "user_id" in filters:
                query_stmt = query_stmt.where(DocumentModel.user_id == filters["user_id"])
            if "modality" in filters:
                query_stmt = query_stmt.where(DocumentModel.doc_type == filters["modality"])

        # Order by relevance score (rank) descending
        query_stmt = query_stmt.order_by(text("rank DESC")).limit(k)

        # Execute query
        result = await self.session.execute(query_stmt)
        rows = result.all()

        # Convert to EmbeddedDocument objects
        documents = []
        scores = []

        for emb, chunk, doc, rank in rows:
            # Normalize BM25 score to 0-1 range (rank is typically 0-1 already)
            normalized_score = float(rank) if rank else 0.0
            scores.append(normalized_score)

            # Create EmbeddedDocument
            embedded_doc = EmbeddedDocument(
                content=chunk.content,
                metadata={
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "source": doc.title,
                    "modality": doc.doc_type,
                    "bm25_score": normalized_score,
                    **chunk.chunk_metadata,
                },
                doc_id=str(chunk.id),
                embedding=np.array(emb.embedding_vector, dtype=np.float32),
                embedding_model=emb.model_name,
            )
            documents.append(embedded_doc)

        logger.info(f"Retrieved {len(documents)} documents using keyword search")

        return QueryResult(
            documents=documents,
            scores=scores,
            query=query,
            metadata={"store": "pgvector", "search_type": "keywords", "total_results": len(documents)},
        )

    async def delete_async(self, doc_ids: list[str]) -> None:
        """
        Delete documents and their embeddings.

        Args:
            doc_ids: List of chunk IDs to delete (as strings)
        """
        # Convert string IDs to integers
        chunk_ids = [int(doc_id) for doc_id in doc_ids]

        # Delete chunks (cascades to embeddings)
        await self.session.execute(
            delete(Chunk).where(Chunk.id.in_(chunk_ids))
        )
        await self.session.commit()

        logger.info(f"Deleted {len(doc_ids)} documents from pgvector store")
    
    async def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        from sqlalchemy import func
        
        # Count total embeddings
        count_result = await self.session.execute(
            select(func.count(EmbeddingModel.id))
        )
        total_embeddings = count_result.scalar()
        
        # Get embedding dimensions distribution
        dim_result = await self.session.execute(
            select(
                EmbeddingModel.embedding_dimension,
                func.count(EmbeddingModel.id).label("count")
            ).group_by(EmbeddingModel.embedding_dimension)
        )
        dimensions = {row.embedding_dimension: row.count for row in dim_result}
        
        return {
            "total_embeddings": total_embeddings,
            "dimensions": dimensions,
            "backend": "pgvector",
        }
