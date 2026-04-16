import asyncio

import pytest

from app.cache import close_cache_connection, get_cache, set_cache


@pytest.mark.asyncio
async def test_set_and_get_cache():
    await set_cache("test_key", {"data": "test_value"}, ttl=60)
    result = await get_cache("test_key")
    assert result == {"data": "test_value"}
    await close_cache_connection()


@pytest.mark.asyncio
async def test_get_cache_returns_none_for_missing_key():
    result = await get_cache("nonexistent_key")
    assert result is None
    await close_cache_connection()


@pytest.mark.asyncio
async def test_cache_respects_ttl():
    await set_cache("ttl_key", {"data": "expires"}, ttl=1)
    await asyncio.sleep(2)
    result = await get_cache("ttl_key")
    assert result is None
    await close_cache_connection()
