#!/bin/bash
# diagnostic.sh - Complete API startup check (ASCII-safe)

echo "========== DIAGNOSTIC REPORT =========="
echo ""

echo "1) Check Python & Dependencies"
python --version
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
echo ""

echo "2) Check Port Status"
lsof -i :8000 2>/dev/null || echo "Port 8000: FREE"
echo ""

echo "3) Check Database"
test -f namonexus.db && echo "Database file exists" || echo "Database file NOT found"
sqlite3 namonexus.db ".tables" 2>/dev/null || echo "Database tables: ERROR"
echo ""

echo "4) Check Alembic"
alembic current 2>/dev/null && echo "Alembic: OK" || echo "Alembic: ERROR"
echo ""

echo "5) Import Main Module (Test)"
python -c "from src.main import app; print('Import successful')" 2>&1 || echo "Import FAILED"
echo ""

echo "6) Start Server (5 sec timeout)"
timeout 5 python src/main.py 2>&1 || echo "Timeout or error occurred"
echo ""

echo "7) Check if port is listening (after startup)"
sleep 2
lsof -i :8000 | grep LISTEN && echo "Port 8000: LISTENING" || echo "Port 8000: NOT listening"
echo ""

echo "========== END DIAGNOSTIC =========="
