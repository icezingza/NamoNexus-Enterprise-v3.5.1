from __future__ import annotations

import json
import os
import time
from typing import Any, Optional

import redis

DEFAULT_CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "30"))


class CacheBackend:
    def get(self, key: str) -> Optional[str]:
        raise NotImplementedError

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def ping(self) -> bool:
        raise NotImplementedError

    def get_json(self, key: str) -> Optional[Any]:
        raw = self.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        self.set(key, json.dumps(value), ttl_seconds)


class InMemoryCache(CacheBackend):
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, Optional[float]]] = {}

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if not entry:
            return None
        value, expires_at = entry
        if expires_at is not None and expires_at <= time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def ping(self) -> bool:
        return True


class RedisCache(CacheBackend):
    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    def get(self, key: str) -> Optional[str]:
        value = self.client.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self.client.set(name=key, value=value, ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def ping(self) -> bool:
        return bool(self.client.ping())


def build_cache_from_env() -> CacheBackend:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return InMemoryCache()
    client = redis.Redis.from_url(redis_url, decode_responses=False)
    return RedisCache(client)
