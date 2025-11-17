"""
Cached Embedder - Wraps any embedder with Redis caching.
"""
from typing import Sequence
import numpy as np
from numpy.typing import NDArray

from ..interfaces import Embedder, Document, EmbeddedDocument
from ..caching import get_embedding_cache
from ...core.logging import get_logger

logger = get_logger(__name__)


class CachedEmbedder(Embedder):
    """
    Embedder wrapper that caches embeddings in Redis.

    Dramatically reduces embedding API costs and latency by caching results.
    Transparently wraps any embedder implementation.

    Benefits:
    - Reduces API costs (OpenAI charges per token)
    - Reduces latency (cached lookups are ~100x faster)
    - Handles cache misses gracefully
    - Works with any embedder backend

    Usage:
        base_embedder = SentenceTransformerEmbedder()
        cached_embedder = CachedEmbedder(base_embedder)
        embeddings = cached_embedder.embed_documents(docs)  # Uses cache when available
    """

    def __init__(self, embedder: Embedder):
        """
        Initialize cached embedder.

        Args:
            embedder: Base embedder to wrap with caching
        """
        self.embedder = embedder
        self._model_name = getattr(embedder, 'model_name', embedder.__class__.__name__)
        logger.info(f"Initialized CachedEmbedder wrapping {self._model_name}")

    @property
    def dimension(self) -> int:
        """Dimension of the embedding vectors from the wrapped embedder."""
        return self.embedder.dimension

    @property
    def model_name(self) -> str:
        """Name of the wrapped embedding model."""
        return self._model_name

    def embed_documents(self, documents: Sequence[Document]) -> list[EmbeddedDocument]:
        """
        Embed documents with caching.

        Checks cache for each document. On cache miss, falls back to base embedder.

        Args:
            documents: Documents to embed

        Returns:
            List of embedded documents
        """
        import asyncio

        # Run async cache operations in sync context
        return asyncio.run(self._embed_documents_async(documents))

    async def _embed_documents_async(self, documents: Sequence[Document]) -> list[EmbeddedDocument]:
        """Async implementation of embed_documents"""
        cache = await get_embedding_cache()

        # Separate cached and uncached documents
        cached_embeddings: dict[int, NDArray[np.float32]] = {}
        uncached_indices: list[int] = []
        uncached_docs: list[Document] = []

        # Check cache for each document
        for idx, doc in enumerate(documents):
            try:
                cached_emb = await cache.get(doc.content, self.model_name)
                if cached_emb is not None:
                    cached_embeddings[idx] = cached_emb
                    continue
            except Exception as e:
                logger.warning(f"Cache get failed: {e}, will re-embed document")

            uncached_indices.append(idx)
            uncached_docs.append(doc)

        logger.debug(
            f"Embedding cache: {len(cached_embeddings)} hits, "
            f"{len(uncached_docs)} misses out of {len(documents)} documents"
        )

        # Embed uncached documents using base embedder
        newly_embedded: list[EmbeddedDocument] = []
        if uncached_docs:
            newly_embedded = self.embedder.embed_documents(uncached_docs)

            # Cache newly generated embeddings
            for doc, embedded_doc in zip(uncached_docs, newly_embedded):
                try:
                    await cache.set(doc.content, self.model_name, embedded_doc.embedding)
                except Exception as e:
                    logger.warning(f"Cache set failed: {e}, continuing without caching")

        # Combine cached and newly embedded documents in original order
        result: list[EmbeddedDocument] = []
        newly_embedded_iter = iter(newly_embedded)

        for idx, doc in enumerate(documents):
            if idx in cached_embeddings:
                # Use cached embedding
                result.append(
                    EmbeddedDocument(
                        content=doc.content,
                        metadata=doc.metadata,
                        doc_id=doc.doc_id,
                        embedding=cached_embeddings[idx],
                        embedding_model=self.model_name,
                    )
                )
            else:
                # Use newly generated embedding
                result.append(next(newly_embedded_iter))

        return result

    def embed_query(self, query: str) -> NDArray[np.float32]:
        """
        Embed query with caching.

        Args:
            query: Query string

        Returns:
            Query embedding vector
        """
        import asyncio

        return asyncio.run(self._embed_query_async(query))

    async def _embed_query_async(self, query: str) -> NDArray[np.float32]:
        """Async implementation of embed_query"""
        cache = await get_embedding_cache()

        # Check cache
        try:
            cached_emb = await cache.get(query, self.model_name)
            if cached_emb is not None:
                logger.debug(f"Query embedding cache HIT for '{query[:50]}...'")
                return cached_emb
        except Exception as e:
            logger.warning(f"Query cache get failed: {e}, will re-embed query")

        # Cache miss - generate embedding
        logger.debug(f"Query embedding cache MISS for '{query[:50]}...'")
        embedding = self.embedder.embed_query(query)

        # Cache result
        try:
            await cache.set(query, self.model_name, embedding)
        except Exception as e:
            logger.warning(f"Query cache set failed: {e}, continuing without caching")

        return embedding

    async def embed_async(self, documents: list[Document]) -> list[EmbeddedDocument]:
        """
        Asynchronously embed multiple documents with caching.

        Args:
            documents: Documents to embed

        Returns:
            List of embedded documents
        """
        return await self._embed_documents_async(documents)
