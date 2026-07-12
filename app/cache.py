from aiocache import Cache
from aiocache.decorators import cached

# Initialize in-memory cache with SimpleCache backend
cache = Cache(Cache.MEMORY)

# We can use @cached(ttl=300, key="menuItems") or similar on our router endpoints.
