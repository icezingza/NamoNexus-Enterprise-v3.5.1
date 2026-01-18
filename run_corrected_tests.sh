#!/bin/bash

# NamoNexus 360-Degree Testing Suite (Corrected)

# Create reports directory
mkdir -p test_reports

echo "🧪 Starting NamoNexus 360-Degree Testing Suite"
echo "================================================"

# Install dependencies required for the actual app + testing
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx fastapi requests psutil locust uvicorn

# Set PYTHONPATH to root directory so tests can find core_engine.py, main.py, etc.
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Function to run test and ignore failure (so we can generate report at the end)
run_test() {
    echo "$1"
    pytest $2 -v --junitxml=test_reports/$3 || echo "⚠️  $1 failed, continuing..."
}

run_test "1️⃣ Unit Tests (Core Engine)..." "test_core_logic.py" "01_unit.xml"
run_test "2️⃣ Integration Tests (Grid Intelligence)..." "test_grid_intelligence.py" "02_integration.xml"
run_test "2️⃣.5️⃣ E2E Persistence Tests (API -> DB)..." "test_e2e_persistence.py" "02_e2e.xml"
run_test "3️⃣ API Tests (FastAPI)..." "test_api_fast.py" "03_api.xml"
run_test "4️⃣ Security Tests..." "test_security.py" "04_security.xml"
run_test "5️⃣ Performance Tests..." "test_performance.py" "05_performance.xml"
run_test "6️⃣ Failover Tests..." "test_failover.py" "06_failover.xml"
run_test "7️⃣ Compliance Tests..." "test_compliance.py" "07_compliance.xml"
run_test "🔥 Reliability Tests (Must-Have)..." "test_api_endpoints.py" "08_reliability.xml"
run_test "🛡️ Safety Moat Tests (Crisis Detection)..." "test_safety_service.py" "09_safety.xml"
run_test "⏱️ Overhead & Latency Analysis..." "test_overhead.py" "10_overhead.xml"

echo "8️⃣ Load Test Check (Locust)..."
if command -v locust &> /dev/null; then
    echo "⚠️  Note: Load tests require the API server to be running separately on port 8000."
    echo "   Run manually: ./run_load_test.sh"
else
    echo "ℹ️  Locust not installed. Skipping load test check."
fi

echo "📊 Generating Consolidated Report..."
# python3 generate_summary_report.py # (Optional: Use existing if available)
python3 generate_reliability_report.py
python3 generate_safety_report.py
python3 generate_executive_summary.py
