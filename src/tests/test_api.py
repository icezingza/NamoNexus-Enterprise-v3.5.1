from fastapi.testclient import TestClient

from src.i18n import load_locale


LOCALE = load_locale("th")


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_healthz_endpoint(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readyz_endpoint(client: TestClient):
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_interact_basic(client: TestClient):
    payload = {"user_id": "test_user_001", "message": LOCALE["tests"]["messages"]["api_greeting"]}
    response = client.post("/interact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tone" in data
    assert "risk_level" in data


def test_interact_missing_fields(client: TestClient):
    response = client.post("/interact", json={"user_id": "test_user"})
    assert response.status_code == 422


def test_reflect_endpoint(client: TestClient):
    payload = {"text": LOCALE["tests"]["messages"]["api_anxiety"], "user_id": "test_user_002"}
    response = client.post("/reflect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tone" in data


def test_reflect_high_risk_refusal(client: TestClient):
    payload = {"text": "I want to hurt myself", "user_id": "test_user_critical"}
    response = client.post("/reflect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_refusal"] is True
    response_text = data["response"].lower()
    assert "i hear" in response_text
    forbidden = ["call", "contact", "reach", "please", "try", "must", "should", "need", "stop"]
    assert all(token not in response_text for token in forbidden)
