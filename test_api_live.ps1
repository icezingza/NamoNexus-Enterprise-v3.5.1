Write-Host "========== NAMONEXUS LIVE API TEST =========="

Write-Host "`n[0/5] Cleaning up port 8000..."
$baseUrl = $env:NAMO_NEXUS_BASE_URL
if (-not $baseUrl) {
    $baseUrl = "http://127.0.0.1:8000"
}
$running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match "main\.py" }
if ($running) {
    foreach ($proc in $running) {
        Write-Host "Stopping existing process PID: $($proc.ProcessId)"
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}

Write-Host "`n[1/5] Starting server..."
$serverProcess = Start-Process -FilePath python `
  -ArgumentList "main.py" `
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
    $json = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "Status: $($json.status)"
    Write-Host "Version: $($json.version)"
} catch {
    Write-Host "Health check failed: $_"
}

Write-Host "`n[3/5] Testing GET /healthz..."
try {
    $json = Invoke-RestMethod -Uri "$baseUrl/healthz" -Method Get
    Write-Host "Status: $($json.status)"
} catch {
    Write-Host "Healthz check failed: $_"
}

$token = $env:NAMO_NEXUS_TOKEN
if (-not $token) {
    Write-Host "NAMO_NEXUS_TOKEN is required for authenticated API tests."
    exit 1
}
$headers = @{ Authorization = "Bearer $token" }

Write-Host "`n[4/5] Testing POST /reflect..."
try {
    $body = @{
        message = "I'm feeling great today!"
        user_id = "test_user_001"
    } | ConvertTo-Json -Compress

    $json = Invoke-RestMethod -Uri "$baseUrl/reflect" -Method Post -ContentType "application/json" -Headers $headers -Body $body
    Write-Host "Tone: $($json.emotional_tone)"
    Write-Host "Risk Level: $($json.risk_level)"
    Write-Host "Confidence: $($json.multimodal_confidence)"
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

    $json = Invoke-RestMethod -Uri "$baseUrl/interact" -Method Post -ContentType "application/json" -Headers $headers -Body $body
    Write-Host "Tone: $($json.emotional_tone)"
    Write-Host "Risk Level: $($json.risk_level)"
    Write-Host "Dharma Score: $($json.dharma_score)"
    Write-Host "Session: $($json.session_id)"
} catch {
    Write-Host "Interact request failed: $_"
}

Write-Host "`n========== CLEANUP =========="
Write-Host "Stopping server PID: $serverId"
Stop-Process -Id $serverId -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Write-Host "Server stopped"

Write-Host "`n========== TEST COMPLETE =========="
