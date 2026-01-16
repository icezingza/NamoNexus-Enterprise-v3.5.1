# NamoNexus Enterprise v3.5.2-golden Release Notes

## Executive Summary
This release hardens the production footprint and introduces the Golden Ratio
harmonic layer for risk modeling and retry orchestration. Blockers resolved,
PDPA/GDPR compliant, Docker secure.

## Highlights
- Commercial licensing enforced for private distribution (MIT removed).
- Docker secrets hygiene via `.dockerignore` patterns.
- SQLCipher OS dependency added to Docker builds for encrypted storage.
- Audit logging minimized to user_id/risk/timestamp with 90-day retention policy.
- Duplicate rate-limit middleware removed; `/metrics` disabled in production.
- Golden Ratio functions added with unit tests (3/3 passing).
- Non-root container execution and SBOM generated (`SBOM.json`).

## Risk & Compliance
- PDPA/GDPR-aligned audit logging (no IP/User-Agent or raw payload storage).
- Retention policy targets 90 days with PostgreSQL/Mongo TTL support.

## Deployment Notes
- Docker port mapping updated to `8080:8080`.
- New runtime dependencies: `bleach`, `redis`, `prometheus-client`,
  `whisper-openai`, `librosa`.

## Golden Ratio Functions (New)
- `calculate_harmonic_risk(primary_risk, secondary_risk)`
- `fibonacci_retry(attempt, base_seconds=0.5, max_seconds=30.0)`

## Files Touched
- `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `requirements.txt`
- `src/audit_middleware.py`, `src/audit_log.py`, `main.py`, `core_engine.py`
- `utils.py`, `tests/test_golden.py`, `README.md`, `SBOM.json`
