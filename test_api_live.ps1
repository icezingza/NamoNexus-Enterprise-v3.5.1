Write-Host "========== NAMONEXUS LIVE API TEST =========="

Write-Host "`n[0/5] Cleaning up port 8000..."
$running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match "src[\\/]+main\.py" }
if ($running) {
    foreach ($proc in $running) {
        Write-Host "Stopping existing process PID: $($proc.ProcessId)"
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}

Write-Host "`n[1/5] Starting server..."
$serverProcess = Start-Process -FilePath python `
  -ArgumentList "src/main.py" `
  -PassThru `
  -WindowStyle Hidden `
  -RedirectStandardOutput "server.log" `
  -RedirectStandardError "server.err"

if (-not $serverProcess) {
    Write-Host "Failed to start server process."
    exit 1
}

$serverId = $serverProcess.Id
Write-Host "Server PID: $serverId"
Start-Sleep -Seconds 3

Write-Host "`n[2/5] Testing GET /health..."
try {
    $json = Invoke-RestMethod -Uri http://localhost:8000/health -Method Get
    Write-Host "Status: $($json.status)"
    Write-Host "Version: $($json.version)"
} catch {
    Write-Host "Health check failed: $_"
}

Write-Host "`n[3/5] Testing GET /healthz..."
try {
    $json = Invoke-RestMethod -Uri http://localhost:8000/healthz -Method Get
    Write-Host "Status: $($json.status)"
} catch {
    Write-Host "Healthz check failed: $_"
}

Write-Host "`n[4/5] Testing POST /reflect..."
try {
    $body = @{
        text = "I'm feeling great today!"
        user_id = "test_user_001"
    } | ConvertTo-Json -Compress

    $json = Invoke-RestMethod -Uri http://localhost:8000/reflect -Method Post -ContentType "application/json" -Body $body
    Write-Host "Tone: $($json.tone)"
    Write-Host "Risk Level: $($json.risk_level)"
    Write-Host "Coherence: $($json.coherence)"
    if ($null -ne $json.response -and $json.response.Length -gt 0) {
        $preview = $json.response.Substring(0, [Math]::Min(50, $json.response.Length))
        Write-Host "Response Preview: $preview..."
    } else {
        Write-Host "Response Preview: (none)"
    }
} catch {
    Write-Host "Reflect request failed: $_"
}

Write-Host "`n[5/5] Testing POST /interact..."
try {
    $body = @{
        user_id = "test_user_002"
        message = "I have an important presentation tomorrow and I'm nervous about it"
    } | ConvertTo-Json -Compress

    $json = Invoke-RestMethod -Uri http://localhost:8000/interact -Method Post -ContentType "application/json" -Body $body
    Write-Host "Tone: $($json.tone)"
    Write-Host "Risk Level: $($json.risk_level)"
    Write-Host "Risk Score: $($json.risk_score)"
    Write-Host "Moral Index: $($json.moral_index)"
    Write-Host "Ethical Score: $($json.ethical_score)"
    Write-Host "Recommendations: $($json.recommendations -join ', ')"
} catch {
    Write-Host "Interact request failed: $_"
}

Write-Host "`n========== CLEANUP =========="
Write-Host "Stopping server PID: $serverId"
Stop-Process -Id $serverId -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Write-Host "Server stopped"

Write-Host "`n========== TEST COMPLETE =========="
