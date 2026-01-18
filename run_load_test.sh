#!/bin/bash

# Script to run Load Tests automatically
# 1. Starts the API server
# 2. Runs Locust headless
# 3. Stops the API server

echo "🚀 Starting API Server for Load Testing..."
# Start uvicorn in background
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level warning &
API_PID=$!

# Ensure API server is killed when script exits (even if Ctrl+C)
trap "echo '🛑 Stopping API Server (PID: $API_PID)...'; kill $API_PID" EXIT

# Wait for API to be ready
echo "⏳ Waiting for API to initialize (5s)..."
sleep 5

echo "🦗 Running Locust Load Test (Users: 500, Rate: 50/s, Duration: 60s)..."
# Run Locust
locust -f locustfile.py \
    --headless \
    -u 500 -r 50 \
    --run-time 60s \
    --host http://localhost:8000 \
    --csv=load_test_results

echo "✅ Load Test Completed. Results saved to load_test_results_stats.csv"

# Visualization step
echo "📊 Generating visualization graphs..."
if ! python3 -c "import pandas, matplotlib" 2>/dev/null; then
    echo "📦 Installing visualization dependencies..."
    pip install pandas matplotlib
fi
python3 visualize_load_test.py load_test_results

echo "🧐 Analyzing results..."
python3 analyze_load_test.py load_test_results