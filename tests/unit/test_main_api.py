from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz_liveness(self, client: TestClient):
        """Test /healthz responds quickly."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_readyz_readiness(self, client: TestClient):
        """Test /readyz shows component status."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in {"ready", "degraded"}
        assert "db_ready" in data
        assert "cache_ready" in data

    def test_health_legacy(self, client: TestClient):
        """Test legacy /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("status") == "operational"
        assert "version" in payload


class TestMetricsEndpoint:
    """Test /metrics endpoint."""

    def test_metrics_json_default(self, client: TestClient):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        assert response.text

    def test_metrics_plaintext(self, client: TestClient):
        response = client.get("/metrics", headers={"accept": "text/plain"})
        assert response.status_code == 200
        assert response.text


class TestInteractEndpoint:
    """Test /interact endpoint."""

    def test_interact_basic(self, client: TestClient, sample_user_message, auth_headers):
        """Test basic interaction."""
        response = client.post("/interact", json=sample_user_message, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "risk_level" in data
        assert "session_id" in data

    def test_interact_missing_message(self, client: TestClient, auth_headers):
        """Test interact with missing message."""
        response = client.post("/interact", json={"user_id": "test"}, headers=auth_headers)
        assert response.status_code == 422

    def test_interact_empty_message(self, client: TestClient, auth_headers):
        """Test interact with empty message."""
        response = client.post(
            "/interact",
            json={
                "message": "",
                "user_id": "test",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_interact_long_message(self, client: TestClient, auth_headers):
        """Test interact with very long message."""
        long_msg = "A" * 10000
        response = client.post(
            "/interact",
            json={
                "message": long_msg,
                "user_id": "test",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestReflectEndpoint:
    """Test /reflect endpoint."""

    def test_reflect_basic(self, client: TestClient, sample_reflect_request, auth_headers):
        """Test basic reflect."""
        response = client.post("/reflect", json=sample_reflect_request, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "risk_level" in data


class TestHarmonicConsole:
    """Test /harmonic-console endpoint."""

    def test_harmonic_console(self, client: TestClient, auth_headers):
        response = client.get("/harmonic-console", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "recent_sessions" in data
        assert "active_alerts" in data
