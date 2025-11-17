"""
Octopus AI Second Brain - Sentence Transformer Embedder
Text embedding using Sentence Transformers library.
"""
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from ..interfaces import Embedder, Document, EmbeddedDocument
from ...core.logging import get_logger
from ...core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class SentenceTransformerEmbedder(Embedder):
    """
    Embedder using Sentence Transformers for text embedding.
    
    Default model: all-MiniLM-L6-v2 (384 dimensions)
    Fast and efficient for semantic search.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        batch_size: int = 32,
    ) -> None:
        """
        Initialize the sentence transformer embedder.
        
        Args:
            model_name: HuggingFace model name (default from settings)
            device: Device to run model on ('cpu' or 'cuda')
            batch_size: Batch size for embedding
        """
        from sentence_transformers import SentenceTransformer
        
        self._model_name = model_name or settings.rag_embedder.text_model
        self._device = device or settings.rag_embedder.device
        self._batch_size = batch_size or settings.rag_embedder.batch_size
        
        logger.info(f"Loading Sentence Transformer model: {self._model_name}")
        self.model = SentenceTransformer(self._model_name, device=self._device)
        dim = self.model.get_sentence_embedding_dimension()
        if dim is None:
            raise ValueError(f"Could not determine embedding dimension for model {self._model_name}")
        self._dimension: int = dim
        
        logger.info(
            f"Loaded {self._model_name} on {self._device} "
            f"(dimension={self._dimension}, batch_size={self._batch_size})"
        )
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self._dimension
    
    @property
    def model_name(self) -> str:
        """Name of the embedding model"""
        return self._model_name
    
    def embed_query(self, query: str) -> NDArray[np.float32]:
        """
        Embed a single query string.
        
        Args:
            query: Query text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embedding.astype(np.float32)
    
    async def embed_async(self, documents: list[Document]) -> list[EmbeddedDocument]:
        """
        Asynchronously embed multiple documents.
        
        Note: sentence-transformers doesn't have true async support,
        so we run in a thread pool for non-blocking behavior.
        
        Args:
            documents: List of documents to embed
            
        Returns:
            List of embedded documents
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def _embed_batch(docs: list[Document]) -> list[EmbeddedDocument]:
            """Embed a batch of documents synchronously"""
            if not docs:
                return []
            
            # Extract text content
            texts = [doc.content for doc in docs]
            
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=self._batch_size,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            
            # Create EmbeddedDocument objects
            embedded_docs = []
            for doc, embedding in zip(docs, embeddings):
                embedded_doc = EmbeddedDocument(
                    content=doc.content,
                    metadata=doc.metadata.copy(),
                    doc_id=doc.doc_id,
                    created_at=doc.created_at,
                    embedding=embedding.astype(np.float32),
                    embedding_model=self._model_name,
                )
                embedded_docs.append(embedded_doc)
            
            return embedded_docs
        
        # Run embedding in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            embedded_docs = await loop.run_in_executor(
                executor,
                _embed_batch,
                documents
            )
        
        logger.info(f"Embedded {len(documents)} documents")
        return embedded_docs
    
    def embed_batch(self, texts: list[str]) -> NDArray[np.float32]:
        """
        Embed a batch of text strings directly.
        
        Useful for bulk operations where Document objects aren't needed.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            2D numpy array of embeddings (num_texts, dimension)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=self._batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.astype(np.float32)
