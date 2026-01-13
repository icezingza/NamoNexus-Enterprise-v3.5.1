#!/bin/bash

echo "Generating Quality Reports..."

mkdir -p reports

# Test coverage
pytest tests/ --cov=app --cov=src --cov-report=html --cov-report=term

# Generate coverage badge
echo "Coverage: $(grep -oP 'line-rate=\"\\K[^\"]*' htmlcov/status.json | head -1)%"

# Generate test report
pytest tests/ --html=reports/test_report.html --self-contained-html

# Generate security report
bandit -r app/ src/ -f html -o reports/security_report.html

echo "Reports generated in reports/ directory"
ls -lh reports/
