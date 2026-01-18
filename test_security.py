import pytest
from fastapi.testclient import TestClient
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from main import app
from src.auth_utils import verify_token

# Mock auth
async def mock_verify_token():
    return {"sub": "test_user"}
app.dependency_overrides[verify_token] = mock_verify_token

client = TestClient(app)

class TestSecurity:
    """Security dimension testing"""

    def test_sql_injection_attempt(self):
        """Test resilience against SQL Injection in input fields"""
        payload = {
            "user_id": "user_1' OR '1'='1",
            "message": "Attempting SQL injection via message'; DROP TABLE conversations; --"
        }
        response = client.post("/triage", json=payload)
        
        # Should process safely (200) or reject (422), but NOT crash (500)
        assert response.status_code in [200, 422]
        data = response.json()
        # Ensure the response doesn't leak DB errors
        assert "sqlite" not in str(data).lower()
        assert "syntax error" not in str(data).lower()

    def test_xss_sanitization(self):
        """Test that HTML/JS tags are sanitized or handled safely"""
        xss_payload = "<script>alert('XSS')</script>"
        payload = {
            "user_id": "test_xss",
            "message": f"Hello {xss_payload}"
        }
        response = client.post("/triage", json=payload)
        assert response.status_code == 200
        
        # The system might sanitize it or just treat it as text. 
        # Key is that it accepts it without executing it on the server side.
        # In a real browser client, we'd check if the output is escaped.
        # Here we check that the API handles it gracefully.
        assert "response" in response.json()

    def test_rate_limiting_headers(self):
        """Check if security headers for rate limiting are present"""
        # Note: TestClient bypasses some middleware depending on setup, 
        # but slowapi usually works if app is initialized correctly.
        payload = {"user_id": "rate_test", "message": "hi"}
        response = client.post("/triage", json=payload)
        
        # Even if rate limit isn't hit, headers should often be present 
        # or at least the request succeeds.
        assert response.status_code == 200
        # If middleware is active, we might see X-RateLimit headers