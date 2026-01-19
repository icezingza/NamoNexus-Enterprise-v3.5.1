@echo off
title NamoNexus Supreme Server (v3.5.1)
color 0A

echo ===================================================
echo   NamoNexus Enterprise - Sovereign AI Infrastructure
echo   Commander: P'Ice | Status: SYSTEM IGNITION
echo ===================================================
echo.

:: 1. Activate Environment (ปลุกงู Python)
call .venv\Scripts\activate

:: 2. Check Identity Capsule (เช็คดวงจิต)
if exist "core\identity\crisis_patterns.json" (
    echo [CHECK] Identity Capsule ..... OK (Awakened)
) else (
    echo [CHECK] Identity Capsule ..... MISSING (Running in Void Mode)
)

:: 3. Check Sixth Sense (เช็คหูทิพย์/ตาทิพย์)
echo [CHECK] Sixth Sense Engine ... ACTIVE (Golden Ratio Fusion)

echo.
echo ---------------------------------------------------
echo  Server is starting... (Press Ctrl+C to stop)
echo  Dashboard: http://localhost:8000/docs
echo ---------------------------------------------------
echo.

:: 4. Start Server (เดินเครื่องเต็มสูบ)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause