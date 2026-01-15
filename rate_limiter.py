from __future__ import annotations

import os
import time
from dataclasses import dataclass

import redis


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after: float


class TokenBucketStore:
    def allow(self, key: str, capacity: int, refill_rate: float) -> RateLimitResult:
        raise NotImplementedError


class InMemoryTokenBucketStore(TokenBucketStore):
    def __init__(self) -> None:
        self._state: dict[str, tuple[float, float]] = {}

    def allow(self, key: str, capacity: int, refill_rate: float) -> RateLimitResult:
        now = time.time()
        tokens, updated_at = self._state.get(key, (float(capacity), now))
        elapsed = max(0.0, now - updated_at)
        tokens = min(float(capacity), tokens + elapsed * refill_rate)
        if tokens < 1.0:
            retry_after = (1.0 - tokens) / refill_rate if refill_rate else 1.0
            self._state[key] = (tokens, now)
            return RateLimitResult(False, retry_after)
        tokens -= 1.0
        self._state[key] = (tokens, now)
        return RateLimitResult(True, 0.0)


class RedisTokenBucketStore(TokenBucketStore):
    def __init__(self, client: redis.Redis) -> None:
        self.client = client
        self._script = self.client.register_script(
            """
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            local requested = tonumber(ARGV[4])
            local data = redis.call('HMGET', key, 'tokens', 'timestamp')
            local tokens = tonumber(data[1])
            local timestamp = tonumber(data[2])
            if tokens == nil then
                tokens = capacity
                timestamp = now
            end
            local elapsed = math.max(0, now - timestamp)
            local filled = math.min(capacity, tokens + (elapsed * refill_rate))
            local allowed = filled >= requested
            local new_tokens = allowed and (filled - requested) or filled
            redis.call('HMSET', key, 'tokens', new_tokens, 'timestamp', now)
            local ttl = 60
            if refill_rate > 0 then
                ttl = math.ceil(capacity / refill_rate)
            end
            redis.call('EXPIRE', key, ttl)
            if allowed then
                return {1, new_tokens}
            end
            return {0, new_tokens}
            """
        )

    def allow(self, key: str, capacity: int, refill_rate: float) -> RateLimitResult:
        now = time.time()
        allowed, tokens = self._script(keys=[key], args=[capacity, refill_rate, now, 1])
        allowed = bool(int(allowed))
        retry_after = (
            (1.0 - float(tokens)) / refill_rate if not allowed and refill_rate else 0.0
        )
        return RateLimitResult(allowed, retry_after)


def build_rate_limiter_store() -> TokenBucketStore:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return InMemoryTokenBucketStore()
    client = redis.Redis.from_url(redis_url, decode_responses=False)
    return RedisTokenBucketStore(client)


class TokenBucketRateLimiter:
    def __init__(
        self, capacity: int, refill_rate: float, store: TokenBucketStore
    ) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.store = store

    def allow(self, identifier: str) -> RateLimitResult:
        return self.store.allow(identifier, self.capacity, self.refill_rate)


def load_rate_limit_settings() -> tuple[int, float]:
    per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    burst = int(os.getenv("RATE_LIMIT_BURST", "20"))
    refill_rate = per_minute / 60.0 if per_minute > 0 else 0.0
    return burst, refill_rate
