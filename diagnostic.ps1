$ErrorActionPreference = "Continue"

Write-Output "========== DIAGNOSTIC REPORT =========="
Write-Output ""

Write-Output "1) Check Python & Dependencies"
python --version
python -c "import fastapi; print('FastAPI: ' + fastapi.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy: ' + sqlalchemy.__version__)"
python -c "import pydantic; print('Pydantic: ' + pydantic.__version__)"
Write-Output ""

Write-Output "2) Check Port Status"
$netstat = netstat -ano | Select-String ":8000"
if ($netstat) {
    $netstat | ForEach-Object { $_.Line }
} else {
    Write-Output "Port 8000: FREE"
}
Write-Output ""

Write-Output "3) Check Database"
if (Test-Path "namonexus.db") {
    Write-Output "Database file exists"
} else {
    Write-Output "Database file NOT found"
}
$dbCode = @'
import sqlite3
db = 'namonexus.db'
conn = sqlite3.connect(db)
tables = [row[0] for row in conn.execute('SELECT name FROM sqlite_master WHERE type=\'table\' ORDER BY name;').fetchall()]
conn.close()
print('Tables: ' + (', '.join(tables) if tables else 'NONE'))
'@
python -c "$dbCode"
Write-Output ""

Write-Output "4) Check Alembic"
$alembicOutput = cmd /c "alembic current 2>&1"
$alembicOutput
if ($LASTEXITCODE -eq 0) {
    Write-Output "Alembic: OK"
} else {
    Write-Output "Alembic: ERROR"
}
Write-Output ""

Write-Output "5) Import Main Module (Test)"
$importOutput = & python -c "from src.main import app; print('Import successful')" 2>&1
$importOutput
if ($LASTEXITCODE -eq 0) {
    Write-Output "Import: OK"
} else {
    Write-Output "Import: FAILED"
}
Write-Output ""

Write-Output "6) Start Server (5 sec timeout)"
$logFile = Join-Path (Get-Location) "diagnostic_server.log"
$errFile = Join-Path (Get-Location) "diagnostic_server.err"
if (Test-Path $logFile) {
    Remove-Item $logFile -Force
}
if (Test-Path $errFile) {
    Remove-Item $errFile -Force
}
$proc = Start-Process -FilePath "python" -ArgumentList "src/main.py" -RedirectStandardOutput $logFile -RedirectStandardError $errFile -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5
if (Test-Path $logFile) {
    Get-Content $logFile -TotalCount 200
} else {
    Write-Output "No output captured"
}
if (Test-Path $errFile) {
    Get-Content $errFile -TotalCount 200
}
if ($proc.HasExited) {
    Write-Output "Server exited early with code $($proc.ExitCode)"
} else {
    Write-Output "Server process started: $($proc.Id)"
    Stop-Process -Id $proc.Id -Force
    Write-Output "Server process stopped"
}
Write-Output ""

Write-Output "7) Check if port is listening (after startup)"
$netstatAfter = netstat -ano | Select-String ":8000"
if ($netstatAfter) {
    $netstatAfter | ForEach-Object { $_.Line }
} else {
    Write-Output "Port 8000: NOT listening"
}
Write-Output ""

Write-Output "========== END DIAGNOSTIC =========="
