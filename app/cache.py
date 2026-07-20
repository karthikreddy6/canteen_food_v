"""Shared cache for menu reads.

Redis can be enabled with ``CACHE_REDIS_URL``.  Development and single-process
deployments automatically use an in-process cache when Redis is not configured.
"""

import json
from typing import Any, Optional

from aiocache import Cache

from app.config import settings


def _build_cache():
    if settings.CACHE_REDIS_URL:
        try:
            return Cache.from_url(settings.CACHE_REDIS_URL, namespace="onfood")
        except Exception:
            # A cache outage must never prevent the API from starting.
            pass
    return Cache(Cache.MEMORY, namespace="onfood")


cache = _build_cache()


async def get_json(key: str) -> Optional[Any]:
    value = await cache.get(key)
    return json.loads(value) if value is not None else None


async def set_json(key: str, value: Any, ttl: int) -> None:
    await cache.set(key, json.dumps(value, default=str), ttl=ttl)


async def invalidate_menu_cache() -> None:
    """Invalidate every cached student menu representation after a menu write."""
    for key in (
        "menu:all", "menu:categories", "menu:discounts", "menu:specials",
    ):
        await cache.delete(key)
    # Paged and category-specific keys use a prefix.
    try:
        await cache.clear(namespace="onfood")
    except TypeError:
        # SimpleMemoryCache.clear does not accept namespace on some versions.
        await cache.clear()
