# Release Notes v1.0.1

Release Date: 2026-01-07
Git Tag: v1.0.1
Status: Production Ready

## Summary
NamoNexus v1.0.1 is a maintenance release focused on documentation alignment,
licensing, and test hygiene. No API behavior changes.

## Highlights
- Align documented ports and defaults with the runtime configuration.
- Fix requirements compatibility so installs resolve cleanly.
- Add MIT license and reference it in the README.
- Filter noisy test warning output for cleaner CI logs.

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
docker build -t namonexus:1.0.1 .
docker run -p 8000:8080 -e PORT=8080 namonexus:1.0.1
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
- POST /reflect - Alias for /interact (rate limited)

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

## Known Issues
- Optional `app/` modules may run in simulation mode if ML dependencies are not installed.
