"""
Octopus AI Second Brain - RAG Service
Orchestrates the RAG workflow: loading, embedding, storing, retrieving, and generating.
"""
from pathlib import Path
from typing import Any, Optional
import time

from sqlalchemy.ext.asyncio import AsyncSession

from ..rag.interfaces import Document
from ..rag.loaders.text_loader import TextLoader
from ..rag.loaders.pdf_loader import PDFLoader
from ..rag.embedders.sentence_transformer import SentenceTransformerEmbedder
from ..rag.stores.pgvector_store import PgVectorStore
from ..rag.retrievers.semantic_retriever import SemanticRetriever
from ..rag.generators.openai_generator import OpenAIGenerator
from ..core.logging import get_logger
from ..core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class RAGService:
    """
    Service for managing RAG operations.
    
    Orchestrates loading, embedding, retrieval, and generation.
    """
    
    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initialize RAG service.
        
        Args:
            db_session: Database session for persistence
        """
        self.db_session = db_session
        
        # Initialize components
        self.embedder = SentenceTransformerEmbedder()
        self.vector_store = PgVectorStore(db_session, dimension=self.embedder.dimension)
        self.retriever = SemanticRetriever(self.embedder, self.vector_store)
        self.generator = OpenAIGenerator()
        
        # Initialize loaders
        self.loaders = {
            "text": TextLoader(),
            "pdf": PDFLoader(),
        }
        
        logger.info("Initialized RAGService")
    
    async def ingest_file(
        self,
        file_path: Path,
        user_id: int,
        metadata: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Ingest a file into the RAG system.
        
        Args:
            file_path: Path to the file
            user_id: User ID for ownership
            metadata: Additional metadata
            
        Returns:
            Number of chunks ingested
        """
        # Determine loader based on file extension
        loader = None
        for loader_type, loader_instance in self.loaders.items():
            if loader_instance.supports(file_path):
                loader = loader_instance
                break
        
        if not loader:
            raise ValueError(f"No loader found for file: {file_path}")
        
        # Load documents
        documents = await loader.load_async(file_path)
        
        # Add user_id to metadata
        for doc in documents:
            doc.metadata["user_id"] = user_id
            if metadata:
                doc.metadata.update(metadata)
        
        # Embed documents
        embedded_docs = await self.embedder.embed_async(documents)
        
        # Store embeddings
        doc_ids = await self.vector_store.add_documents_async(embedded_docs)
        
        logger.info(f"Ingested {len(doc_ids)} chunks from {file_path}")
        
        return len(doc_ids)
    
    async def ingest_text(
        self,
        text: str,
        title: str,
        user_id: int,
        metadata: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Ingest raw text into the RAG system.
        
        Args:
            text: Text content
            title: Document title
            user_id: User ID for ownership
            metadata: Additional metadata
            
        Returns:
            Number of chunks ingested
        """
        from ..core.utils import chunk_text
        
        # Chunk the text
        chunks = chunk_text(
            text,
            settings.rag_ingestion.chunk_size,
            settings.rag_ingestion.chunk_overlap,
        )
        
        # Create Document objects
        documents = []
        for idx, chunk in enumerate(chunks):
            doc = Document(
                content=chunk,
                metadata={
                    "source": title,
                    "modality": "text",
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "user_id": user_id,
                    **(metadata or {}),
                },
            )
            documents.append(doc)
        
        # Embed documents
        embedded_docs = await self.embedder.embed_async(documents)
        
        # Store embeddings
        doc_ids = await self.vector_store.add_documents_async(embedded_docs)
        
        logger.info(f"Ingested {len(doc_ids)} chunks from text '{title}'")
        
        return len(doc_ids)
    
    async def search(
        self,
        query: str,
        k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> tuple[list[dict[str, Any]], float]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results
            filters: Metadata filters
            
        Returns:
            Tuple of (results list, response time in ms)
        """
        start_time = time.time()
        
        # Retrieve documents
        result = await self.retriever.retrieve_async(query, k=k, filters=filters)
        
        # Format results
        results = []
        for doc, score in zip(result.documents, result.scores):
            results.append({
                "content": doc.content,
                "score": score,
                "metadata": doc.metadata,
                "chunk_id": doc.metadata.get("chunk_id"),
                "document_id": doc.metadata.get("document_id"),
            })
        
        response_time = (time.time() - start_time) * 1000
        
        logger.info(f"Search returned {len(results)} results in {response_time:.2f}ms")
        
        return results, response_time
    
    async def answer(
        self,
        query: str,
        k: int = 10,
        filters: Optional[dict[str, Any]] = None,
        **gen_kwargs: Any,
    ) -> tuple[str, list[dict[str, Any]], float]:
        """
        Generate an answer to a question using RAG.
        
        Args:
            query: User question
            k: Number of context documents
            filters: Metadata filters
            **gen_kwargs: Generation parameters (temperature, max_tokens)
            
        Returns:
            Tuple of (answer, sources, response time in ms)
        """
        start_time = time.time()
        
        # Retrieve relevant documents
        result = await self.retriever.retrieve_async(query, k=k, filters=filters)
        
        # Generate answer
        answer = await self.generator.generate_async(
            query,
            result.documents,
            **gen_kwargs,
        )
        
        # Format sources
        sources = []
        for doc, score in zip(result.documents, result.scores):
            sources.append({
                "content": doc.content,
                "score": score,
                "metadata": doc.metadata,
                "chunk_id": doc.metadata.get("chunk_id"),
                "document_id": doc.metadata.get("document_id"),
            })
        
        response_time = (time.time() - start_time) * 1000
        
        logger.info(f"Generated answer in {response_time:.2f}ms")
        
        return answer, sources, response_time
    
    async def get_stats(self) -> dict[str, Any]:
        """
        Get RAG system statistics.
        
        Returns:
            Dictionary with system stats
        """
        store_stats = await self.vector_store.get_stats()
        
        return {
            "total_embeddings": store_stats.get("total_embeddings", 0),
            "vector_store_backend": store_stats.get("backend", "pgvector"),
            "embedding_model": self.embedder.model_name,
            "embedding_dimension": self.embedder.dimension,
        }
