"""
Caching layer for RAG components.
Provides Redis-backed caching for embeddings and search results.
"""
import hashlib
import json
import pickle
import base64
from typing import Any, Optional
import numpy as np
from numpy.typing import NDArray

from app.core.redis import get_redis
from app.core.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingCache:
    """
    Cache for text embeddings to avoid redundant API calls.

    Caches embedding vectors by text content hash, dramatically reducing
    embedding API costs and latency for repeated queries.
    """

    def __init__(self):
        self._settings = get_settings()
        self._ttl = self._settings.redis.cache_ttl_embeddings

    @staticmethod
    def _get_cache_key(text: str, model: str) -> str:
        """
        Generate cache key for text embedding.

        Uses SHA256 hash to handle arbitrary text lengths and special characters.

        Args:
            text: Text content
            model: Embedding model name

        Returns:
            Cache key string
        """
        # Hash text content for consistent key generation
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        return f"embedding:{model}:{text_hash}"

    async def get(self, text: str, model: str) -> Optional[NDArray[np.float32]]:
        """
        Get cached embedding for text.

        Args:
            text: Text content
            model: Embedding model name

        Returns:
            Cached embedding vector or None if not found
        """
        try:
            redis = await get_redis()
            cache_key = self._get_cache_key(text, model)

            cached_data = await redis.get(cache_key)
            if not cached_data:
                return None

            # Deserialize embedding (stored as base64-encoded numpy array)
            embedding_bytes = base64.b64decode(cached_data)
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

            logger.debug(f"Embedding cache HIT for text (len={len(text)}, model={model})")
            return embedding

        except Exception as e:
            logger.warning(f"Failed to get cached embedding: {e}")
            return None

    async def set(
        self,
        text: str,
        model: str,
        embedding: NDArray[np.float32],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache embedding for text.

        Args:
            text: Text content
            model: Embedding model name
            embedding: Embedding vector
            ttl: Cache TTL in seconds (default: from settings)

        Returns:
            True if cache write successful
        """
        try:
            redis = await get_redis()
            cache_key = self._get_cache_key(text, model)

            # Serialize embedding as base64-encoded bytes
            embedding_bytes = embedding.tobytes()
            embedding_b64 = base64.b64encode(embedding_bytes).decode('utf-8')

            # Store with TTL
            success = await redis.set(
                cache_key,
                embedding_b64,
                ttl=ttl or self._ttl,
            )

            if success:
                logger.debug(f"Embedding cached for text (len={len(text)}, model={model})")

            return success

        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")
            return False

    async def invalidate(self, text: str, model: str) -> bool:
        """
        Invalidate cached embedding.

        Args:
            text: Text content
            model: Embedding model name

        Returns:
            True if invalidation successful
        """
        try:
            redis = await get_redis()
            cache_key = self._get_cache_key(text, model)
            return await redis.delete(cache_key)
        except Exception as e:
            logger.warning(f"Failed to invalidate embedding cache: {e}")
            return False


class SearchCache:
    """
    Cache for search results to speed up repeated queries.

    Caches complete search results including documents, scores, and metadata.
    Invalidated when documents are added, updated, or deleted.
    """

    def __init__(self):
        self._settings = get_settings()
        self._ttl = self._settings.redis.cache_ttl_search

    @staticmethod
    def _get_cache_key(
        query: str,
        k: int,
        filters: Optional[dict[str, Any]],
        search_type: str = "hybrid",
    ) -> str:
        """
        Generate cache key for search query.

        Args:
            query: Search query
            k: Number of results
            filters: Search filters
            search_type: Type of search (semantic, keyword, hybrid)

        Returns:
            Cache key string
        """
        # Create deterministic representation of query parameters
        cache_params = {
            "query": query,
            "k": k,
            "filters": filters or {},
            "search_type": search_type,
        }

        # Hash parameters
        params_str = json.dumps(cache_params, sort_keys=True)
        params_hash = hashlib.sha256(params_str.encode('utf-8')).hexdigest()[:16]

        return f"search:{search_type}:{params_hash}"

    async def get(
        self,
        query: str,
        k: int,
        filters: Optional[dict[str, Any]],
        search_type: str = "hybrid",
    ) -> Optional[dict[str, Any]]:
        """
        Get cached search results.

        Args:
            query: Search query
            k: Number of results
            filters: Search filters
            search_type: Type of search

        Returns:
            Cached search results or None if not found
        """
        try:
            redis = await get_redis()
            cache_key = self._get_cache_key(query, k, filters, search_type)

            cached_data = await redis.get(cache_key)
            if not cached_data:
                return None

            # Deserialize search results (stored as pickled dict)
            results = pickle.loads(base64.b64decode(cached_data))

            logger.debug(
                f"Search cache HIT for query '{query[:50]}...' "
                f"(k={k}, type={search_type})"
            )
            return results

        except Exception as e:
            logger.warning(f"Failed to get cached search results: {e}")
            return None

    async def set(
        self,
        query: str,
        k: int,
        filters: Optional[dict[str, Any]],
        search_type: str,
        results: dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache search results.

        Args:
            query: Search query
            k: Number of results
            filters: Search filters
            search_type: Type of search
            results: Search results to cache
            ttl: Cache TTL in seconds (default: from settings)

        Returns:
            True if cache write successful
        """
        try:
            redis = await get_redis()
            cache_key = self._get_cache_key(query, k, filters, search_type)

            # Serialize results (pickle for complex objects)
            results_pickled = pickle.dumps(results)
            results_b64 = base64.b64encode(results_pickled).decode('utf-8')

            # Store with TTL
            success = await redis.set(
                cache_key,
                results_b64,
                ttl=ttl or self._ttl,
            )

            if success:
                logger.debug(
                    f"Search results cached for query '{query[:50]}...' "
                    f"(k={k}, type={search_type})"
                )

            return success

        except Exception as e:
            logger.warning(f"Failed to cache search results: {e}")
            return False

    async def invalidate_user(self, user_id: int) -> int:
        """
        Invalidate all search results for a user.

        Called when user's documents are modified.

        Args:
            user_id: User ID

        Returns:
            Number of cache keys invalidated
        """
        try:
            redis = await get_redis()

            # Find all search cache keys for this user
            # Note: In production, maintain a set of cache keys per user for efficient invalidation
            pattern = f"search:*:{user_id}:*"
            keys = await redis.scan(pattern)

            # Delete all matching keys
            deleted = 0
            for key in keys:
                if await redis.delete(key):
                    deleted += 1

            if deleted > 0:
                logger.info(f"Invalidated {deleted} search cache entries for user {user_id}")

            return deleted

        except Exception as e:
            logger.warning(f"Failed to invalidate user search cache: {e}")
            return 0

    async def invalidate_all(self) -> int:
        """
        Invalidate all search results (use sparingly).

        Returns:
            Number of cache keys invalidated
        """
        try:
            redis = await get_redis()

            # Find all search cache keys
            pattern = "search:*"
            keys = await redis.scan(pattern)

            # Delete all matching keys
            deleted = 0
            for key in keys:
                if await redis.delete(key):
                    deleted += 1

            if deleted > 0:
                logger.warning(f"Invalidated ALL {deleted} search cache entries")

            return deleted

        except Exception as e:
            logger.warning(f"Failed to invalidate all search cache: {e}")
            return 0


# Global cache instances
_embedding_cache: Optional[EmbeddingCache] = None
_search_cache: Optional[SearchCache] = None


async def get_embedding_cache() -> EmbeddingCache:
    """Get embedding cache instance (singleton)"""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache()
    return _embedding_cache


async def get_search_cache() -> SearchCache:
    """Get search cache instance (singleton)"""
    global _search_cache
    if _search_cache is None:
        _search_cache = SearchCache()
    return _search_cache
