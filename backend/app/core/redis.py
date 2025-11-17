"""
Redis connection manager with connection pooling and health checks.
Supports graceful fallback to in-memory storage when Redis is unavailable.
"""
import json
import logging
from typing import Any, Optional
from datetime import timedelta

import redis.asyncio as aioredis
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Manages Redis connections with automatic fallback to in-memory storage.
    Provides caching, job queue, and session management capabilities.
    """

    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[Redis] = None
        self._enabled: bool = True
        self._in_memory_cache: dict[str, Any] = {}
        settings = get_settings()
        self._settings = settings.redis

    async def initialize(self) -> None:
        """Initialize Redis connection pool"""
        if not self._settings.enabled:
            logger.info("Redis disabled in settings, using in-memory fallback")
            self._enabled = False
            return

        try:
            # Create connection pool
            self._pool = ConnectionPool.from_url(
                self._settings.url,
                max_connections=self._settings.max_connections,
                socket_timeout=self._settings.socket_timeout,
                socket_connect_timeout=self._settings.socket_connect_timeout,
                decode_responses=True,
                encoding="utf-8",
            )

            # Create Redis client
            self._redis = Redis(connection_pool=self._pool)

            # Test connection
            await self._redis.ping()
            logger.info(f"✅ Redis connected: {self._settings.url}")
            self._enabled = True

        except (RedisConnectionError, RedisError) as e:
            logger.warning(
                f"⚠️ Redis connection failed: {e}. Falling back to in-memory storage."
            )
            self._enabled = False
            self._redis = None
            self._pool = None

    async def close(self) -> None:
        """Close Redis connections"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")

        if self._pool:
            await self._pool.disconnect()
            logger.info("Redis connection pool closed")

        self._in_memory_cache.clear()

    async def health_check(self) -> dict[str, Any]:
        """Check Redis health status"""
        if not self._enabled:
            return {
                "status": "disabled",
                "backend": "in-memory",
                "message": "Redis is disabled, using in-memory storage",
            }

        if not self._redis:
            return {
                "status": "unhealthy",
                "backend": "in-memory",
                "message": "Redis connection not initialized",
            }

        try:
            await self._redis.ping()
            info = await self._redis.info("server")
            return {
                "status": "healthy",
                "backend": "redis",
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
            }
        except (RedisConnectionError, RedisError) as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "backend": "redis",
                "error": str(e),
            }

    # ==================== Cache Operations ====================

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self._enabled or not self._redis:
            return self._in_memory_cache.get(key)

        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET failed for {key}: {e}")
            return self._in_memory_cache.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache with optional TTL"""
        if not self._enabled or not self._redis:
            self._in_memory_cache[key] = value
            return True

        try:
            if ttl:
                await self._redis.setex(key, ttl, value)
            else:
                await self._redis.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET failed for {key}: {e}")
            self._in_memory_cache[key] = value
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._enabled or not self._redis:
            self._in_memory_cache.pop(key, None)
            return True

        try:
            await self._redis.delete(key)
            self._in_memory_cache.pop(key, None)
            return True
        except RedisError as e:
            logger.error(f"Redis DELETE failed for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._enabled or not self._redis:
            return key in self._in_memory_cache

        try:
            return bool(await self._redis.exists(key))
        except RedisError as e:
            logger.error(f"Redis EXISTS failed for {key}: {e}")
            return key in self._in_memory_cache

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on existing key"""
        if not self._enabled or not self._redis:
            # In-memory storage doesn't support expiration
            return True

        try:
            return bool(await self._redis.expire(key, ttl))
        except RedisError as e:
            logger.error(f"Redis EXPIRE failed for {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache"""
        value = await self.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON for {key}: {e}")
            return None

    async def set_json(
        self,
        key: str,
        value: dict,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set JSON value in cache"""
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to encode JSON for {key}: {e}")
            return False

    # ==================== Hash Operations ====================

    async def hset(self, name: str, key: str, value: str) -> bool:
        """Set hash field"""
        if not self._enabled or not self._redis:
            if name not in self._in_memory_cache:
                self._in_memory_cache[name] = {}
            self._in_memory_cache[name][key] = value
            return True

        try:
            await self._redis.hset(name, key, value)
            return True
        except RedisError as e:
            logger.error(f"Redis HSET failed for {name}.{key}: {e}")
            return False

    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field"""
        if not self._enabled or not self._redis:
            hash_data = self._in_memory_cache.get(name, {})
            return hash_data.get(key)

        try:
            return await self._redis.hget(name, key)
        except RedisError as e:
            logger.error(f"Redis HGET failed for {name}.{key}: {e}")
            return None

    async def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        if not self._enabled or not self._redis:
            return self._in_memory_cache.get(name, {})

        try:
            return await self._redis.hgetall(name)
        except RedisError as e:
            logger.error(f"Redis HGETALL failed for {name}: {e}")
            return {}

    async def hdel(self, name: str, key: str) -> bool:
        """Delete hash field"""
        if not self._enabled or not self._redis:
            if name in self._in_memory_cache:
                self._in_memory_cache[name].pop(key, None)
            return True

        try:
            await self._redis.hdel(name, key)
            return True
        except RedisError as e:
            logger.error(f"Redis HDEL failed for {name}.{key}: {e}")
            return False

    # ==================== List Operations ====================

    async def lpush(self, key: str, *values: str) -> int:
        """Push values to list (left)"""
        if not self._enabled or not self._redis:
            if key not in self._in_memory_cache:
                self._in_memory_cache[key] = []
            self._in_memory_cache[key] = list(values) + self._in_memory_cache[key]
            return len(self._in_memory_cache[key])

        try:
            return await self._redis.lpush(key, *values)
        except RedisError as e:
            logger.error(f"Redis LPUSH failed for {key}: {e}")
            return 0

    async def rpush(self, key: str, *values: str) -> int:
        """Push values to list (right)"""
        if not self._enabled or not self._redis:
            if key not in self._in_memory_cache:
                self._in_memory_cache[key] = []
            self._in_memory_cache[key].extend(values)
            return len(self._in_memory_cache[key])

        try:
            return await self._redis.rpush(key, *values)
        except RedisError as e:
            logger.error(f"Redis RPUSH failed for {key}: {e}")
            return 0

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        """Get list range"""
        if not self._enabled or not self._redis:
            list_data = self._in_memory_cache.get(key, [])
            return list_data[start : end + 1 if end != -1 else None]

        try:
            return await self._redis.lrange(key, start, end)
        except RedisError as e:
            logger.error(f"Redis LRANGE failed for {key}: {e}")
            return []

    async def lpop(self, key: str) -> Optional[str]:
        """Pop value from list (left)"""
        if not self._enabled or not self._redis:
            list_data = self._in_memory_cache.get(key, [])
            if list_data:
                return list_data.pop(0)
            return None

        try:
            return await self._redis.lpop(key)
        except RedisError as e:
            logger.error(f"Redis LPOP failed for {key}: {e}")
            return None

    async def rpop(self, key: str) -> Optional[str]:
        """Pop value from list (right)"""
        if not self._enabled or not self._redis:
            list_data = self._in_memory_cache.get(key, [])
            if list_data:
                return list_data.pop()
            return None

        try:
            return await self._redis.rpop(key)
        except RedisError as e:
            logger.error(f"Redis RPOP failed for {key}: {e}")
            return None

    async def blpop(self, key: str, timeout: int = 0) -> Optional[tuple[str, str]]:
        """Blocking pop from list (left)"""
        if not self._enabled or not self._redis:
            # Non-blocking for in-memory
            list_data = self._in_memory_cache.get(key, [])
            if list_data:
                value = list_data.pop(0)
                return (key, value)
            return None

        try:
            result = await self._redis.blpop(key, timeout=timeout)
            return result if result else None
        except RedisError as e:
            logger.error(f"Redis BLPOP failed for {key}: {e}")
            return None

    # ==================== Key Pattern Operations ====================

    async def keys(self, pattern: str) -> list[str]:
        """Get keys matching pattern (use carefully in production)"""
        if not self._enabled or not self._redis:
            import fnmatch

            return [k for k in self._in_memory_cache.keys() if fnmatch.fnmatch(k, pattern)]

        try:
            return await self._redis.keys(pattern)
        except RedisError as e:
            logger.error(f"Redis KEYS failed for pattern {pattern}: {e}")
            return []

    async def scan(self, match: str, count: int = 100):
        """Scan keys matching pattern (preferred over keys())"""
        if not self._enabled or not self._redis:
            # Fallback to keys for in-memory
            return await self.keys(match)

        try:
            keys = []
            async for key in self._redis.scan_iter(match=match, count=count):
                keys.append(key)
            return keys
        except RedisError as e:
            logger.error(f"Redis SCAN failed for pattern {match}: {e}")
            return []


# Global Redis manager instance
_redis_manager: Optional[RedisManager] = None


async def get_redis() -> RedisManager:
    """Get Redis manager instance (singleton)"""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
        await _redis_manager.initialize()
    return _redis_manager


async def close_redis() -> None:
    """Close Redis connections"""
    global _redis_manager
    if _redis_manager:
        await _redis_manager.close()
        _redis_manager = None
