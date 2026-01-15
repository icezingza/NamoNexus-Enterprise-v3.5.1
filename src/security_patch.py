import os
from random import SystemRandom

from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

_sr = SystemRandom()


def secure_random_uniform(a: float, b: float) -> float:
    """Drop-in replacement for random.uniform() using cryptographically secure PRNG."""
    return _sr.uniform(a, b)


def add_https_redirect(app: FastAPI) -> None:
    """Add HTTPS redirect middleware only in production & not localhost."""
    env = os.getenv("ENVIRONMENT", "dev")
    host = os.getenv("HOST", "localhost")
    if env == "production" and host != "localhost":
        app.add_middleware(HTTPSRedirectMiddleware)
