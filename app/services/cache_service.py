import time
from typing import Any, Optional

_cache: dict = {}


def get(key: str) -> Optional[Any]:
    entry = _cache.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.time() > expires_at:
        del _cache[key]
        return None
    return value


def set(key: str, value: Any, ttl: int = 10):
    _cache[key] = (value, time.time() + ttl)


def delete(key: str):
    _cache.pop(key, None)


def flush():
    _cache.clear()
