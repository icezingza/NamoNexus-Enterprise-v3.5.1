# API Reference (Lightweight API)

## Base URL
- FastAPI service root: `/`

## Endpoints
- `GET /health` – Health payload with version.
- `GET /healthz` – Liveness probe.
- `GET /readyz` – Readiness probe with latency metrics.
- `GET /metrics` – Runtime latency metrics.
- `POST /interact` – Body: `{ "message": "...", "user_id": "..." }` (or `{ "text": "..." }`).
- `POST /reflect` – Alias for `/interact` (rate limited).

## Response Structure
`/interact` and `/reflect` respond with:
- `user_id` – Caller identifier.
- `response` – Primary response string.
- `reflection_text` – Response used by downstream UI.
- `tone` – Derived emotional tone.
- `risk_level` / `risk_score` – Safety assessment.
- `coherence` – Alignment confidence.
- `moral_index` – Derived moral index.
- `ethical_score` – Ethical alignment score.
- `decision_consistency` – Consistency score.
- `recommendations` – Suggested follow-up actions.
