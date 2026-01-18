#!/bin/bash

# NamoNexus 360-Degree Testing Suite (Corrected)

set -e

echo "🧪 Starting NamoNexus 360-Degree Testing Suite"
echo "================================================"

# Install dependencies required for the actual app + testing
pip install pytest pytest-asyncio pytest-cov httpx fastapi requests

# Set PYTHONPATH to root directory so tests can find core_engine.py, main.py, etc.
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../.."

echo "1️⃣ Unit Tests (Core Engine)..."
pytest ../01-unit-tests/test_core_logic.py -v

echo "2️⃣ Integration Tests (Grid Intelligence)..."
pytest ../02-integration-tests/test_grid_intelligence.py -v

echo "3️⃣ API Tests (FastAPI)..."
pytest ../03-api-tests/test_api_fast.py -v