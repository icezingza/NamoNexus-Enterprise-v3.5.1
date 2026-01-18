from __future__ import annotations

import os
from typing import Iterable, Set
from urllib.parse import urlparse


DEFAULT_ALLOWED_SERVICES = {"local", "gemini"}


def _normalize_allowed(raw: str) -> Set[str]:
    cleaned = raw.strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned[1:-1]
    parts = [item.strip().strip("'\"") for item in cleaned.split(",")]
    return {item.lower() for item in parts if item}


def get_allowed_services() -> Set[str]:
    raw = os.getenv("ALLOWED_SERVICES")
    if not raw:
        return set(DEFAULT_ALLOWED_SERVICES)
    return _normalize_allowed(raw)


def ensure_service_allowed(service: str, allowed_services: Iterable[str] | None = None) -> None:
    allowed = set(allowed_services) if allowed_services is not None else get_allowed_services()
    if service.lower() not in allowed:
        raise RuntimeError(
            f"Service '{service}' is not allowed. Allowed services: {sorted(allowed)}"
        )


def _is_local_host(host: str) -> bool:
    normalized = host.lower().strip()
    return normalized in {"localhost", "127.0.0.1", "::1"} or normalized.endswith(".local")


def ensure_url_allowed(url: str, allowed_services: Iterable[str] | None = None) -> None:
    allowed = set(allowed_services) if allowed_services is not None else get_allowed_services()
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        if "local" not in allowed:
            raise RuntimeError(
                f"Local URLs are not allowed. Allowed services: {sorted(allowed)}"
            )
        return
    if _is_local_host(host):
        ensure_service_allowed("local", allowed_services=allowed)
        return
    if "gemini" in host.lower():
        ensure_service_allowed("gemini", allowed_services=allowed)
        return
    raise RuntimeError(
        f"Outbound URL '{url}' is not allowed. Allowed services: {sorted(allowed)}"
    )
