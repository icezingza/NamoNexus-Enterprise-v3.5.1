import os

import pytest

from fastapi.testclient import TestClient

from src.i18n import load_locale

TOKEN = os.getenv("NAMO_NEXUS_TOKEN")
if not TOKEN:
    pytest.skip("NAMO_NEXUS_TOKEN must be set for API tests.", allow_module_level=True)

from main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"}
LOCALE = load_locale("th")


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_interact_tier_0():
    response = client.post(
        "/interact",
        json={
            "message": LOCALE["tests"]["messages"]["main_calm"],
            "user_id": "test_001",
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    payload = response.json()
    assert "response" in payload
    assert "risk_level" in payload
    assert "session_id" in payload
    assert "human_handoff_required" in payload


def test_interact_tier_3_blocked():
    response = client.post(
        "/interact",
        json={
            "message": LOCALE["tests"]["messages"]["main_severe"],
            "user_id": "test_002",
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("risk_level") == "severe"
    assert payload.get("human_handoff_required") is True
