"""Helper to deploy NamoNexus Enterprise to Cloud Run via gcloud."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.allowed_services import ensure_service_allowed


def deploy(project_id: str, region: str, service_name: str = "namo-nexus") -> None:
    ensure_service_allowed("gcp")
    image = f"gcr.io/{project_id}/{service_name}"
    subprocess.run(["gcloud", "builds", "submit", "--tag", image, str(ROOT)], check=True)
    subprocess.run(
        [
            "gcloud",
            "run",
            "deploy",
            service_name,
            "--image",
            image,
            "--platform",
            "managed",
            "--region",
            region,
            "--port",
            "8080",
            "--cpu",
            "1",
            "--memory",
            "1Gi",
            "--allow-unauthenticated",
        ],
        check=True,
    )


if __name__ == "__main__":
    print("Invoke deploy(project_id, region) to deploy NamoNexus Enterprise.")
