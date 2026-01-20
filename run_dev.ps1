Write-Host "🚀 Starting NamoNexus Enterprise (Local Dev Mode)..."
$env:NAMO_NEXUS_TOKEN = "dev-token-123"
$env:PYTHONPATH = "."

uvicorn api.main:app --reload --host 127.0.0.1 --port 8000