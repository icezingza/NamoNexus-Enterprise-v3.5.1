import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from main import app
from src.auth_utils import verify_token

async def mock_verify_token():
    return {"sub": "test_user"}
app.dependency_overrides[verify_token] = mock_verify_token

client = TestClient(app)

class TestFailover:
    """Failover and Robustness testing"""

    def test_malformed_json_input(self):
        """Test API resilience against bad input types"""
        # Sending list instead of dict for voice_features
        payload = {
            "user_id": "fail_test",
            "message": "test",
            "voice_features": [] # Should be dict
        }
        response = client.post("/triage", json=payload)
        # FastAPI validation should catch this (422) without crashing (500)
        assert response.status_code == 422

    def test_empty_message_handling(self):
        """Test handling of empty messages"""
        payload = {
            "user_id": "fail_test",
            "message": "" # Empty string
        }
        response = client.post("/triage", json=payload)
        # Should be 422 (validation error) or handled gracefully
        assert response.status_code == 422

    def test_health_check_recovery(self):
        """Ensure health check always returns 200 even under load/test"""
        response = client.get("/health")
        assert response.status_code == 200