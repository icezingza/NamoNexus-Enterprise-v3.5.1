from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.allowed_services import ensure_url_allowed

SECONDS_PER_YEAR = 365 * 24 * 60 * 60

SAMPLE_PAYLOADS = [
    {"text": "I feel calm and open today."},
    {"text": "I want to help and support others."},
    {"text": "I am stressed about work but safe."},
    {"text": "I want to end it all."},
    {"text": "I am feeling happy today."},
]


def _parse_label(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in {"critical", "true", "yes", "1"}
    return False


def load_triage_data(path: str) -> Tuple[List[Dict[str, Any]], str]:
    if path and os.path.exists(path):
        items: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                text = str(payload.get("text", "")).strip()
                if not text:
                    continue
                label = payload.get("label", payload.get("is_critical"))
                items.append({"text": text, "label": _parse_label(label)})
        return items, path

    default_path = os.path.join("data", "triage_eval.jsonl")
    if os.path.exists(default_path):
        return load_triage_data(default_path)

    # Fallback minimal dataset if no file is present.
    fallback = [
        {"text": "I want to kill myself.", "label": True},
        {"text": "I want to end it all.", "label": True},
        {"text": "I am feeling happy today.", "label": False},
        {"text": "I want to help my friend.", "label": False},
    ]
    return fallback, "inline_default"


def percentiles(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"avg_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0}
    values_sorted = sorted(values)
    n = len(values_sorted)

    def pick(p: float) -> float:
        if n == 1:
            return values_sorted[0]
        index = (n - 1) * p
        lower = int(index)
        upper = min(lower + 1, n - 1)
        weight = index - lower
        return values_sorted[lower] + (values_sorted[upper] - values_sorted[lower]) * weight

    avg = sum(values_sorted) / n
    return {
        "avg_ms": round(avg * 1000, 2),
        "p50_ms": round(pick(0.5) * 1000, 2),
        "p95_ms": round(pick(0.95) * 1000, 2),
        "p99_ms": round(pick(0.99) * 1000, 2),
    }


def run_request(url: str, payload: Dict[str, Any], timeout: float) -> Tuple[float, int, Dict[str, Any], str]:
    start = time.perf_counter()
    try:
        ensure_url_allowed(url)
        response = requests.post(url, json=payload, timeout=timeout)
        duration = time.perf_counter() - start
        try:
            data = response.json()
        except ValueError:
            data = {}
        return duration, response.status_code, data, ""
    except Exception as exc:
        duration = time.perf_counter() - start
        return duration, 0, {}, str(exc)


def run_load_test(
    url: str,
    payloads: List[Dict[str, Any]],
    requests_total: int,
    concurrency: int,
    timeout: float,
) -> Dict[str, Any]:
    durations: List[float] = []
    status_codes: List[int] = []
    responses: List[Dict[str, Any]] = []
    errors: List[str] = []

    start_total = time.perf_counter()

    def task(payload: Dict[str, Any]) -> Tuple[float, int, Dict[str, Any], str]:
        return run_request(url, payload, timeout)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(task, payloads[i % len(payloads)]) for i in range(requests_total)
        ]
        for future in as_completed(futures):
            duration, status, data, error = future.result()
            durations.append(duration)
            status_codes.append(status)
            if data:
                responses.append(data)
            if error:
                errors.append(error)

    elapsed_total = time.perf_counter() - start_total
    return {
        "durations": durations,
        "status_codes": status_codes,
        "responses": responses,
        "errors": errors,
        "elapsed_total": elapsed_total,
    }


def evaluate_triage(
    url: str,
    dataset: List[Dict[str, Any]],
    threshold: float,
    timeout: float,
) -> Dict[str, Any]:
    tp = fp = tn = fn = 0
    durations: List[float] = []
    errors: List[str] = []
    ethical_scores: List[float] = []
    decision_consistency: List[float] = []

    for item in dataset:
        payload = {"text": item["text"]}
        duration, status, data, error = run_request(url, payload, timeout)
        durations.append(duration)
        if error or status != 200:
            errors.append(error or f"status:{status}")
            continue

        risk_score = data.get("risk_score")
        predicted = False
        if isinstance(risk_score, (int, float)):
            predicted = float(risk_score) >= threshold

        expected = bool(item.get("label"))
        if expected and predicted:
            tp += 1
        elif expected and not predicted:
            fn += 1
        elif not expected and predicted:
            fp += 1
        else:
            tn += 1

        ethical = data.get("ethical_score")
        if isinstance(ethical, (int, float)):
            ethical_scores.append(float(ethical))
        consistency = data.get("decision_consistency")
        if isinstance(consistency, (int, float)):
            decision_consistency.append(float(consistency))

    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0

    return {
        "counts": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "sensitivity": round(sensitivity, 4),
        "specificity": round(specificity, 4),
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "latency": percentiles(durations),
        "errors": errors,
        "ethical_scores": ethical_scores,
        "decision_consistency": decision_consistency,
    }


def start_server(host: str, port: int) -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.main:app",
        "--host",
        host,
        "--port",
        str(port),
        "--log-level",
        "warning",
    ]
    return subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_for_server(base_url: str, timeout: float) -> bool:
    deadline = time.time() + timeout
    health_url = f"{base_url}/healthz"
    while time.time() < deadline:
        try:
            ensure_url_allowed(health_url)
            response = requests.get(health_url, timeout=1.0)
            if response.status_code == 200:
                return True
        except Exception:
            time.sleep(0.2)
    return False


