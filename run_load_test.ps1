# PowerShell script to run Load Tests automatically
# Windows equivalent of run_load_test.sh

Write-Host "Starting API Server for Load Testing..." -ForegroundColor Green

# Start uvicorn in background
$APIProcess = Start-Process uvicorn -ArgumentList "main:app --host 0.0.0.0 --port 8000 --log-level warning" -PassThru -WindowStyle Hidden

# Wait for API to be ready
Write-Host "Waiting for API to initialize (10s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if API is responding
try {
    $HealthCheck = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($HealthCheck.StatusCode -eq 200) {
        Write-Host "API is responding correctly" -ForegroundColor Green
    }
} catch {
    Write-Host "API health check warning: $_" -ForegroundColor Yellow
}

Write-Host "Running Locust Load Test (Users: 50, Rate: 5/s, Duration: 30s)..." -ForegroundColor Cyan

# Run Locust using the local locustfile.py
$LocustProcess = Start-Process locust -ArgumentList @(
    "-f", "locustfile.py",
    "--headless",
    "-u", "50", "-r", "5",
    "--run-time", "30s",
    "--host", "http://localhost:8000",
    "--csv=load_test_results"
) -PassThru -Wait -NoNewWindow

Write-Host "Stopping API Server..." -ForegroundColor Red

# Stop the API server
if ($APIProcess) {
    try {
        Stop-Process -Id $APIProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "API Server stopped" -ForegroundColor Green
    } catch {
        Write-Host "Could not stop API server cleanly: $_" -ForegroundColor Yellow
    }
}

# Check if results file was created
if (Test-Path "load_test_results_stats.csv") {
    Write-Host "Load Test Completed. Results saved to load_test_results_stats.csv" -ForegroundColor Green
    Write-Host ""
    Write-Host "Summary Results:" -ForegroundColor Cyan
    try {
        $Results = Import-Csv "load_test_results_stats.csv"
        if ($Results) {
            $LastResult = $Results[-1]
            Write-Host "Total Requests: $($LastResult.'Total Request Count')" -ForegroundColor White
            Write-Host "Failed Requests: $($LastResult.'Total Failure Count')" -ForegroundColor White
            Write-Host "Average Response Time: $($LastResult.'Average Response Time') ms" -ForegroundColor White
            Write-Host "Requests/Sec: $($LastResult.'Requests/s')" -ForegroundColor White
        }
    } catch {
        Write-Host "Could not parse results file, but test completed." -ForegroundColor Yellow
    }
} else {
    Write-Host "Results file not found, but test may have completed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Load Test Process Finished!" -ForegroundColor Green

# Clean up any remaining uvicorn processes
taskkill /F /IM uvicorn.exe >nul 2>&1
