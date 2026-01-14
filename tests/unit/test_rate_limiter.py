from rate_limiter import InMemoryTokenBucketStore, TokenBucketRateLimiter


def test_rate_limiter_blocks_when_exceeded():
    store = InMemoryTokenBucketStore()
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate=0.0, store=store)

    assert limiter.allow("client-1").allowed is True
    assert limiter.allow("client-1").allowed is True
    assert limiter.allow("client-1").allowed is False
