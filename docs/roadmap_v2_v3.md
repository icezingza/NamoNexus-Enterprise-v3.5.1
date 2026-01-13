# Roadmap v2.0 - v3.0 (Engineering)

This roadmap captures the next phases requested for stability, observability, and advanced capabilities.

## Phase 1: v2.0 (Stability & Scale)
Priority 1 (Must have):
- Comprehensive test suite (target 80% coverage).
- Monitoring + observability (metrics + tracing).
- Performance optimization (cold start < 5s).
- Safety system upgrade (ML-based classifier + fallback rules).

Priority 2 (Should have):
- Multilingual support (Thai, Chinese, Vietnamese).
- Memory system hardening (eviction + caching).
- Frontend modernization.
- Kubernetes deployment templates.

Priority 3 (Nice to have):
- Redis integration for caching.
- API auth + rate limiting.
- Conversation analytics dashboard.

## Phase 2: v2.5 (Intelligence)
- Fine-tuned emotion models per language.
- Advanced conversation flow management.
- User preference learning.
- Platform integrations (Slack, Teams, etc.).

## Phase 3: v3.0 (Advanced Features)
- Real-time voice interaction.
- Multi-turn conversation context management.
- Personalized dharma guidance.
- Mobile native apps (iOS/Android).
- Meditation/mindfulness app integrations.

## v2.0 Quick Start Checklist
1) Create a test suite structure:
   - `tests/unit/`
   - `tests/integration/`
   - `tests/performance/`
2) Add coverage tooling:
   - `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`
3) Add observability:
   - Prometheus metrics + OpenTelemetry tracing
4) Performance optimization:
   - JSON fast path (`orjson`/`ujson`), warm-up paths, and caching
5) Run coverage:
   - `pytest tests/ --cov=app --cov-report=html`
