from __future__ import annotations

import logging
import math
import os
import time
import uuid
from datetime import datetime
from typing import Dict

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from cache import build_cache_from_env
from core_engine import HarmonicGovernor
from database import GridIntelligence
from metrics import record_metrics
from models import MultiModalAnalysis, TriageRequest, TriageResponse
from rate_limiter import (
    TokenBucketRateLimiter,
    build_rate_limiter_store,
    load_rate_limit_settings,
)
from structured_logging import configure_logging, trace_id_var
from tasks import process_triage_background

configure_logging()
logger = logging.getLogger("namo_nexus")

AUTH_TOKEN = os.getenv("NAMO_NEXUS_TOKEN", "namo-nexus-enterprise-2026")
DB_PATH = os.getenv("DB_PATH", os.path.join("data", "namo_nexus_sovereign.db"))

app = FastAPI(
    title="NamoNexus Enterprise API",
    version="3.5.1",
    description="Mental Health Infrastructure AI - Production Hardened",
)
security = HTTPBearer()


class NamoNexusEnterprise:
    """Main triage engine for NamoNexus Enterprise v3.5.1."""

    def __init__(self, db_path: str, cache_backend=None) -> None:
        self.governor = HarmonicGovernor()
        self.grid = GridIntelligence(db_path, cache=cache_backend)

    async def process_triage(
        self, request: TriageRequest, background_tasks: BackgroundTasks
    ) -> TriageResponse:
        start = time.time()
        session_id = request.session_id or self._generate_session_id()

        result = await self.governor.orchestrate(
            request.message,
            request.voice_features,
            request.facial_features,
        )

        multimodal = result["multimodal"]
        ethics = result["ethics"]
        response_text = self._generate_response(request.message, ethics, multimodal)
        human_required = ethics["requires_human"] or multimodal.combined_risk > 0.7

        background_tasks.add_task(
            self._background_process,
            request,
            session_id,
            response_text,
            ethics,
            multimodal,
            human_required,
        )

        latency = (time.time() - start) * 1000

        return TriageResponse(
            response=response_text,
            risk_level=ethics["risk_level"],
            dharma_score=ethics["dharma_score"],
            emotional_tone=ethics["emotional_tone"],
            multimodal_confidence=multimodal.confidence,
            latency_ms=latency,
            session_id=session_id,
            human_handoff_required=human_required,
            empathy_prompts=(
                self.grid._generate_empathy_prompts(ethics["risk_level"])
                if human_required
                else None
            ),
        )

    def _generate_response(
        self, message: str, ethics: Dict, multimodal: MultiModalAnalysis
    ) -> str:
        tone = ethics["emotional_tone"]
        risk = ethics["risk_level"]

        if tone == "compassionate":
            greeting = "พี่ครับ ผมรู้สึกว่าพี่กำลังลำบากใจมากนะ "
        elif tone == "supportive":
            greeting = "สวัสดีครับ ผมพร้อมรับฟังพี่นะ "
        else:
            greeting = "สวัสดีครับ "

        if risk == "severe":
            main = "ผมเห็นว่าพี่กำลังเจอช่วงเวลาที่ยากลำบากมาก พี่ไม่ได้อยู่คนเดียวนะครับ ให้ผมช่วยพี่ได้ไหม"
        elif risk == "moderate":
            main = "ขอบคุณที่ไว้วางใจเล่าให้ฟังนะครับ ผมเข้าใจความรู้สึกของพี่"
        else:
            main = "ยินดีที่ได้พูดคุยกับพี่ครับ"

        dharma_note = ""
        if ethics["principles"]:
            dharma_note = f" (หลักธรรม: {', '.join(ethics['principles'])})"

        return f"{greeting}{main}{dharma_note}"

    def _background_process(
        self,
        request: TriageRequest,
        session_id: str,
        response: str,
        ethics: Dict,
        multimodal: MultiModalAnalysis,
        human_required: bool,
    ) -> None:
        payload = {
            "user_id": request.user_id,
            "session_id": session_id,
            "message": request.message,
            "response": response,
            "risk_level": ethics["risk_level"],
            "dharma_score": ethics["dharma_score"],
            "multimodal": {
                "combined_risk": multimodal.combined_risk,
                "confidence": multimodal.confidence,
            },
            "human_required": human_required,
        }
        broker_url = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL")
        try:
            if broker_url:
                process_triage_background.delay(payload)
            else:
                process_triage_background(payload)
        except Exception:
            logger.exception("triage_background_enqueue_failed")
            process_triage_background(payload)
        if human_required:
            logger.warning(
                "crisis_alert_enqueued user_id=%s session_id=%s",
                request.user_id,
                session_id,
            )

    @staticmethod
    def _generate_session_id() -> str:
        return f"session_{uuid.uuid4().hex[:12]}"


