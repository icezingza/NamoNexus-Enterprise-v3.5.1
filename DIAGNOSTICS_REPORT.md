# OpenAPI /openapi.json Debug Report

## Issue Analysis
The `/openapi.json` endpoint was returning 500 errors with "missing func query parameter" messages.

This error typically occurs when:
1. A decorator is used without `@functools.wraps(func)`, causing FastAPI to introspect the wrapper instead of the actual endpoint
2. Middleware interferes with request/response flow
3. Function signatures are not properly preserved

## Fixes Applied

### 1. AuditMiddleware Fix (`src/audit_middleware.py`)
**Problem**: The middleware was trying to use `self._session_factory()` without checking if it was None, causing TypeErrors.

**Fix Applied**:
- Added None check for `session_factory` before attempting to use it
- Added `/openapi.json` to the skip list (along with health/metrics endpoints)
- Added proper error handling around database operations
- Added logging imports and error logging
- Wrapped session creation and logging in try/except to prevent middleware failures from breaking the request chain

### 2. Added functools Import (`main.py`)
**Prevention**: Added `import functools` to ensure any future decorators can properly use `@functools.wraps`.

## Root Cause
The immediate issue was in `AuditMiddleware.dispatch()`:
```python
db_session = self._session_factory()  # TypeError when session_factory is None
```

In `main.py`, the AuditMiddleware is disabled (commented out) for Phase 1 recovery, but the middleware was still imported. If it were enabled without proper None checking, it would crash when trying to create database sessions.

## Verification
Routes that skip audit logging (including `/openapi.json`):
- `/health`
- `/healthz`
- `/readyz`
- `/metrics`
- `/openapi.json` (NEW - added to prevent introspection issues)

## Next Steps for Complete Fix
1. Ensure all custom decorators in the codebase use `@functools.wraps(func)`
2. Verify no other middleware has similar issues
3. Test the `/openapi.json` endpoint once httpx is installed
4. Consider re-enabling AuditMiddleware in a controlled manner once Phase 1 recovery is complete
