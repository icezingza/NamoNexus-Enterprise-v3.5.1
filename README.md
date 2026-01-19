# NamoNexus Enterprise v3.5.1 (Sovereign Edition) 💫

> **"The First AI with a Soul."** - Engineered with Golden Ratio Logic & Dhammic Reasoning.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Supreme-009688?style=for-the-badge&logo=fastapi)
![Architecture](https://img.shields.io/badge/Architecture-Sovereign-red?style=for-the-badge)

## 🧠 Core Philosophy

NamoNexus is not just a chatbot. It is a **Sovereign AI Infrastructure** designed to operate independently (On-Premise) with a unique "Identity Capsule" architecture. It prioritizes **Non-Verbal Cues (Voice/Face)** over text using the **Golden Ratio ($\phi \approx 1.618$)**, allowing it to detect hidden emotions and deception.

## ✨ Key Features (Selling Points)

### 1. 🧬 Identity Capsule v1.1

- **Dynamic Personality:** The AI's personality is not hardcoded but loaded from JSON capsules.
- **Evolutionary Memory:** Capable of "Reflecting" on past sessions to evolve its state using `ConsciousEvolutionLattice`.

### 2. 🔮 Sixth Sense Engine (Multimodal Fusion)

- **Golden Ratio Logic:** Weights Non-Verbal signals ($61.8\%$) higher than Text ($38.2\%$).
- **Deception Detection:** Instantly flags "White Lies" (e.g., saying "I'm okay" with a distressed voice).

### 3. 🛡️ Sovereign Security (Dhammic Moat)

- **Token-Based Auth:** Enterprise-grade Bearer Token security.
- **Local Execution:** Runs 100% offline/local. No data leakage to external clouds.
- **Privacy First:** Built-in PII redaction and encrypted storage (SQLCipher).

## 🚀 Quick Start (Installation)

**Prerequisites:**

- Python 3.10+
- FFmpeg (for Audio Triage)

**1. Clone & Install**

```bash
git clone https://github.com/icezingza/NamoNexus_v1.0.git
cd NamoNexus
pip install -r requirements.txt
```

## 🛠️ Tech Stack

- **Core:** Python 3.11, FastAPI

- **Database:** SQLite (WAL Mode) with Thread-safe Connection Pool
- **Deployment:** Docker, Docker Compose (Optimized for Production)
- **Performance:** Async/Await Concurrency + Background Tasks

## 📦 Quick Start

```bash
# 1. Clone & Enter
git clone https://github.com/icezingza/NamoNexus-Enterprise-v3.5.1.git
cd NamoNexus-Enterprise-v3.5.1

# 2. Deploy with Docker (One-click)
docker-compose up -d --build

# 3. Verify System Health
curl http://localhost:8000/health
```

# NamoNexus Enterprise v3.5.1

NamoNexus Enterprise is a FastAPI service for emotion-aware conversations with safety checks,
alignment guidance, and persistent memory. It exposes a lightweight API for
production use and keeps advanced research modules under the `research/` directory.

## Features

- Emotion analysis and tone detection
- Safety screening with escalation handling
- Personalized responses with alignment insights
- SQLAlchemy persistence and Alembic migrations
- Metrics, health, and readiness endpoints
- Rate limiting on `/triage` (and aliases `/interact`, `/reflect`)

## v3.5.1 scope (production)

Included:

- EmotionService (keyword-based Thai/English)
- SafetyService (crisis detection + escalation)
- DharmaService (alignment analysis)
- PersonalizationEngine (response templates)
- MemoryService (SQLAlchemy ORM)
- Health/readiness probes and metrics

Research-only (v2.0+):

- IntegrityKernel and supervisor chain
- Temporal reasoning and simulation modules
- Experimental emotion models

## Quick start

Requirements: Python 3.11+

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:

   ```bash
   alembic upgrade head
   ```

4. Start the API:

   ```bash
   python main.py
   ```

The API listens on `http://localhost:8000` by default.

For a lightweight dev stack without auth/Celery, use `python src/main.py`.

Optional frontend: open `frontend/index.html` for the Harmonic Alignment Console.

## Configuration

Copy `.env.example` to `.env` and adjust values as needed.

Core settings:

- `API_HOST`, `API_PORT`
- `DEBUG`, `LOG_LEVEL`
- `DATABASE_URL`
- `AUTO_CREATE_DB`
- `MAX_MEMORY_ITEMS`, `MEMORY_RETENTION_DAYS`

Enterprise API settings (main.py):

- `NAMO_NEXUS_TOKEN` (required; generated at startup if missing)
- `DB_PATH`
- `CORS_ALLOW_ORIGINS`
- `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_BURST`

Advanced stack settings live under `NAMO_*` variables (see `.env.example`).

Set `AUTO_CREATE_DB=true` only for local dev convenience; production should use Alembic migrations.

## API endpoints (primary: `main.py`)

- `GET /health` - Health and version
- `GET /healthz` - Liveness probe (alias)
- `GET /ready` - Readiness probe
- `GET /readyz` - Readiness alias
- `GET /metrics` - Prometheus metrics
- `POST /triage` - Primary triage endpoint (requires `Authorization: Bearer <token>`)
- `POST /interact` - Alias for `/triage` (requires auth)
- `POST /reflect` - Alias for `/triage` (requires auth)
- `GET /harmonic-console` - Global metrics (requires auth)
- `GET /harmonic-console/{session_id}` - Session view (requires auth)

Lightweight dev stack (`src/main.py`) exposes `/interact`, `/reflect`, `/healthz`, `/readyz`, and `/api/status` without auth.

Example request:

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $NAMO_NEXUS_TOKEN" \
  -d '{"user_id":"user_123","message":"I feel anxious about tomorrow"}'
```

Example response:

```json
{
  "response": "...",
  "risk_level": "moderate",
  "dharma_score": 0.72,
  "emotional_tone": "supportive",
  "multimodal_confidence": 0.75,
  "latency_ms": 12.3,
  "session_id": "session_a1b2c3d4e5f6",
  "human_handoff_required": false,
  "empathy_prompts": null
}
```

The request body accepts `message` and `user_id` with optional `session_id`, `voice_features`, and `facial_features`.

## Database and migrations

```bash
alembic revision --autogenerate -m "Describe change"
alembic upgrade head
alembic current
alembic history
```

Default (SQLite): `sqlite:///./namonexus.db`

For PostgreSQL, set `DATABASE_URL` to:

```
postgresql://namonexus:password@db:5432/namonexus
```

## Testing

```bash
pytest src/tests/ -v
pytest src/tests/ --cov=src --cov-report=html
```

Live API check (Windows):

```powershell
powershell -ExecutionPolicy Bypass -File test_api_live.ps1
```

Diagnostics:

- Windows: `diagnostic.ps1`
- Linux/Mac: `diagnostic.sh`

## Docker

Build:

```bash
docker build -t namonexus:3.5.1 .
```

Run:

```bash
docker run -p 8000:8080 -e PORT=8080 namonexus:3.5.1
```

## Docker Compose

```bash
docker compose up --build
```

To use PostgreSQL, update `DATABASE_URL` in `.env` and run:

```bash
docker compose --profile postgres up --build
```

## Project structure

```
namonexus/
├── src/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── main.py
├── research/
│   └── README.md
├── app/
│   └── README.md
├── migrations/
├── frontend/
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── README.md
```

Production services live under `src/services/`. Legacy modules under `src/*_service.py`
remain for backward compatibility and are not wired to the API.

## Troubleshooting

Port already in use:

```bash
# Linux/Mac
lsof -i :8000
# Windows
netstat -ano | findstr :8000
```

Reset local SQLite database:

```bash
rm namonexus.db
alembic upgrade head
```

Run a single test:

```bash
pytest src/tests/test_api.py::test_health_endpoint -v
```

## License

Licensed under the NamoNexus Commercial License. See LICENSE-COMMERCIAL.