cache_backend = build_cache_from_env()
engine = NamoNexusEnterprise(DB_PATH, cache_backend=cache_backend)
rate_limit_capacity, rate_limit_refill = load_rate_limit_settings()
rate_limit_store = build_rate_limiter_store()
rate_limiter = TokenBucketRateLimiter(
    capacity=rate_limit_capacity,
    refill_rate=rate_limit_refill,
    store=rate_limit_store,
)


@app.post("/triage", response_model=TriageResponse)
async def triage_endpoint(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    credentials=Depends(security),
):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await engine.process_triage(request, background_tasks)


@app.post("/interact", response_model=TriageResponse)
async def interact_alias(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    credentials=Depends(security),
):
    return await triage_endpoint(request, background_tasks, credentials)


@app.post("/reflect", response_model=TriageResponse)
async def reflect_alias(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    credentials=Depends(security),
):
    return await triage_endpoint(request, background_tasks, credentials)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in {"/health", "/healthz", "/ready", "/readyz", "/metrics"}:
        return await call_next(request)
    identifier = request.headers.get("X-API-Key")
    if not identifier and request.client:
        identifier = request.client.host
    identifier = identifier or "anonymous"
    result = rate_limiter.allow(identifier)
    if not result.allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"Retry-After": str(max(1, math.ceil(result.retry_after)))},
        )
    return await call_next(request)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    token = trace_id_var.set(trace_id)
    start = time.time()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        logger.exception(
            "request_failed method=%s path=%s", request.method, request.url.path
        )
        raise
    finally:
        latency_ms = (time.time() - start) * 1000
        record_metrics(request.method, request.url.path, status_code, latency_ms)
        logger.info(
            "request_completed method=%s path=%s status=%s latency_ms=%.2f",
            request.method,
            request.url.path,
            status_code,
            latency_ms,
        )
        trace_id_var.reset(token)


@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "system": "NamoNexus Enterprise",
        "version": "3.5.1",
        "grid_status": "sovereign",
        "fixes": ["connection_pool", "non_blocking_io"],
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/healthz")
async def healthz():
    return {"status": "alive"}


@app.get("/ready")
async def readiness_check():
    db_ready = False
    cache_ready = False
    try:
        with engine.grid.db_pool.get_connection() as conn:
            conn.execute("SELECT 1")
        db_ready = True
    except Exception:
        logger.exception("readiness_db_failed")
    try:
        cache_ready = engine.grid.cache.ping()
    except Exception:
        logger.exception("readiness_cache_failed")
    status = "ready" if db_ready and cache_ready else "degraded"
    return {"status": status, "db_ready": db_ready, "cache_ready": cache_ready}


@app.get("/readyz")
async def readyz():
    return await readiness_check()


@app.get("/metrics")
async def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/harmonic-console")
async def get_harmonic_console_global(credentials=Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401)

    metrics = engine.grid.get_global_metrics()
    sessions = engine.grid.get_recent_sessions()
    alerts = engine.grid.get_all_alerts()

    return {
        "metrics": metrics,
        "recent_sessions": sessions,
        "active_alerts": alerts,
    }


@app.get("/harmonic-console/{session_id}")
async def get_harmonic_console_session(session_id: str, credentials=Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401)

    history = engine.grid.get_session_history(session_id)
    alerts = engine.grid.get_alerts(session_id)

    return {
        "session_id": session_id,
        "conversation_history": history,
        "crisis_alerts": alerts,
        "empathy_guidance": alerts[0].get("prompts", []) if alerts else [],
    }
