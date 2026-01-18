import pandas as pd
import sys
import os

def analyze(prefix):
    stats_file = f"{prefix}_stats.csv"
    
    if not os.path.exists(stats_file):
        print(f"❌ Stats file not found: {stats_file}")
        return

    print(f"\n📊 Analyzing Load Test Results: {stats_file}")
    try:
        df = pd.read_csv(stats_file)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

    # Locust usually has an 'Aggregated' row or 'Total' row at the end
    total_row = df[df['Name'] == 'Aggregated']
    if total_row.empty:
        total_row = df[df['Name'] == 'Total']
    if total_row.empty:
        # Fallback: take the last row
        total_row = df.iloc[-1:]
    
    if total_row.empty:
        print("❌ No data found in stats file.")
        return

    # Extract metrics
    req_count = total_row['Request Count'].values[0]
    fail_count = total_row['Failure Count'].values[0]
    rps = total_row['Requests/s'].values[0]
    
    # Latency (ms) - Column names might vary slightly by Locust version
    p50 = total_row['50%'].values[0] if '50%' in total_row else 0
    p95 = total_row['95%'].values[0] if '95%' in total_row else 0
    p99 = total_row['99%'].values[0] if '99%' in total_row else 0
    
    error_rate = (fail_count / req_count) * 100 if req_count > 0 else 0
    
    print("\n--- 🏁 Load Test Summary ---")
    print(f"Total Requests: {req_count}")
    print(f"Total Failures: {fail_count}")
    print(f"Error Rate:     {error_rate:.2f}%")
    print(f"Throughput:     {rps:.2f} req/s")
    print(f"Latency (P95):  {p95:.2f} ms")
    print("----------------------------")

    # Evaluation Logic (Standard Web API Thresholds)
    status = "✅ PASSED"
    reasons = []

    if error_rate > 1.0:
        status = "❌ FAILED"
        reasons.append(f"Error rate too high ({error_rate:.2f}% > 1.0%)")
    
    if p95 > 2000: # 2 seconds
        status = "⚠️ WARNING (Slow)" if status == "✅ PASSED" else status
        reasons.append(f"High Latency P95 ({p95:.2f}ms > 2000ms)")

    print(f"Final Verdict: {status}")
    for r in reasons:
        print(f" - {r}")

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "load_test_results"
    analyze(prefix)