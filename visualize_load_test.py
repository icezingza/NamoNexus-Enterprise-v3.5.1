import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def visualize(prefix):
    # Locust generates _stats_history.csv for time-series data
    history_file = f"{prefix}_stats_history.csv"
    
    if not os.path.exists(history_file):
        print(f"❌ History file not found: {history_file}")
        print("   (Make sure Locust ran long enough to generate stats)")
        return

    print(f"📈 Reading data from {history_file}...")
    try:
        df = pd.read_csv(history_file)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

    if df.empty:
        print("⚠️ Dataframe is empty, skipping visualization.")
        return

    # Create a figure with 2 subplots (Throughput & Latency)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Plot 1: Requests per Second
    ax1.plot(df['Timestamp'], df['Requests/s'], label='RPS', color='blue')
    ax1.plot(df['Timestamp'], df['Failures/s'], label='Failures/s', color='red')
    ax1.set_title('Load Test: Throughput (Requests/s)')
    ax1.set_ylabel('Requests / Second')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Response Times (Percentiles)
    # Note: Column names depend on Locust version, usually "50%" and "95%" exist
    ax2.plot(df['Timestamp'], df['50%'], label='Median (50%)', color='green')
    ax2.plot(df['Timestamp'], df['95%'], label='95th Percentile', color='orange')
    ax2.set_title('Load Test: Latency (ms)')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Response Time (ms)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = "load_test_report.png"
    plt.savefig(output_file)
    print(f"✅ Visualization saved to {output_file}")

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "load_test_results"
    visualize(prefix)