@echo off
REM Simple batch file to run load test on Windows

echo Starting API Server...
start uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning

timeout /t 10

echo Running Locust Load Test...
locust -f namonexus-360-testing/06-load-tests/locustfile.py --headless -u 50 -r 5 --run-time 30s --host http://localhost:8000 --csv=load_test_results

echo.
echo Load test completed!
echo Press any key to stop the API server...
pause >nul
taskkill /F /IM uvicorn.exe >nul 2>&1

echo Done!
