from __future__ import annotations

import datetime
import json

from starlette.middleware.base import BaseHTTPMiddleware

from src.audit_log import write_log


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session_factory):
        super().__init__(app)
        self._session_factory = session_factory

    async def dispatch(self, request, call_next):
        if request.url.path in {"/health", "/healthz", "/readyz", "/metrics"}:
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

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

        db_session = self._session_factory()
        try:
            write_log(db_session, user_id, endpoint, method, payload)
        finally:
            db_session.close()

        return response
