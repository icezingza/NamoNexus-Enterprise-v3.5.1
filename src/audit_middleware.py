from __future__ import annotations

import json

from starlette.datastructures import UploadFile
from starlette.middleware.base import BaseHTTPMiddleware

from src.audit_log import write_log


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session_factory):
        super().__init__(app)
        self._session_factory = session_factory

    async def dispatch(self, request, call_next):
        if request.url.path in {"/health", "/healthz", "/readyz", "/metrics"}:
            return await call_next(request)

        ip_addr = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")[:500]
        method = request.method
        endpoint = request.url.path

        payload = {}
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            for key, value in form.items():
                if isinstance(value, UploadFile):
                    payload[key] = {
                        "filename": value.filename,
                        "content_type": value.content_type,
                    }
                else:
                    payload[key] = str(value)[:1000]
        else:
            body = await request.body()
            if body:
                try:
                    payload = json.loads(body)
                except Exception:
                    payload = {"raw": body.decode("utf-8", "replace")[:1000]}

        user_id = payload.get("user_id", "anonymous")

        response = await call_next(request)

        db_session = self._session_factory()
        try:
            write_log(db_session, user_id, endpoint, method, ip_addr, user_agent, payload)
        finally:
            db_session.close()

        return response
