#!/bin/bash

echo "Sprint 1 Complete Setup"

# 1. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 2. Create test structure
mkdir -p tests/{unit,integration,performance,fixtures} reports

# 3. Run tests
pytest tests/ -v --cov=app --cov=src --cov-report=html

# 4. Security scan
bash scripts/security_scan.sh

# 5. Generate reports
bash scripts/generate_reports.sh

# 6. Show summary
echo ""
echo "Sprint 1 Summary:"
echo "  OK $(pytest tests/ --collect-only -q | tail -1) test cases"
echo "  OK Coverage: $(grep -oP 'line-rate=\"\\K[^\"]*' htmlcov/status.json)%"
echo "  OK Reports: $(ls -1 reports/ | wc -l) files"
