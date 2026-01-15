from __future__ import annotations

import logging
import os
from typing import Dict

# Celery is optional - fallback to direct execution
try:
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    Celery = None
    HAS_CELERY = False

from cache import build_cache_from_env
from database import GridIntelligence
from sanitization import sanitize_text

logger = logging.getLogger("namo_nexus")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))
CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL", CELERY_BROKER_URL)

if HAS_CELERY:
    celery_app = Celery("namo_nexus", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)
    app = celery_app
else:
    celery_app = None
    app = None


def _process_triage_impl(payload: Dict) -> None:
    """Core implementation of triage background processing."""
    db_path = os.getenv("DB_PATH", os.path.join("data", "namo_nexus_sovereign.db"))
    cache = build_cache_from_env()
    grid = GridIntelligence(db_path, cache=cache)
    message = sanitize_text(payload.get("message", ""))

    grid.store_sovereign(
        {
            "user_id": payload["user_id"],
            "session_id": payload["session_id"],
            "message": message,
            "response": payload["response"],
            "risk_level": payload["risk_level"],
            "dharma_score": payload["dharma_score"],
            "multimodal": payload["multimodal"],
        }
    )

    if payload.get("human_required"):
        grid.create_crisis_alert(
            {
                "user_id": payload["user_id"],
                "session_id": payload["session_id"],
                "risk_level": payload["risk_level"],
            }
        )


if HAS_CELERY:
    @celery_app.task(name="namo_nexus.process_triage_background")
    def process_triage_background(payload: Dict) -> None:
        _process_triage_impl(payload)
else:
    def process_triage_background(payload: Dict) -> None:
        """Fallback: run directly when Celery is not available."""
        try:
            _process_triage_impl(payload)
        except Exception:
            logger.exception("process_triage_background_failed")
