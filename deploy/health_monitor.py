import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.allowed_services import ensure_url_allowed

URL = "http://127.0.0.1:8000/health"
MAX_RETRIES = 5
SLEEP_SECONDS = 10
TIMEOUT_SECONDS = 5


def main() -> int:
    ensure_url_allowed(URL)
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(URL, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                print(f"Health check passed: {response.json()}")
                return 0
            print(f"Retry {attempt + 1}/{MAX_RETRIES} - status {response.status_code}")
        except Exception as exc:  # pragma: no cover - network exceptions during monitoring
            print(f"Retry {attempt + 1}/{MAX_RETRIES} - {exc}")
        time.sleep(SLEEP_SECONDS)

    print("Health check failed after 5 retries.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
