# Security Cleanup v3.5.1

## Summary
Production code (src/) is isolated from research modules. Research code is in research/ and not part of the v3.5.1 deployment.

## Known research-only risks
- random.uniform() usage in research modules (B311 Bandit) remains in research/.
- Research docstrings may expose internal concepts; production code avoids these.

## Production posture
- TLS in transit (deployment-configured)
- SQLAlchemy ORM with migrations
- Pydantic input validation
- Rate limiting on /interact and /reflect
- Structured logging (no PII in previews)

## Dependency cleanup
Removed experimental libraries from production requirements:
- transformers
- torch
- sentence-transformers
- chromadb
- numpy

