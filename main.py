from __future__ import annotations

import asyncio
import logging
import math
import os
import secrets
import threading
import time
import uuid
from datetime import datetime
from typing import Dict

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from cache import build_cache_from_env
from core_engine import HarmonicGovernor
from database import GridIntelligence
from metrics import record_metrics
from models import MultiModalAnalysis, TriageResponse
from rate_limiter import (
    TokenBucketRateLimiter,
    build_rate_limiter_store,
    load_rate_limit_settings,
)
from sanitization import sanitize_text
from structured_logging import configure_logging, trace_id_var
from src.auth_utils import verify_token
from src.schemas_day2 import InteractRequest, ReflectRequest, TriageRequest
from src.security_patch import add_https_redirect

configure_logging()
logger = logging.getLogger("namo_nexus")


# ---------- Minimal CORS helper (compatible 5a71b0a7) ----------
def load_cors_origins() -> list[str]:
    """
    Return allowed CORS origins from env.
    If CORS_ORIGINS is not set → allow localhost only.
    Format: comma-separated, no space.
    """
    raw = os.getenv("CORS_ORIGINS")
    if not raw:
        raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://localhost:8080")
    return [o.strip() for o in raw.split(",") if o.strip()]

DB_PATH = os.getenv("DB_PATH", os.path.join("data", "namo_nexus_sovereign.db"))

app = FastAPI(
    title="NamoNexus Enterprise API",
    version="3.5.1",
    description="Mental Health Infrastructure AI - Production Hardened",
)
cors_origins = load_cors_origins()
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials="*" not in cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
add_https_redirect(app)


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
        self.grid.store_sovereign(
            {
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
            }
        )

        if human_required:
            self.grid.create_crisis_alert(
                {
                    "user_id": request.user_id,
                    "session_id": session_id,
                    "risk_level": ethics["risk_level"],
                }
            )
            print(
                f"▲ CRISIS ALERT: User {request.user_id} requires immediate human intervention"
            )

    @staticmethod
    def _generate_session_id() -> str:
        return f"session_{uuid.uuid4().hex[:12]}"


engine = NamoNexusEnterprise(DB_PATH)
rate_limit_capacity, rate_limit_refill = load_rate_limit_settings()
rate_limit_store = build_rate_limiter_store()
rate_limiter = TokenBucketRateLimiter(
    capacity=rate_limit_capacity,
    refill_rate=rate_limit_refill,
    store=rate_limit_store,
)
rate_limit_per_minute = int(round(rate_limit_refill * 60))


@app.post("/triage", response_model=TriageResponse, dependencies=[Depends(verify_token)])
async def triage_endpoint(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
):
    cleaned_message = sanitize_text(request.message)
    voice_features = request.voice_features
    if hasattr(voice_features, "model_dump"):
        voice_features = voice_features.model_dump()
    facial_features = request.facial_features
    if hasattr(facial_features, "model_dump"):
        facial_features = facial_features.model_dump()
    sanitized_request = request.model_copy(
        update={
            "message": cleaned_message,
            "voice_features": voice_features,
            "facial_features": facial_features,
        }
    )
    return await engine.process_triage(sanitized_request, background_tasks)


@app.post("/interact", response_model=TriageResponse, dependencies=[Depends(verify_token)])
async def interact_alias(
    request: InteractRequest,
    background_tasks: BackgroundTasks,
):
    triage_request = TriageRequest(user_id=request.user_id, message=request.message)
    return await triage_endpoint(triage_request, background_tasks)


@app.post("/reflect", response_model=TriageResponse, dependencies=[Depends(verify_token)])
async def reflect_alias(
    request: ReflectRequest,
    background_tasks: BackgroundTasks,
):
    triage_request = TriageRequest(
        user_id=request.user_id,
        message=request.message,
        session_id=request.session_id,
    )
    return await triage_endpoint(triage_request, background_tasks)


# Audio triage configuration
ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/mpeg"}
MAX_AUDIO_SIZE = 5 * 1024 * 1024  # 5MB


