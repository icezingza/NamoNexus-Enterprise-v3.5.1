"""Minimal API tests for health and reflect endpoints."""
import os

from fastapi.testclient import TestClient

os.environ.setdefault("NAMO_NEXUS_TOKEN", "test-token")

from main import app


client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {os.environ['NAMO_NEXUS_TOKEN']}"}


def test_health_endpoint_returns_ok():
    # Use /healthz for liveness checks.
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("status"), str)
    assert payload["status"] == "alive"

def test_ready_endpoint_contains_metrics():
    response = client.get("/readyz")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") in {"ready", "degraded"}
    assert "db_ready" in payload
    assert "cache_ready" in payload


def test_reflect_endpoint_basic():
    response = client.post(
        "/reflect",
        json={"message": "รู้สึกสบายใจวันนี้", "user_id": "test_003"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    payload = response.json()
    assert "response" in payload
    assert "risk_level" in payload
    assert "session_id" in payload
    assert "human_handoff_required" in payload
