"""
Octopus AI Second Brain - RAG Core Interfaces
Abstract base classes for the RAG system components.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
from numpy.typing import NDArray


@dataclass
class Document:
    """
    A document in the knowledge base.
    
    Attributes:
        content: The textual representation of the document
        metadata: Arbitrary key/value pairs (source, page, timestamp, etc.)
        doc_id: Unique identifier for the document
        created_at: Timestamp when the document was created
    """
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    doc_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Ensure metadata has required fields"""
        if "source" not in self.metadata:
            self.metadata["source"] = "unknown"
        if "modality" not in self.metadata:
            self.metadata["modality"] = "text"


@dataclass
class EmbeddedDocument(Document):
    """
    A document with an associated embedding vector.
    
    Attributes:
        embedding: Dense vector representation of the document
        embedding_model: Identifier of the model used to create the embedding
    """
    embedding: NDArray[np.float32] = field(default_factory=lambda: np.array([], dtype=np.float32))
    embedding_model: Optional[str] = None


@dataclass
class QueryResult:
    """
    Result from a retrieval query.
    
    Attributes:
        documents: List of retrieved documents
        scores: Similarity scores for each document
        query: Original query string
        metadata: Additional metadata about the retrieval
    """
    documents: list[EmbeddedDocument]
    scores: list[float] = field(default_factory=list)
    query: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class Loader(ABC):
    """
    Abstract base class for document loaders.
    
    Loaders are responsible for reading files and converting them to Document objects.
    """
    
    @abstractmethod
    async def load_async(self, source: str | Path) -> list[Document]:
        """
        Asynchronously load documents from a source.
        
        Args:
            source: File path, URL, or other source identifier
            
        Returns:
            List of Document objects extracted from the source
            
        Raises:
            ValueError: If source format is unsupported
            IOError: If source cannot be read
        """
        pass
    
    def load(self, source: str | Path) -> list[Document]:
        """
        Synchronously load documents from a source.
        
        Args:
            source: File path, URL, or other source identifier
            
        Returns:
            List of Document objects extracted from the source
        """
        import asyncio
        return asyncio.run(self.load_async(source))
    
    @abstractmethod
    def supports(self, source: str | Path) -> bool:
        """
        Check if this loader supports the given source.
        
        Args:
            source: File path or URL to check
            
        Returns:
            True if this loader can handle the source
        """
        pass


class Embedder(ABC):
    """
    Abstract base class for embedding models.
    
    Embedders convert text or other content into dense vector representations.
    """
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimension of the embedding vectors"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the embedding model"""
        pass
    
    @abstractmethod
    def embed_query(self, query: str) -> NDArray[np.float32]:
        """
        Embed a single query string.
        
        Args:
            query: Query text to embed
            
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    async def embed_async(self, documents: list[Document]) -> list[EmbeddedDocument]:
        """
        Asynchronously embed multiple documents.
        
        Args:
            documents: List of documents to embed
            
        Returns:
            List of embedded documents
        """
        pass
    
    def embed(self, documents: list[Document]) -> list[EmbeddedDocument]:
        """
        Synchronously embed multiple documents.
        
        Args:
            documents: List of documents to embed
            
        Returns:
            List of embedded documents
        """
        import asyncio
        return asyncio.run(self.embed_async(documents))


class VectorStore(ABC):
    """
    Abstract base class for vector storage and retrieval.
    
    Vector stores manage embedding storage and similarity search.
    """
    
    @abstractmethod
    async def add_documents_async(self, documents: list[EmbeddedDocument]) -> list[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of embedded documents to add
            
        Returns:
            List of document IDs
        """
        pass
    
    @abstractmethod
    async def search_async(
        self,
        query_embedding: NDArray[np.float32],
        k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> QueryResult:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            QueryResult with documents and scores
        """
        pass
    
    @abstractmethod
    async def delete_async(self, doc_ids: list[str]) -> None:
        """
        Delete documents from the store.
        
        Args:
            doc_ids: List of document IDs to delete
        """
        pass


class Retriever(ABC):
    """
    Abstract base class for retrieval strategies.
    
    Retrievers orchestrate embedding and search operations.
    """
    
    @abstractmethod
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
        pass


class Generator(ABC):
    """
    Abstract base class for answer generation.
    
    Generators use LLMs to create answers based on retrieved context.
    """
    
    @abstractmethod
    async def generate_async(
        self,
        query: str,
        context_documents: list[EmbeddedDocument],
        **kwargs: Any,
    ) -> str:
        """
        Generate an answer based on query and context.
        
        Args:
            query: User query
            context_documents: Retrieved documents for context
            **kwargs: Additional generation parameters
            
        Returns:
            Generated answer text
        """
        pass
    
    def generate(
        self,
        query: str,
        context_documents: list[EmbeddedDocument],
        **kwargs: Any,
    ) -> str:
        """
        Synchronously generate an answer.
        
        Args:
            query: User query
            context_documents: Retrieved documents for context
            **kwargs: Additional generation parameters
            
        Returns:
            Generated answer text
        """
        import asyncio
        return asyncio.run(self.generate_async(query, context_documents, **kwargs))
