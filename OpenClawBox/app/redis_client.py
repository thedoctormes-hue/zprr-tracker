"""Redis client for rate limiting and caching."""

import os
import json
import time
from typing import Optional, Any

import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class RedisClient:
    """Async Redis client for rate limiting and caching."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.from_url(
                REDIS_URL,
                decode_responses=True
            )
        return cls._instance

    async def check_rate_limit(self, key: str, limit: int, window: int = 60) -> tuple[bool, int]:
        """
        Check rate limit using sliding window.
        Returns (allowed, remaining).
        """
        now = int(time.time())
        pipeline = self.client.pipeline()

        pipeline.zremrangebyscore(key, 0, now - window)
        pipeline.zcard(key)
        pipeline.zadd(key, {str(now): now})
        pipeline.expire(key, window)

        results = await pipeline.execute()
        current = results[1]

        remaining = max(0, limit - current - 1)
        allowed = current < limit

        return allowed, remaining

    async def get_cached(self, key: str) -> Optional[Any]:
        """Get cached value."""
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_cached(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Cache value with TTL."""
        await self.client.setex(key, ttl, json.dumps(value))

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        return await self.client.incrby(key, amount)

    async def get(self, key: str) -> Optional[str]:
        """Get string value."""
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set string value with TTL."""
        await self.client.setex(key, ttl, value)


# Global instance
redis_client = RedisClient()