import json
from typing import Any, Optional

import redis.asyncio as redis

from app.config import settings

_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    return _redis_client


async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache by key."""
    client = await get_redis_client()
    value = await client.get(key)

    if value is None:
        return None

    return json.loads(value)


async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache with optional TTL seconds."""
    client = await get_redis_client()
    cache_ttl = ttl if ttl is not None else settings.REDIS_CACHE_TTL
    await client.setex(key, cache_ttl, json.dumps(value, ensure_ascii=False))
    return True


async def close_cache_connection() -> None:
    """Close Redis connection."""
    global _redis_client

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
