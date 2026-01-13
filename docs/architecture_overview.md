# NamoNexus Enterprise v3.5.1 Architecture Overview

NamoNexus Enterprise ships with two API stacks:

- **Lightweight API (`src/`)**: Production-ready FastAPI service (`main.py` → `src/main.py`) focused on fast latency and measurable metrics.
- **Advanced stack (`research/`)**: Research/feature-rich pipeline with memory, reflection, and safety modules (not wired to the production entrypoint by default).

Core layers:
- **src/**: Runtime API, safety scoring, emotion analysis, alignment, and in-memory history.
- **research/**: Persona core, memory system, safety (DivineShield), and supervisor chain experiments.
- **frontend/**: Harmonic Alignment Console web interface (static).

Key flows (lightweight API):
- `src/main.py` receives user input and calls `emotion_service`, `safety_service`, `dharma_service`, and `personalization_engine`.
- Responses include `risk_score`, `ethical_score`, and `decision_consistency` for audit/metrics.
- `src/metrics_store.py` tracks latency summaries for `/readyz` and `/metrics`.

Deployment aids live in `deploy/` and documentation in `docs/`. The manifest `Namo_FormGenesis_v3.5.1_RELEASE_MANIFEST.md` captures project identity.

## Adaptive Supervisor Chain (Four Noble Truths)

The Adaptive Supervisor Chain is a multi-stage filter for resolving conflicting signals (emotion vs. ethics, short-term urge vs. long-term impact) using a four-step loop inspired by the Four Noble Truths:

- Dukkha (ทุกข์): Identify the core problem and primary emotion with intensity.
- Samudaya (สมุทัย): Analyze the cause and detect conflicting drivers.
- Nirodha (นิโรธ): Propose resolution paths (pause, safe alternatives, escalation if safety risk).
- Magga (มัคคะ): Choose the most ethical and sustainable path for the user.

Example 1:
- User: "ผมท้อแท้แล้ว อยากเลิกทั้งหมด"
- Detected: sadness, high intensity; conflict between immediate urge and long-term impact.
- Recommendation: pause, regulate, and choose a low-risk first step.

Example 2:
- User: "ผมกังวลเกี่ยวกับการนำเสนอพรุ่งนี้"
- Detected: anxiety, moderate intensity; low conflict.
- Recommendation: focus on preparation and a practical next action.
