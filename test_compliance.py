import pytest
from fastapi.testclient import TestClient
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from main import app
from src.auth_utils import verify_token

async def mock_verify_token():
    return {"sub": "test_user"}
app.dependency_overrides[verify_token] = mock_verify_token

client = TestClient(app)

class TestCompliance:
    """Compliance and PII testing"""

    def test_pii_leakage_in_response(self):
        """Ensure sensitive PII is not echoed back unnecessarily or logged"""
        # Note: In a real scenario, we'd check logs. Here we check API response.
        phone_number = "081-234-5678"
        payload = {
            "user_id": "user_pii",
            "message": f"My phone is {phone_number}"
        }
        response = client.post("/triage", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # The response message usually contains a greeting and advice.
        # It should NOT echo the user's phone number back in the 'response' field.
        # (Unless it's a specific intent to confirm, but generally avoided in mental health triage)
        assert phone_number not in data["response"]
        
        # Check that we have a valid session ID (Audit trail requirement)
        assert "session_id" in data
        assert len(data["session_id"]) > 0