@app.post("/triage/audio", response_model=TriageResponse, dependencies=[Depends(verify_token)])
async def triage_audio_endpoint(
    background_tasks: BackgroundTasks,
    audio: UploadFile | None = File(None, description="Audio file (WAV, MP3)"),
    audio_file: UploadFile | None = File(None, description="Audio file (WAV, MP3)"),
    user_id: str = Form(..., min_length=1, max_length=255, description="User identifier"),
    session_id: str | None = Form(
        None, max_length=255, description="Optional session ID"
    ),
    message: str | None = Form(
        None,
        max_length=5_000,
        description="Optional text message (will transcribe if empty)",
    ),
):
    """Triage endpoint that accepts audio file for voice analysis.
    
    This endpoint extracts voice features (pitch, energy, speech rate, etc.)
    from the uploaded audio and optionally transcribes speech to text using Whisper.
    
    Supported formats: WAV, MP3
    Max file size: 5MB
    """
    selected_audio = audio_file or audio
    if selected_audio is None:
        raise HTTPException(status_code=422, detail="Audio file is required")
    # Validate content type
    if not selected_audio.content_type or selected_audio.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=422, detail="Only .wav / .mp3 allowed")
    
    # Read and validate size
    audio_bytes = await selected_audio.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    if len(audio_bytes) < 1000:
        raise HTTPException(status_code=422, detail="Audio file too small or empty")
    
    # Extract voice features (run in thread pool to not block)
    try:
        from voice_extractor import voice_extractor
    except ModuleNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Voice analysis dependencies not installed",
        ) from exc
    try:
        voice_result: VoiceAnalysisResult = await asyncio.to_thread(
            voice_extractor.extract_from_bytes,
            audio_bytes,
            transcribe=True,
        )
        logger.info(
            "voice_extraction_complete duration=%.1f transcription_len=%d",
            voice_result.duration_seconds,
            len(voice_result.transcription or ""),
        )
    except Exception as e:
        logger.exception("voice_extraction_failed")
        raise HTTPException(status_code=400, detail=f"Failed to process audio: {str(e)}")
    
    # Determine message: user-provided > transcription > fallback
    final_message = message
    if not final_message and voice_result.transcription:
        final_message = voice_result.transcription
    if not final_message:
        final_message = "[Audio triage - no text available]"
    if len(final_message) > 5_000:
        raise HTTPException(status_code=422, detail="Message too long")
    
    cleaned_message = sanitize_text(final_message)
    
    # Build triage request with extracted voice features
    request = TriageRequest(
        message=cleaned_message,
        user_id=user_id,
        session_id=session_id,
        voice_features=voice_result.to_voice_features_dict(),
        facial_features=None,
    )
    
    # Process triage
    response = await engine.process_triage(request, background_tasks)
    
    # Add transcription to response if available
    if voice_result.transcription:
        response_dict = response.model_dump()
        response_dict["transcription"] = voice_result.transcription
        return TriageResponse(**response_dict)
    
    return response


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
        limit_headers = {
            "X-RateLimit-Limit": str(rate_limit_per_minute),
            "X-RateLimit-Burst": str(rate_limiter.capacity),
            "X-RateLimit-Remaining": str(max(0, int(result.remaining))),
        }
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={
                "Retry-After": str(max(1, math.ceil(result.retry_after))),
                **limit_headers,
            },
        )
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limit_per_minute)
    response.headers["X-RateLimit-Burst"] = str(rate_limiter.capacity)
    response.headers["X-RateLimit-Remaining"] = str(max(0, int(result.remaining)))
    return response


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


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in {"/health", "/ready", "/metrics"}:
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
            headers={"Retry-After": str(int(result.retry_after))},
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
        logger.exception("request_failed method=%s path=%s", request.method, request.url.path)
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
        await asyncio.to_thread(engine.grid.db_pool.ping)
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


@app.get("/harmonic-console", dependencies=[Depends(verify_token)])
async def get_harmonic_console_global():
    metrics = await engine.grid.get_global_metrics_async()
    sessions = await engine.grid.get_recent_sessions_async()
    alerts = await engine.grid.get_all_alerts_async()

    return {
        "metrics": metrics,
        "recent_sessions": sessions,
        "active_alerts": alerts,
    }


@app.get("/harmonic-console/{session_id}", dependencies=[Depends(verify_token)])
async def get_harmonic_console_session(session_id: str):
    history = await engine.grid.get_session_history_async(session_id)
    alerts = await engine.grid.get_alerts_async(session_id)

    return {
        "session_id": session_id,
        "conversation_history": history,
        "crisis_alerts": alerts,
        "empathy_guidance": alerts[0].get("prompts", []) if alerts else [],
    }
