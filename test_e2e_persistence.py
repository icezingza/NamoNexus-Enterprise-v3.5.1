import pytest
from fastapi.testclient import TestClient
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Import main app and engine
from main import app, engine
from src.auth_utils import verify_token

# Mock authentication
async def mock_verify_token():
    return {"sub": "e2e_tester"}
app.dependency_overrides[verify_token] = mock_verify_token

client = TestClient(app)

class TestE2EPersistence:
    """End-to-End tests verifying data persistence via API"""

    def test_triage_saves_to_database(self):
        """
        Verify that a call to /triage actually creates a record in the database.
        This confirms that the 'GridIntelligence' integration in main.py is active.
        """
        # 1. Send a triage request
        test_message = f"E2E Persistence Test {time.time()}"
        payload = {
            "user_id": "e2e_user",
            "message": test_message
        }
        
        response = client.post("/triage", json=payload)
        assert response.status_code == 200
        data = response.json()
        session_id = data["session_id"]
        
        # 2. Verify response structure
        assert "response" in data
        assert data["human_handoff_required"] is False
        
        # 3. Check Database directly using the engine instance
        # Note: In TestClient, background tasks run synchronously, so data should be there.
        history = engine.grid.get_session_history(session_id)
        
        assert len(history) > 0, "Database should contain the session record"
        assert history[0]["message"] == test_message, "Stored message should match input"
        assert history[0]["risk"] is not None