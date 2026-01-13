import sys
import time
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from slowapi import _rate_limit_exceeded_handler

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.api import routes
from src.api.limiter import limiter
from src.config import config
from src.database.db import init_db
from src.metrics_store import LatencyMetricsStore
from src.utils.exceptions import (
    DatabaseError,
    InvalidInputError,
    NamoException,
    RateLimitExceeded,
    SafetyException,
    ServiceError,
    UserNotFoundError,
)
from src.utils.logger import log_error, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.AUTO_CREATE_DB:
        try:
            init_db()
            logger.info("Database initialized")
        except Exception:  # noqa: BLE001 - startup errors should be logged
            logger.error("Database initialization failed", exc_info=True)
            raise
    else:
        logger.info("Database auto-create disabled")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="NamoNexus Enterprise Lightweight API",
    description="Minimal service stack for deployment readiness",
    version="3.5.1",
    lifespan=lifespan,
)

app.include_router(routes.router)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

latency_metrics = LatencyMetricsStore()
REQUEST_COUNT = Counter("namonexus_requests_total", "Total requests")
REQUEST_LATENCY = Histogram("namonexus_latency_seconds", "Latency")


@app.middleware("http")
async def record_latency(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    latency_metrics.record(duration, response.status_code)
    REQUEST_COUNT.inc()
    REQUEST_LATENCY.observe(duration)
    response.headers["X-Request-Duration-Ms"] = f"{duration * 1000:.2f}"
    return response


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy", "version": app.version}


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "alive"}


@app.get("/api/status")
def api_status() -> Dict[str, str]:
    return {
        "system": "NamoNexus Enterprise",
        "status": "online",
        "message": "May wisdom guide you.",
    }


@app.get("/readyz")
def readyz() -> Dict[str, Any]:
    """Lightweight readiness with component/metric snapshots."""
    metrics_summary = latency_metrics.summary()
    return {
        "status": "ready",
        "components": {
            "collective": {"status": "ok"},
            "simulation": {"status": "ok"},
        },
        "metrics": {
            "latency": metrics_summary,
        },
    }


@app.get("/metrics", response_model=None)
def metrics(request: Request):
    """Runtime metrics for monitoring and reporting."""
    accept_header = request.headers.get("accept", "")
    if "text/plain" in accept_header or "application/openmetrics-text" in accept_header:
        return Response(generate_latest(), media_type="text/plain")
    return {
        "status": "ok",
        "latency": latency_metrics.summary(),
    }


@app.exception_handler(NamoException)
async def namo_exception_handler(request: Request, exc: NamoException) -> JSONResponse:
    if isinstance(exc, RateLimitExceeded):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, UserNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, (ServiceError, DatabaseError)):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, (InvalidInputError, SafetyException)):
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    log_error(
        error_type=type(exc).__name__,
        user_id=request.query_params.get("user_id", "unknown"),
        error_message=str(exc),
        traceback_str=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status_code,
        content={"error": type(exc).__name__, "detail": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Validation error: %s", exc)
    errors = exc.errors()
    for error in errors:
        ctx = error.get("ctx")
        if ctx and isinstance(ctx.get("error"), Exception):
            ctx["error"] = str(ctx["error"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"error": "ValidationError", "detail": errors}),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log_error(
        error_type="UnexpectedException",
        user_id=request.query_params.get("user_id", "unknown"),
        error_message=str(exc),
        traceback_str=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "detail": "An unexpected error occurred"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower(),
    )
