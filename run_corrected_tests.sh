#!/bin/bash

# NamoNexus 360-Degree Testing Suite (Corrected)

set -u

REPORT_DIR="test_reports"
TEST_ROOT="namonexus-360-testing"

# Create reports directory
mkdir -p "${REPORT_DIR}"

echo "Starting NamoNexus 360-Degree Testing Suite"
echo "==========================================="

# Install dependencies required for the actual app + testing
if [ -f requirements.txt ]; then
    python -m pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found; skipping base dependency install."
fi
python -m pip install pytest pytest-asyncio pytest-cov httpx fastapi requests psutil locust uvicorn

# Set PYTHONPATH to root directory so tests can find core_engine.py, main.py, etc.
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Function to run test and ignore failure (so we can generate report at the end)
run_test() {
    local label="$1"
    local path="$2"
    local report="$3"

    if [ ! -d "${path}" ]; then
        echo "SKIP: ${label} (missing ${path})"
        return
    fi

    echo "${label}"
    python -m pytest "${path}" -v --junitxml="${REPORT_DIR}/${report}" || echo "WARNING: ${label} failed, continuing..."
}

run_test "1 Unit Tests (Core Engine)" "${TEST_ROOT}/01-unit-tests" "01_unit.xml"
run_test "2 Integration Tests (Grid Intelligence)" "${TEST_ROOT}/02-integration-tests" "02_integration.xml"
run_test "3 API Tests (FastAPI)" "${TEST_ROOT}/03-api-tests" "03_api.xml"
run_test "4 Security Tests" "${TEST_ROOT}/04-security-tests" "04_security.xml"
run_test "5 Performance Tests" "${TEST_ROOT}/05-performance-tests" "05_performance.xml"
run_test "6 Failover Tests" "${TEST_ROOT}/07-failover-tests" "06_failover.xml"
run_test "7 Compliance Tests" "${TEST_ROOT}/08-compliance-tests" "07_compliance.xml"

echo "Load Test Check (Locust)..."
if command -v locust &> /dev/null; then
    echo "NOTE: Load tests require the API server to be running separately on port 8000."
    echo "Run manually: ./run_load_test.sh"
else
    echo "INFO: Locust not installed. Skipping load test check."
fi

echo "Generating Consolidated Report..."
python generate_summary_report.py
