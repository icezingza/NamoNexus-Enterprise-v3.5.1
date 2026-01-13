#!/bin/bash

echo "Starting Load Test..."

mkdir -p reports

# Start API in background
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

sleep 5  # Wait for startup

# Run Locust
echo "Running Locust (100 users, 5 minutes)..."
locust -f tests/performance/locust_test.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --csv=reports/load_test

# Generate report
echo "Load Test completed!"
ls -lh reports/load_test*

# Cleanup
kill $API_PID
