from __future__ import annotations

import datetime
import json
import logging

from starlette.middleware.base import BaseHTTPMiddleware

from src.audit_log import write_log

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session_factory):
        super().__init__(app)
        self._session_factory = session_factory

    async def dispatch(self, request, call_next):
        # Skip audit for health and metrics endpoints
        if request.url.path in {"/health", "/healthz", "/readyz", "/metrics", "/openapi.json"}:
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Skip audit if session_factory is None (disabled for Phase 1 recovery)
        if self._session_factory is None:
            return await call_next(request)

        user_id = "anonymous"
        risk = "unknown"
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            body = await request.body()
            if body:
                try:
                    data = json.loads(body)
                    if isinstance(data, dict):
                        user_id = str(data.get("user_id") or user_id)
                        risk = str(data.get("risk") or data.get("risk_level") or risk)
                except Exception:
                    pass
        else:
            user_id = request.query_params.get("user_id", user_id)
            risk = request.query_params.get("risk", risk)

        payload = {
            "user_id": user_id,
            "risk": risk,
            "ts": datetime.datetime.utcnow().isoformat(),
        }

        response = await call_next(request)

        try:
            db_session = self._session_factory()
            try:
                write_log(
                    db_session,
                    user_id,
                    endpoint,
                    method,
                    payload,
                    ip_addr=request.client.host if request.client else "",
                    user_agent=request.headers.get("user-agent", ""),
                )
            finally:
                db_session.close()
        except Exception:
            logger.exception("audit_log_failed")

        return response
