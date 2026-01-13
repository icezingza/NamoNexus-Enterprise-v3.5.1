# 🏛️ NamoNexus Enterprise v3.5.1 (Production Hardened)

> **"From Concept to Concrete: The Sovereign AI Infrastructure for Mental Health"**

## 💡 About The Project
NamoNexus Enterprise v3.5.1 คือร่างสมบูรณ์ (Reference Implementation) ของระบบปัญญาประดิษฐ์เพื่อโครงสร้างพื้นฐานด้านสาธารณสุขไทย ถูกพัฒนาต่อยอดจากแนวคิดเชิงปรัชญาใน v1.0 ให้กลายเป็น **"Production-Grade Engine"** ที่พร้อมรับมือกับ Traffic จริงในโรงพยาบาล

ระบบนี้ไม่ได้เป็นเพียง Chatbot แต่คือ **"หอบังคับการบินทางอารมณ์" (Emotional Air Traffic Control)** ที่ทำหน้าที่คัดกรอง (Triage) ผู้ป่วยวิกฤตด้วยความเมตตาเชิงรุก (Active Karuna) โดยรักษาข้อมูลทั้งหมดไว้ในประเทศไทย 100% (Sovereign Grid)

## 🚀 Key Features (ฟีเจอร์เด็ด)
* [cite_start]**🏥 Multi-Modal Triage:** วิเคราะห์ความเสี่ยงจาก 3 มิติ: ข้อความ (Text), น้ำเสียง (Voice Features), และสีหน้า (Facial Features) [cite: 81-125]
* [cite_start]**🛡️ Dhammic Moat (Ethical Kernel):** แกนกลางจริยธรรมที่ฝังลึกในระดับ Code (Hard-coded constraints) ไม่ใช่แค่ Prompt ตัดสินใจบนฐานของ "Right Speech", "Compassion", และ "Mindfulness" [cite: 81-125]
* [cite_start]**⚡ Non-Blocking Architecture:** แก้ปัญหาคอขวดด้วยการแยก Background Tasks ออกจาก Main Event Loop และใช้ Connection Pool สำหรับ SQLite (WAL Mode) รองรับ Concurrency สูง [cite: 142-150]
* [cite_start]**🇹🇭 Sovereign Grid Intelligence:** เก็บข้อมูลอ่อนไหวทั้งหมดลง Local Database (`namo_nexus_sovereign.db`) ภายในเซิร์ฟเวอร์องค์กร ไม่มีการส่งข้อมูลออกนอกประเทศ [cite: 112, 142]
* [cite_start]**🤝 Harmonic Console Bridge:** เตรียม API พร้อมส่งต่อเคสวิกฤตให้เจ้าหน้าที่มนุษย์ พร้อม "Empathy Prompts" แนะนำวิธีการพูดคุย [cite: 134-138, 177]

## 🛠️ Tech Stack
* **Core:** Python 3.11, FastAPI
* **Database:** SQLite (WAL Mode) with Thread-safe Connection Pool
* **Deployment:** Docker, Docker Compose (Optimized for Production)
* **Performance:** Async/Await Concurrency + Background Tasks

## 📦 Quick Start
```bash
# 1. Clone & Enter
git clone [https://github.com/your-org/namo-nexus-enterprise-v3.git](https://github.com/your-org/namo-nexus-enterprise-v3.git)
cd namo-nexus-enterprise-v3

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
- Rate limiting on `/interact` and `/reflect`

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
   python src/main.py
   ```

The API listens on `http://localhost:8000` by default.

Optional frontend: open `frontend/index.html` for the Harmonic Alignment Console.

## Configuration
Copy `.env.example` to `.env` and adjust values as needed.

Core settings:
- `API_HOST`, `API_PORT`
- `DEBUG`, `LOG_LEVEL`
- `DATABASE_URL`
- `AUTO_CREATE_DB`
- `MAX_MEMORY_ITEMS`, `MEMORY_RETENTION_DAYS`

Advanced stack settings live under `NAMO_*` variables (see `.env.example`).

Set `AUTO_CREATE_DB=true` only for local dev convenience; production should use Alembic migrations.

## API endpoints
- `GET /health` - Health and version
- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe with latency metrics
- `GET /metrics` - Prometheus metrics or JSON summary
- `GET /api/status` - Service status
- `POST /interact` - Main interaction endpoint (rate limited)
- `POST /reflect` - Alias for `/interact` (rate limited)

Example request:
```bash
curl -X POST http://localhost:8000/interact \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_123","message":"I feel anxious about tomorrow"}'
```

Example response:
```json
{
  "user_id": "user_123",
  "response": "...",
  "reflection_text": "...",
  "tone": "anxiety",
  "risk_level": "low",
  "risk_score": 0.25,
  "coherence": 0.85,
  "moral_index": 0.9,
  "ethical_score": 0.88,
  "decision_consistency": 0.82,
  "recommendations": ["..."]
}
```

The request body accepts `message` or `text`.

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
Licensed under the MIT License. See LICENSE.
