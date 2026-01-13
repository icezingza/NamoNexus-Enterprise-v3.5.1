# Release Notes v1.0.0

Release Date: January 2, 2026
Git Tag: v1.0.0
Status: Production Ready

## Summary
NamoNexus v1.0.0 delivers a modular architecture, persistent storage,
comprehensive tests, and production-ready containerization with zero breaking
changes.

## Highlights
- Modular src/ layout (models, services, database, api, utils).
- SQLAlchemy ORM with Alembic migrations.
- Refactored emotion, safety, and memory services with logging and exceptions.
- Test suite: 20 unit/integration tests plus a live API verification script.
- Containerization with Dockerfile and docker-compose.
- Health, readiness, and metrics endpoints for operations.

## Getting Started
Local development:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python src/main.py
```

Docker:
```bash
docker build -t namonexus:1.0.0 .
docker run -p 8000:8080 -e PORT=8080 namonexus:1.0.0
```

Docker Compose:
```bash
cp .env.example .env
docker compose up --build
```

## API Endpoints
- GET /health - Health and version
- GET /healthz - Liveness probe
- GET /readyz - Readiness probe
- GET /metrics - Prometheus metrics or JSON summary
- GET /api/status - Service status
- POST /interact - Main interaction (rate limited)
- POST /reflect - Alias for /interact

Example request:
```bash
curl -X POST http://localhost:8000/interact \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_123","message":"I feel anxious about tomorrow"}'
```

## Migration Guide
Breaking changes: none.

Upgrade steps:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
alembic upgrade head
pytest src/tests/ -v
python src/main.py
```

## Key Dependencies
- fastapi 0.109.1
- uvicorn 0.27.0
- sqlalchemy 2.0.25
- pydantic 2.5.0
- alembic 1.13.1
- prometheus-client 0.20.0
- slowapi 0.1.9

## Known Issues
None reported in v1.0.0.

## Next Steps
- Redis caching layer
- Extended metrics dashboards
- WebSocket support
- Multi-language responses
