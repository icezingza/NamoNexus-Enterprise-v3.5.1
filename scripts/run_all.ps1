Write-Host "Sprint 1 Complete Setup"

# 1. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 2. Create test structure
New-Item -ItemType Directory -Force -Path tests/unit, tests/integration, tests/performance, tests/fixtures, reports | Out-Null

# 3. Run tests
pytest tests/ -v --cov=app --cov=src --cov-report=html

# 4. Security scan
$env:PYTHONIOENCODING = "utf-8"
pip-audit --desc --format json > reports/pip_audit_report.json
pip-audit

bandit -r app/ src/ -f json -o reports/bandit_report.json
bandit -r app/ src/

if (Get-Command rg -ErrorAction SilentlyContinue) {
    $secretMatches = rg -n "password|api_key|secret|token" app src
} else {
    $secretMatches = Get-ChildItem -Path app, src -Recurse -File | Select-String -Pattern "password|api_key|secret|token"
}

if ($secretMatches) {
    $secretMatches
} else {
    Write-Host "No hardcoded secrets found"
}

pip-licenses > reports/licenses.txt

# 5. Generate reports
pytest tests/ --cov=app --cov=src --cov-report=html --cov-report=term --cov-report=json:reports/coverage.json
pytest tests/ --html=reports/test_report.html --self-contained-html
bandit -r app/ src/ -f html -o reports/security_report.html

# 6. Show summary
Write-Host ""
Write-Host "Sprint 1 Summary:"
$testCountLine = pytest tests/ --collect-only -q | Select-Object -Last 1
Write-Host ("  OK {0} test cases" -f $testCountLine)

$coverage = "unknown"
if (Test-Path reports/coverage.json) {
    try {
        $coverage = (python -c "import json; print(json.load(open('reports/coverage.json'))['totals']['percent_covered'])").Trim()
    } catch {
        $coverage = "unknown"
    }
}
Write-Host ("  OK Coverage: {0}%" -f $coverage)

$reportCount = 0
if (Test-Path reports) {
    $reportCount = (Get-ChildItem reports -File | Measure-Object).Count
}
Write-Host ("  OK Reports: {0} files" -f $reportCount)