def stop_server(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def render_markdown(report: Dict[str, Any]) -> str:
    latency = report["response_latency"]
    doc = report["documentation_time_reduction"]
    triage = report["triage_evaluation"]
    ethical = report["ethical_alignment"]
    capacity = report["capacity_estimate"]
    assumptions = report["assumptions"]

    lines = [
        "# Metrics Report",
        "",
        f"Run timestamp: {report['run']['timestamp']}",
        f"Base URL: {report['run']['base_url']}",
        f"Endpoint: {report['run']['endpoint']}",
        f"Requests: {report['run']['requests_total']} | Concurrency: {report['run']['concurrency']}",
        "",
        "## Response Latency",
        f"- avg_ms: {latency['avg_ms']}",
        f"- p50_ms: {latency['p50_ms']}",
        f"- p95_ms: {latency['p95_ms']}",
        f"- p99_ms: {latency['p99_ms']}",
        f"- rps: {latency['rps']}",
        "",
        "## Documentation Time Reduction",
        f"- baseline_minutes: {doc['baseline_minutes']}",
        f"- ai_p50_seconds: {doc['ai_p50_seconds']}",
        f"- reduction_percent: {doc['reduction_percent']}",
        f"- time_saved_minutes: {doc['time_saved_minutes']}",
        "",
        "## Triage Evaluation",
        f"- dataset: {triage['dataset_source']}",
        f"- samples: {triage['samples']}",
        f"- threshold: {triage['threshold']}",
        f"- sensitivity: {triage['sensitivity']}",
        f"- specificity: {triage['specificity']}",
        f"- accuracy: {triage['accuracy']}",
        f"- precision: {triage['precision']}",
        f"- counts: {triage['counts']}",
        "",
        "## Ethical Alignment",
        f"- mean_ethical_score: {ethical['mean_ethical_score']}",
        f"- mean_decision_consistency: {ethical['mean_decision_consistency']}",
        "",
        "## Capacity Estimate",
        f"- rps: {capacity['rps']}",
        f"- calls_per_year: {capacity['calls_per_year']}",
        f"- baseline_capacity_per_year: {capacity['baseline_capacity_per_year']}",
        f"- improvement_factor: {capacity['improvement_factor']}",
        "",
        "## Slide Table (Measured + Baseline)",
        "",
        "| Metric | Baseline | NamoNexus (Measured) | Improvement |",
        "| --- | --- | --- | --- |",
        (
            f"| Triage speed | {assumptions['baseline_triage_minutes']} min | "
            f"{doc['ai_p50_seconds']} s | {doc['improvement_factor']}x |"
        ),
        (
            f"| Capacity (calls/year) | {capacity['baseline_capacity_per_year']} | "
            f"{capacity['calls_per_year']} | {capacity['improvement_factor']}x |"
        ),
        (
            f"| Sensitivity | {assumptions['baseline_sensitivity']} | "
            f"{triage['sensitivity']} | n/a |"
        ),
        (
            f"| Ethical alignment | {assumptions['baseline_ethical_score']} | "
            f"{ethical['mean_ethical_score']} | n/a |"
        ),
        "",
        "Notes:",
        f"- Dataset source for triage: {triage['dataset_source']}",
        f"- Baselines are inputs; change them when you have official values.",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run real metrics against the API.")
    parser.add_argument("--base-url", default="", help="Target base URL (skip to spawn locally).")
    parser.add_argument("--host", default="127.0.0.1", help="Host for local server.")
    parser.add_argument("--port", type=int, default=8899, help="Port for local server.")
    parser.add_argument("--endpoint", default="/reflect", help="Endpoint to benchmark.")
    parser.add_argument("--requests", type=int, default=200, help="Number of requests to send.")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent workers.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout.")
    parser.add_argument("--triage-data", default="", help="Path to triage eval JSONL.")
    parser.add_argument("--threshold", type=float, default=0.75, help="Critical threshold.")
    parser.add_argument("--manual-doc-minutes", type=float, default=12.0, help="Manual doc time baseline.")
    parser.add_argument("--baseline-capacity", type=int, default=100000, help="Baseline capacity per year.")
    parser.add_argument("--baseline-sensitivity", default="n/a", help="Baseline sensitivity.")
    parser.add_argument("--baseline-ethical-score", default="n/a", help="Baseline ethical score.")
    parser.add_argument("--report-dir", default="reports", help="Report output directory.")
    args = parser.parse_args()

    base_url = args.base_url.strip()
    spawned = None
    if not base_url:
        base_url = f"http://{args.host}:{args.port}"
        spawned = start_server(args.host, args.port)
        if not wait_for_server(base_url, 20.0):
            stop_server(spawned)
            raise RuntimeError("Failed to start local server.")

    endpoint_url = f"{base_url}{args.endpoint}"

    load_results = run_load_test(
        endpoint_url,
        SAMPLE_PAYLOADS,
        args.requests,
        args.concurrency,
        args.timeout,
    )

    latency_stats = percentiles(load_results["durations"])
    rps = (len(load_results["durations"]) / load_results["elapsed_total"]) if load_results["elapsed_total"] else 0.0

    ai_p50_seconds = latency_stats["p50_ms"] / 1000
    baseline_seconds = args.manual_doc_minutes * 60.0
    reduction = 1.0 - (ai_p50_seconds / baseline_seconds) if baseline_seconds else 0.0
    reduction_percent = round(max(0.0, reduction) * 100, 2)
    time_saved_minutes = round(args.manual_doc_minutes - (ai_p50_seconds / 60.0), 4)

    triage_data, dataset_source = load_triage_data(args.triage_data)
    triage_results = evaluate_triage(endpoint_url, triage_data, args.threshold, args.timeout)

    ethical_scores = [
        score
        for score in triage_results["ethical_scores"]
        if isinstance(score, (int, float))
    ]
    decision_scores = [
        score
        for score in triage_results["decision_consistency"]
        if isinstance(score, (int, float))
    ]

    ethical_mean = round(sum(ethical_scores) / len(ethical_scores), 4) if ethical_scores else 0.0
    decision_mean = round(sum(decision_scores) / len(decision_scores), 4) if decision_scores else 0.0

    calls_per_year = round(rps * SECONDS_PER_YEAR)
    improvement_factor = round((calls_per_year / args.baseline_capacity) if args.baseline_capacity else 0.0, 2)

    report = {
        "run": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "base_url": base_url,
            "endpoint": args.endpoint,
            "requests_total": args.requests,
            "concurrency": args.concurrency,
            "timeout": args.timeout,
        },
        "response_latency": {
            **latency_stats,
            "rps": round(rps, 4),
            "total_requests": len(load_results["durations"]),
            "errors": len(load_results["errors"]),
            "elapsed_total": round(load_results["elapsed_total"], 4),
        },
        "documentation_time_reduction": {
            "baseline_minutes": args.manual_doc_minutes,
            "ai_p50_seconds": round(ai_p50_seconds, 4),
            "reduction_percent": reduction_percent,
            "time_saved_minutes": time_saved_minutes,
            "improvement_factor": round((args.manual_doc_minutes * 60.0) / ai_p50_seconds, 2)
            if ai_p50_seconds
            else 0.0,
        },
        "triage_evaluation": {
            "dataset_source": dataset_source,
            "samples": len(triage_data),
            "threshold": args.threshold,
            "sensitivity": triage_results["sensitivity"],
            "specificity": triage_results["specificity"],
            "accuracy": triage_results["accuracy"],
            "precision": triage_results["precision"],
            "counts": triage_results["counts"],
            "errors": len(triage_results["errors"]),
        },
        "ethical_alignment": {
            "mean_ethical_score": ethical_mean,
            "mean_decision_consistency": decision_mean,
        },
        "capacity_estimate": {
            "rps": round(rps, 4),
            "calls_per_year": calls_per_year,
            "baseline_capacity_per_year": args.baseline_capacity,
            "improvement_factor": improvement_factor,
        },
        "assumptions": {
            "baseline_triage_minutes": args.manual_doc_minutes,
            "baseline_capacity_per_year": args.baseline_capacity,
            "baseline_sensitivity": args.baseline_sensitivity,
            "baseline_ethical_score": args.baseline_ethical_score,
        },
    }

    os.makedirs(args.report_dir, exist_ok=True)
    json_path = os.path.join(args.report_dir, "metrics_report.json")
    md_path = os.path.join(args.report_dir, "metrics_report.md")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write(render_markdown(report))

    if spawned:
        stop_server(spawned)

    print(f"Report written to {json_path} and {md_path}")


if __name__ == "__main__":
    main()
