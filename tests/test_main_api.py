from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_interact_tier_0():
    response = client.post(
        "/interact",
        json={
            "message": "I feel calm today",
            "user_id": "test_001",
        },
    )
    assert response.status_code == 200
    assert "reflection_text" in response.json()


def test_interact_tier_3_blocked():
    response = client.post(
        "/interact",
        json={
            "message": "I want to kill myself",
            "user_id": "test_002",
        },
    )
    assert response.status_code == 200
    assert response.json().get("status") == "ESCALATION_QUEUED"
