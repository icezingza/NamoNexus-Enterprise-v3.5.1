#!/bin/bash

echo "Running Security Scans..."

mkdir -p reports

# 1. Pip audit (vulnerabilities)
echo "Scanning dependencies with pip-audit..."
pip-audit --desc --format json > reports/pip_audit_report.json
pip-audit

# 2. Bandit (code security)
echo "Scanning code with bandit..."
bandit -r app/ src/ -f json -o reports/bandit_report.json
bandit -r app/ src/

# 3. Check for hardcoded secrets
echo "Checking for hardcoded secrets..."
grep -r "password\|api_key\|secret\|token" app/ src/ || echo "No hardcoded secrets found"

# 4. License check
echo "Checking dependencies licenses..."
pip-licenses > reports/licenses.txt

# 5. Generate report
echo ""
echo "Security Report:"
echo "================================================"
echo "Scan completed. Results:"
echo "  - pip_audit_report.json"
echo "  - bandit_report.json"
echo "  - licenses.txt"
echo "================================================"
