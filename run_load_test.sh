#!/bin/bash

# Script to run Load Tests automatically
# 1. Starts the API server
# 2. Runs Locust headless
# 3. Stops the API server

echo "🚀 Starting API Server for Load Testing..."
# Start uvicorn in background
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning &
API_PID=$!

# Wait for API to be ready
echo "⏳ Waiting for API to initialize (5s)..."
sleep 5

echo "🦗 Running Locust Load Test (Users: 50, Rate: 5/s, Duration: 30s)..."
# Run Locust
locust -f namonexus-360-testing/06-load-tests/locustfile.py \
    --headless \
    -u 50 -r 5 \
    --run-time 30s \
    --host http://localhost:8000 \
    --csv=load_test_results

echo "🛑 Stopping API Server..."
kill $API_PID
echo "✅ Load Test Completed. Results saved to load_test_results_stats.csv"

# Visualization step
echo "📊 Generating visualization graphs..."
if ! python3 -c "import pandas, matplotlib" 2>/dev/null; then
    echo "📦 Installing visualization dependencies..."
    pip install pandas matplotlib
fi
python3 visualize_load_test.py load_test_results