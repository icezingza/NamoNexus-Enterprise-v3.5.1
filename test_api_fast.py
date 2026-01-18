import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from main import app
from src.auth_utils import verify_token

# Mock authentication to bypass token check for tests
async def mock_verify_token():
    return {"sub": "test_user"}

# Override the dependency
app.dependency_overrides[verify_token] = mock_verify_token

client = TestClient(app)

class TestNamoAPI:
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["system"] == "NamoNexus Enterprise"
        assert data["status"] == "operational"

    def test_triage_endpoint_basic(self):
        """Test basic triage functionality"""
        payload = {
            "user_id": "test_user_1",
            "message": "I am feeling a bit anxious about work."
        }
        response = client.post("/triage", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "risk_level" in data
        assert "dharma_score" in data
        assert data["human_handoff_required"] is False

    def test_triage_severe_risk(self):
        """Test severe risk detection via API"""
        payload = {
            "user_id": "test_user_2",
            "message": "I want to end it all right now."
        }
        response = client.post("/triage", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["risk_level"] == "severe"
        assert data["human_handoff_required"] is True

    def test_input_validation(self):
        """Test API validation for missing fields"""
        payload = {
            "message": "Test without user_id"
        }
        response = client.post("/triage", json=payload)
        assert response.status_code == 422  # Unprocessable Entity