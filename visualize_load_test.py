import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def visualize(csv_prefix="load_test_results"):
    history_file = f"{csv_prefix}_stats_history.csv"
    
    if not os.path.exists(history_file):
        print(f"File {history_file} not found. Cannot generate graphs.")
        return

    print(f"Generating graphs from {history_file}...")
    try:
        df = pd.read_csv(history_file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Filter for Aggregated data if 'Name' column exists (standard Locust output)
    if 'Name' in df.columns:
        df = df[df['Name'] == 'Aggregated']
    
    if df.empty:
        print("No data found to visualize.")
        return

    # Create relative time column
    if 'Timestamp' in df.columns:
        df['Time'] = df['Timestamp'] - df['Timestamp'].iloc[0]
    else:
        df['Time'] = range(len(df))

    # Plot 1: Requests per Second (RPS)
    plt.figure(figsize=(10, 6))
    plt.plot(df['Time'], df['Requests/s'], label='Requests/s', color='blue')
    plt.plot(df['Time'], df['Failures/s'], label='Failures/s', color='red')
    plt.title('Load Test: Throughput (RPS)')
    plt.xlabel('Time (s)')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('load_test_rps.png')
    print("Saved load_test_rps.png")

    # Plot 2: Response Times
    plt.figure(figsize=(10, 6))
    plt.plot(df['Time'], df['50%'], label='Median', color='green')
    plt.plot(df['Time'], df['95%'], label='95th Percentile', color='orange')
    plt.plot(df['Time'], df['99%'], label='99th Percentile', color='purple', linestyle='--')
    plt.title('Load Test: Latency')
    plt.xlabel('Time (s)')
    plt.ylabel('Response Time (ms)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('load_test_latency.png')
    print("Saved load_test_latency.png")

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "load_test_results"
    visualize(prefix)
