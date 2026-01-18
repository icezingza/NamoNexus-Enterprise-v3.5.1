import os
import time
from datetime import datetime

import requests

from src.allowed_services import ensure_url_allowed
from src.i18n import load_locale

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = os.getenv("NAMO_NEXUS_TOKEN", "")
if not TOKEN:
    raise RuntimeError("NAMO_NEXUS_TOKEN is required for stress tests.")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
TRIAGE_URL = f"{BASE_URL}/triage"

LOCALE = load_locale("th")
PROMPTS = LOCALE["tests"]["stress"]["prompts"]
ALERT_KEYWORDS = LOCALE["tests"]["stress"]["alert_failure_keywords"]
TONE_VIOLATION_KEYWORDS = LOCALE["tests"]["stress"]["tone_violation_keywords"]


def run_stress_test():
    results = []
    ensure_url_allowed(TRIAGE_URL)
    print(f"Starting Stress Test with {len(PROMPTS)} prompts...")

    for i, message in enumerate(PROMPTS):
        payload = {
            "message": message,
            "user_id": f"test_user_{i}",
            "session_id": f"stress_session_{i}",
        }

        try:
            start_time = time.time()
            response = requests.post(
                TRIAGE_URL, json=payload, headers=HEADERS
            )
            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                results.append(
                    {
                        "prompt": message,
                        "risk_level": data["risk_level"],
                        "human_required": data["human_handoff_required"],
                        "ai_response": data["response"],
                        "latency": f"{latency:.2f}ms",
                        "status": "PASS",
                    }
                )
            else:
                results.append(
                    {
                        "prompt": message,
                        "status": f"FAIL ({response.status_code})",
                        "error": response.text,
                    }
                )
        except Exception as e:
            results.append({"prompt": message, "status": "ERROR", "error": str(e)})

        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/100...")

    # Analyze Results
    total = len(results)
    alert_failures = [
        r
        for r in results
        if r.get("status") == "PASS"
        and any(keyword in r["prompt"] for keyword in ALERT_KEYWORDS)
        and not r["human_required"]
    ]
    tone_checks = [
        r
        for r in results
        if r.get("status") == "PASS"
        and any(bad in r["ai_response"] for bad in TONE_VIOLATION_KEYWORDS)
    ]

    # Generate Report
    report_path = "triage_reliability_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Triage Reliability Report\n\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n")
        f.write(f"**Total Cases Tested:** {total}\n\n")

        f.write("## Summary Metrics\n")
        f.write("| Metric | Count | Percentage |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(
            f"| Successful Requests | {len([r for r in results if r['status'] == 'PASS'])} | {(len([r for r in results if r['status'] == 'PASS']) / total) * 100:.1f}% |\n"
        )
        f.write(
            f"| Alert Failures (False Negatives) | {len(alert_failures)} | {(len(alert_failures) / total) * 100:.1f}% |\n"
        )
        f.write(
            f"| Tone Violations (AI Insults) | {len(tone_checks)} | {(len(tone_checks) / total) * 100:.1f}% |\n\n"
        )

        f.write("## Detailed Findings\n")

        if alert_failures:
            f.write("### Alert Failures\n")
            f.write(
                "Prompts containing 'die/kill' keywords but didn't trigger `human_handoff_required`:\n"
            )
            for r in alert_failures:
                f.write(f"- **Prompt:** {r['prompt']} (Risk: {r['risk_level']})\n")
            f.write("\n")

        if tone_checks:
            f.write("### Tone Violations\n")
            f.write("AI responses detected as inappropriate or lacking compassion:\n")
            for r in tone_checks:
                f.write(f"- **Prompt:** {r['prompt']}\n- **AI:** {r['ai_response']}\n")
            f.write("\n")
        else:
            f.write("### Tone Sanity Check\n")
            f.write(
                "No direct insults or daring responses detected in the test set.\n\n"
            )

        f.write("## Full Logs (First 10)\n")
        for r in results[:10]:
            f.write(f"**Prompt:** {r['prompt']}\n")
            if r["status"] == "PASS":
                f.write(
                    f"- Risk: {r['risk_level']}\n- Human Alert: {r['human_required']}\n- Response: {r['ai_response']}\n\n"
                )
            else:
                f.write(f"- Status: {r['status']}\n\n")

    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    run_stress_test()
